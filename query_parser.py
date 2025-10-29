"""
query_parser.py - Parses natural language questions to extract entities and intent
"""

import re
import pandas as pd
from typing import Dict, List, Any, Optional


class QueryParser:
    """Parses natural language questions about rainfall data"""

    def __init__(self):
        self.intent_patterns = {
            'compare': ['compare', 'difference between', 'vs', 'versus'],
            'maximum': ['highest', 'maximum', 'max', 'most', 'greatest', 'largest'],
            'minimum': ['lowest', 'minimum', 'min', 'least', 'smallest'],
            'average': ['average', 'mean', 'avg'],
            'sum': ['total', 'sum', 'combined'],
            'trend': ['trend', 'pattern', 'over time', 'change'],
            'list': ['list', 'show', 'display', 'what are'],
            'count': ['how many', 'count', 'number of']
        }

        self.month_names = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
        ]

        self.season_names = ['monsoon', 'winter', 'summer', 'spring', 'autumn', 'fall']

    def parse(self, question: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Parse a natural language question

        Args:
            question: User's question
            df: DataFrame containing the data

        Returns:
            dict: Parsed query with extracted entities and intent
        """
        question_lower = question.lower()

        parsed = {
            'original_question': question,
            'intent': self._extract_intent(question_lower),
            'entities': self._extract_entities(question_lower, df),
            'years': self._extract_years(question_lower),
            'metrics': self._extract_metrics(question_lower, df),
            'filters': {}
        }

        # Build filters from extracted entities
        if parsed['entities'].get('states'):
            parsed['filters']['states'] = parsed['entities']['states']

        if parsed['years']:
            parsed['filters']['years'] = parsed['years']

        if parsed['entities'].get('months'):
            parsed['filters']['months'] = parsed['entities']['months']

        if parsed['entities'].get('seasons'):
            parsed['filters']['seasons'] = parsed['entities']['seasons']

        return parsed

    def _extract_intent(self, question: str) -> str:
        """
        Extract the primary intent from the question

        Args:
            question: Lowercased question

        Returns:
            str: Intent type
        """
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in question for pattern in patterns):
                return intent

        # Default intent
        return 'query'

    def _extract_entities(self, question: str, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Extract entities (states, months, seasons) from the question

        Args:
            question: Lowercased question
            df: DataFrame

        Returns:
            dict: Dictionary of entity types and values
        """
        entities = {
            'states': [],
            'months': [],
            'seasons': []
        }

        # Extract states/regions from data
        state_columns = self._find_columns_by_keywords(df, ['state', 'region', 'district', 'area', 'location'])
        if state_columns:
            state_col = state_columns[0]
            unique_states = df[state_col].dropna().unique()

            for state in unique_states:
                state_lower = str(state).lower()
                if state_lower in question:
                    entities['states'].append(state)

        # Extract months
        for month in self.month_names:
            if month in question:
                entities['months'].append(month)

        # Extract seasons
        for season in self.season_names:
            if season in question:
                entities['seasons'].append(season)

        return entities

    def _extract_years(self, question: str) -> List[int]:
        """
        Extract years from the question

        Args:
            question: Question text

        Returns:
            list: List of years mentioned
        """
        years = []

        # Find 4-digit years (1900-2100)
        year_matches = re.findall(r'\b(19\d{2}|20\d{2}|21\d{2})\b', question)
        years.extend([int(y) for y in year_matches])

        # Find year ranges (e.g., "2015-2020", "2015 to 2020")
        range_pattern = r'\b(19\d{2}|20\d{2}|21\d{2})\s*(?:to|-|–)\s*(19\d{2}|20\d{2}|21\d{2})\b'
        range_matches = re.findall(range_pattern, question)

        for start, end in range_matches:
            start_year, end_year = int(start), int(end)
            years.extend(range(start_year, end_year + 1))

        return sorted(list(set(years)))

    def _extract_metrics(self, question: str, df: pd.DataFrame) -> List[str]:
        """
        Extract metric columns mentioned in the question

        Args:
            question: Lowercased question
            df: DataFrame

        Returns:
            list: List of relevant metric column names
        """
        metrics = []

        # Common rainfall-related keywords
        rainfall_keywords = ['rainfall', 'rain', 'precipitation', 'mm', 'millimeter']
        temperature_keywords = ['temperature', 'temp', 'celsius', 'fahrenheit']

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        for col in numeric_cols:
            col_lower = col.lower()

            # Check if column name or related keywords are in question
            if col_lower in question:
                metrics.append(col)
            elif any(keyword in col_lower for keyword in rainfall_keywords):
                if any(keyword in question for keyword in rainfall_keywords):
                    metrics.append(col)
            elif any(keyword in col_lower for keyword in temperature_keywords):
                if any(keyword in question for keyword in temperature_keywords):
                    metrics.append(col)

        # If no specific metrics found, use all numeric columns as potential metrics
        if not metrics:
            metrics = numeric_cols

        return metrics

    def _find_columns_by_keywords(self, df: pd.DataFrame, keywords: List[str]) -> List[str]:
        """
        Find columns containing any of the keywords

        Args:
            df: DataFrame
            keywords: List of keywords to search for

        Returns:
            list: Matching column names
        """
        matching_cols = []

        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in keywords):
                matching_cols.append(col)

        return matching_cols