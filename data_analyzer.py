"""
data_analyzer.py - Executes queries on the data and returns results with citations
"""

import pandas as pd
from typing import Dict, Any, List, Optional


class DataAnalyzer:
    """Analyzes data based on parsed queries"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df.reset_index(drop=True, inplace=True)  # Reset index for row citations

    def execute_query(self, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the parsed query on the dataframe

        Args:
            parsed_query: Parsed query dictionary

        Returns:
            dict: Results with data and citations
        """
        intent = parsed_query['intent']
        filters = parsed_query.get('filters', {})
        metrics = parsed_query.get('metrics', [])

        # Apply filters
        filtered_df = self._apply_filters(filters)

        # Execute based on intent
        if intent == 'compare':
            results = self._compare_entities(filtered_df, filters, metrics)
        elif intent == 'maximum':
            results = self._find_maximum(filtered_df, metrics)
        elif intent == 'minimum':
            results = self._find_minimum(filtered_df, metrics)
        elif intent == 'average':
            results = self._calculate_average(filtered_df, metrics)
        elif intent == 'sum':
            results = self._calculate_sum(filtered_df, metrics)
        elif intent == 'trend':
            results = self._analyze_trend(filtered_df, metrics)
        elif intent == 'count':
            results = self._count_records(filtered_df)
        else:
            results = self._general_query(filtered_df, metrics)

        return results

    def _apply_filters(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filters to the dataframe

        Args:
            filters: Dictionary of filters

        Returns:
            pd.DataFrame: Filtered dataframe
        """
        df = self.df.copy()

        # Filter by states
        if 'states' in filters and filters['states']:
            state_cols = self._find_state_columns()
            if state_cols:
                state_col = state_cols[0]
                df = df[df[state_col].isin(filters['states'])]

        # Filter by years
        if 'years' in filters and filters['years']:
            year_cols = self._find_year_columns()
            if year_cols:
                year_col = year_cols[0]
                df = df[df[year_col].isin(filters['years'])]

        # Filter by months
        if 'months' in filters and filters['months']:
            month_cols = self._find_month_columns()
            if month_cols:
                month_col = month_cols[0]
                df = df[df[month_col].str.lower().isin([m.lower() for m in filters['months']])]

        return df

    def _compare_entities(self, df: pd.DataFrame, filters: Dict, metrics: List[str]) -> Dict[str, Any]:
        """Compare values between different entities"""
        results = {'type': 'comparison', 'data': [], 'citations': []}

        state_cols = self._find_state_columns()
        if not state_cols or not metrics:
            return results

        state_col = state_cols[0]
        metric = metrics[0] if metrics else None

        if not metric:
            return results

        # Group by state and aggregate
        if 'states' in filters and filters['states']:
            for state in filters['states']:
                state_data = df[df[state_col] == state]
                if len(state_data) > 0:
                    agg_value = state_data[metric].mean()

                    # Get citation from first matching row
                    row_idx = state_data.index[0]

                    results['data'].append({
                        'entity': state,
                        'metric': metric,
                        'value': agg_value,
                        'row_index': int(row_idx),
                        'count': len(state_data)
                    })

        return results

    def _find_maximum(self, df: pd.DataFrame, metrics: List[str]) -> Dict[str, Any]:
        """Find maximum value"""
        results = {'type': 'maximum', 'data': [], 'citations': []}

        if not metrics or len(df) == 0:
            return results

        metric = metrics[0]

        if metric not in df.columns:
            return results

        max_idx = df[metric].idxmax()
        max_value = df.loc[max_idx, metric]

        # Get identifying columns
        state_cols = self._find_state_columns()
        year_cols = self._find_year_columns()

        entity_info = {}
        if state_cols:
            entity_info['state'] = df.loc[max_idx, state_cols[0]]
        if year_cols:
            entity_info['year'] = df.loc[max_idx, year_cols[0]]

        results['data'].append({
            'metric': metric,
            'value': max_value,
            'row_index': int(max_idx),
            'entity_info': entity_info
        })

        return results

    def _find_minimum(self, df: pd.DataFrame, metrics: List[str]) -> Dict[str, Any]:
        """Find minimum value"""
        results = {'type': 'minimum', 'data': [], 'citations': []}

        if not metrics or len(df) == 0:
            return results

        metric = metrics[0]

        if metric not in df.columns:
            return results

        min_idx = df[metric].idxmin()
        min_value = df.loc[min_idx, metric]

        # Get identifying columns
        state_cols = self._find_state_columns()
        year_cols = self._find_year_columns()

        entity_info = {}
        if state_cols:
            entity_info['state'] = df.loc[min_idx, state_cols[0]]
        if year_cols:
            entity_info['year'] = df.loc[min_idx, year_cols[0]]

        results['data'].append({
            'metric': metric,
            'value': min_value,
            'row_index': int(min_idx),
            'entity_info': entity_info
        })

        return results

    def _calculate_average(self, df: pd.DataFrame, metrics: List[str]) -> Dict[str, Any]:
        """Calculate average"""
        results = {'type': 'average', 'data': [], 'citations': []}

        if not metrics or len(df) == 0:
            return results

        for metric in metrics:
            if metric in df.columns and pd.api.types.is_numeric_dtype(df[metric]):
                avg_value = df[metric].mean()

                results['data'].append({
                    'metric': metric,
                    'value': avg_value,
                    'count': len(df),
                    'row_indices': df.index.tolist()
                })

        return results

    def _calculate_sum(self, df: pd.DataFrame, metrics: List[str]) -> Dict[str, Any]:
        """Calculate sum"""
        results = {'type': 'sum', 'data': [], 'citations': []}

        if not metrics or len(df) == 0:
            return results

        for metric in metrics:
            if metric in df.columns and pd.api.types.is_numeric_dtype(df[metric]):
                sum_value = df[metric].sum()

                results['data'].append({
                    'metric': metric,
                    'value': sum_value,
                    'count': len(df),
                    'row_indices': df.index.tolist()
                })

        return results

    def _analyze_trend(self, df: pd.DataFrame, metrics: List[str]) -> Dict[str, Any]:
        """Analyze trend over time"""
        results = {'type': 'trend', 'data': [], 'citations': []}

        year_cols = self._find_year_columns()
        if not year_cols or not metrics or len(df) == 0:
            return results

        year_col = year_cols[0]
        metric = metrics[0]

        if metric not in df.columns:
            return results

        # Group by year
        trend_data = df.groupby(year_col)[metric].mean().reset_index()

        for _, row in trend_data.iterrows():
            year = row[year_col]
            value = row[metric]

            # Find original row index
            orig_rows = df[df[year_col] == year].index.tolist()

            results['data'].append({
                'year': int(year),
                'metric': metric,
                'value': value,
                'row_indices': orig_rows
            })

        return results

    def _count_records(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Count records"""
        results = {'type': 'count', 'data': [], 'citations': []}

        results['data'].append({
            'count': len(df),
            'row_indices': df.index.tolist()
        })

        return results

    def _general_query(self, df: pd.DataFrame, metrics: List[str]) -> Dict[str, Any]:
        """General query - return filtered data"""
        results = {'type': 'general', 'data': [], 'citations': []}

        if len(df) == 0:
            return results

        # Return summary statistics for relevant metrics
        for metric in metrics:
            if metric in df.columns and pd.api.types.is_numeric_dtype(df[metric]):
                results['data'].append({
                    'metric': metric,
                    'mean': df[metric].mean(),
                    'min': df[metric].min(),
                    'max': df[metric].max(),
                    'count': len(df),
                    'row_indices': df.index.tolist()
                })

        return results

    def _find_state_columns(self) -> List[str]:
        """Find state/region columns"""
        keywords = ['state', 'region', 'district', 'area', 'location']
        return [col for col in self.df.columns if any(k in col.lower() for k in keywords)]

    def _find_year_columns(self) -> List[str]:
        """Find year columns"""
        keywords = ['year', 'yr']
        return [col for col in self.df.columns if any(k in col.lower() for k in keywords)]

    def _find_month_columns(self) -> List[str]:
        """Find month columns"""
        keywords = ['month', 'mon']
        return [col for col in self.df.columns if any(k in col.lower() for k in keywords)]