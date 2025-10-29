"""
data_loader.py - Handles CSV loading and preprocessing
"""

import pandas as pd
import re
from typing import Optional


class DataLoader:
    """Loads and preprocesses rainfall CSV data"""

    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.original_columns: dict = {}

    def load_csv(self, file) -> pd.DataFrame:
        """
        Load CSV file and preprocess it

        Args:
            file: Uploaded file object (from Streamlit)

        Returns:
            pd.DataFrame: Preprocessed dataframe
        """
        # Read CSV
        df = pd.read_csv(file)

        # Store original column names for reference
        self.original_columns = {self._clean_column_name(col): col for col in df.columns}

        # Clean column names
        df.columns = [self._clean_column_name(col) for col in df.columns]

        # Remove completely empty rows and columns
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')

        # Detect and convert year columns
        df = self._detect_and_convert_years(df)

        # Detect and clean numeric columns
        df = self._clean_numeric_columns(df)

        # Store processed dataframe
        self.df = df

        return df

    def _clean_column_name(self, col_name: str) -> str:
        """
        Clean column name: lowercase, replace spaces with underscores

        Args:
            col_name: Original column name

        Returns:
            str: Cleaned column name
        """
        # Convert to string and lowercase
        cleaned = str(col_name).lower().strip()

        # Replace spaces and special characters with underscores
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        cleaned = re.sub(r'\s+', '_', cleaned)

        # Remove multiple consecutive underscores
        cleaned = re.sub(r'_+', '_', cleaned)

        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')

        return cleaned

    def _detect_and_convert_years(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect year columns and ensure they're integers

        Args:
            df: DataFrame to process

        Returns:
            pd.DataFrame: DataFrame with converted year columns
        """
        year_patterns = ['year', 'yr', 'years']

        for col in df.columns:
            # Check if column name suggests it's a year
            if any(pattern in col.lower() for pattern in year_patterns):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                except:
                    pass

            # Check if column contains year-like values (1900-2100)
            elif df[col].dtype == 'object':
                try:
                    # Try to convert and check if values look like years
                    temp = pd.to_numeric(df[col], errors='coerce')
                    if temp.notna().any():
                        if (temp.dropna() >= 1900).all() and (temp.dropna() <= 2100).all():
                            df[col] = temp.astype('Int64')
                except:
                    pass

        return df

    def _clean_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and convert numeric columns (rainfall, temperature, etc.)

        Args:
            df: DataFrame to process

        Returns:
            pd.DataFrame: DataFrame with cleaned numeric columns
        """
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Remove common non-numeric characters
                    cleaned = df[col].astype(str).str.replace(',', '')
                    cleaned = cleaned.str.replace('₹', '')
                    cleaned = cleaned.str.replace('$', '')
                    cleaned = cleaned.str.strip()

                    # Try to convert to numeric
                    numeric_values = pd.to_numeric(cleaned, errors='coerce')

                    # If most values are numeric, convert the column
                    if numeric_values.notna().sum() / len(df) > 0.5:
                        df[col] = numeric_values
                except:
                    pass

        return df

    def get_column_mapping(self) -> dict:
        """
        Get mapping of cleaned columns to original column names

        Returns:
            dict: Mapping dictionary
        """
        return self.original_columns

    def get_numeric_columns(self) -> list:
        """
        Get list of numeric columns

        Returns:
            list: List of numeric column names
        """
        if self.df is None:
            return []
        return self.df.select_dtypes(include=['number']).columns.tolist()

    def get_categorical_columns(self) -> list:
        """
        Get list of categorical (text) columns

        Returns:
            list: List of categorical column names
        """
        if self.df is None:
            return []
        return self.df.select_dtypes(include=['object']).columns.tolist()

    def get_unique_values(self, column: str) -> list:
        """
        Get unique values in a column

        Args:
            column: Column name

        Returns:
            list: List of unique values
        """
        if self.df is None or column not in self.df.columns:
            return []
        return self.df[column].dropna().unique().tolist()