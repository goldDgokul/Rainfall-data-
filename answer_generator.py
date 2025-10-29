"""
answer_generator.py - Generates natural language answers with citations
"""

import pandas as pd
from typing import Dict, Any, List, Optional


class AnswerGenerator:
    """Generates natural language answers with proper citations"""

    def __init__(self):
        pass

    def generate_answer(
            self,
            question: str,
            parsed_query: Dict[str, Any],
            results: Dict[str, Any],
            df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Generate natural language answer with citations

        Args:
            question: Original question
            parsed_query: Parsed query information
            results: Results from data analyzer
            df: Original dataframe

        Returns:
            dict: Answer and citations
        """
        result_type = results.get('type', 'general')
        data = results.get('data', [])

        if not data:
            return {
                'answer': "I couldn't find relevant data to answer this question. Please check if the data contains the required information.",
                'citations': []
            }

        # Generate answer based on result type
        if result_type == 'comparison':
            return self._generate_comparison_answer(question, data, df)
        elif result_type == 'maximum':
            return self._generate_maximum_answer(question, data, df)
        elif result_type == 'minimum':
            return self._generate_minimum_answer(question, data, df)
        elif result_type == 'average':
            return self._generate_average_answer(question, data, df)
        elif result_type == 'sum':
            return self._generate_sum_answer(question, data, df)
        elif result_type == 'trend':
            return self._generate_trend_answer(question, data, df)
        elif result_type == 'count':
            return self._generate_count_answer(question, data, df)
        else:
            return self._generate_general_answer(question, data, df)

    def _generate_comparison_answer(self, question: str, data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comparison answer"""
        answer_parts = []
        citations = []

        answer_parts.append("Based on the data analysis:\n\n")

        for item in data:
            entity = item['entity']
            metric = item['metric']
            value = item['value']
            row_idx = item['row_index']
            count = item['count']

            # Format value
            formatted_value = self._format_value(value)

            answer_parts.append(
                f"• **{entity}**: {formatted_value} {self._format_metric_name(metric)} "
                f"(averaged from {count} record{'s' if count > 1 else ''})"
            )

            # Create citation
            citation = self._create_citation(row_idx, metric, df)
            citations.append(citation)

        # Add comparison summary
        if len(data) >= 2:
            values = [item['value'] for item in data]
            max_item = data[values.index(max(values))]
            min_item = data[values.index(min(values))]

            answer_parts.append(
                f"\n**{max_item['entity']}** had the highest value "
                f"({self._format_value(max_item['value'])} {self._format_metric_name(max_item['metric'])}), "
                f"while **{min_item['entity']}** had the lowest "
                f"({self._format_value(min_item['value'])} {self._format_metric_name(min_item['metric'])})."
            )

        return {
            'answer': ''.join(answer_parts),
            'citations': citations
        }

    def _generate_maximum_answer(self, question: str, data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Generate maximum answer"""
        item = data[0]
        metric = item['metric']
        value = item['value']
        row_idx = item['row_index']
        entity_info = item.get('entity_info', {})

        answer_parts = []

        if 'state' in entity_info and 'year' in entity_info:
            answer_parts.append(
                f"The highest {self._format_metric_name(metric)} was recorded in "
                f"**{entity_info['state']}** during **{entity_info['year']}** "
                f"with a value of **{self._format_value(value)} {self._get_unit(metric)}**."
            )
        elif 'state' in entity_info:
            answer_parts.append(
                f"The highest {self._format_metric_name(metric)} was recorded in "
                f"**{entity_info['state']}** with a value of **{self._format_value(value)} {self._get_unit(metric)}**."
            )
        elif 'year' in entity_info:
            answer_parts.append(
                f"The highest {self._format_metric_name(metric)} was recorded in "
                f"**{entity_info['year']}** with a value of **{self._format_value(value)} {self._get_unit(metric)}**."
            )
        else:
            answer_parts.append(
                f"The maximum {self._format_metric_name(metric)} value found is "
                f"**{self._format_value(value)} {self._get_unit(metric)}**."
            )

        citation = self._create_citation(row_idx, metric, df)

        return {
            'answer': ''.join(answer_parts),
            'citations': [citation]
        }

    def _generate_minimum_answer(self, question: str, data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Generate minimum answer"""
        item = data[0]
        metric = item['metric']
        value = item['value']
        row_idx = item['row_index']
        entity_info = item.get('entity_info', {})

        answer_parts = []

        if 'state' in entity_info and 'year' in entity_info:
            answer_parts.append(
                f"The lowest {self._format_metric_name(metric)} was recorded in "
                f"**{entity_info['state']}** during **{entity_info['year']}** "
                f"with a value of **{self._format_value(value)} {self._get_unit(metric)}**."
            )
        elif 'state' in entity_info:
            answer_parts.append(
                f"The lowest {self._format_metric_name(metric)} was recorded in "
                f"**{entity_info['state']}** with a value of **{self._format_value(value)} {self._get_unit(metric)}**."
            )
        elif 'year' in entity_info:
            answer_parts.append(
                f"The lowest {self._format_metric_name(metric)} was recorded in "
                f"**{entity_info['year']}** with a value of **{self._format_value(value)} {self._get_unit(metric)}**."
            )
        else:
            answer_parts.append(
                f"The minimum {self._format_metric_name(metric)} value found is "
                f"**{self._format_value(value)} {self._get_unit(metric)}**."
            )

        citation = self._create_citation(row_idx, metric, df)

        return {
            'answer': ''.join(answer_parts),
            'citations': [citation]
        }

    def _generate_average_answer(self, question: str, data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Generate average answer"""
        answer_parts = []
        citations = []

        for item in data:
            metric = item['metric']
            value = item['value']
            count = item['count']
            row_indices = item.get('row_indices', [])

            answer_parts.append(
                f"The average {self._format_metric_name(metric)} is "
                f"**{self._format_value(value)} {self._get_unit(metric)}** "
                f"(calculated from {count} record{'s' if count > 1 else ''})."
            )

            # Create citations for sample rows
            sample_indices = row_indices[:3] if len(row_indices) > 3 else row_indices
            for idx in sample_indices:
                citation = self._create_citation(idx, metric, df)
                citations.append(citation)

            if len(row_indices) > 3:
                citations.append(f"... and {len(row_indices) - 3} more rows")

        return {
            'answer': ' '.join(answer_parts),
            'citations': citations
        }

    def _generate_sum_answer(self, question: str, data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Generate sum answer"""
        answer_parts = []
        citations = []

        for item in data:
            metric = item['metric']
            value = item['value']
            count = item['count']
            row_indices = item.get('row_indices', [])

            answer_parts.append(
                f"The total {self._format_metric_name(metric)} is "
                f"**{self._format_value(value)} {self._get_unit(metric)}** "
                f"(summed from {count} record{'s' if count > 1 else ''})."
            )

            # Create citations for sample rows
            sample_indices = row_indices[:3] if len(row_indices) > 3 else row_indices
            for idx in sample_indices:
                citation = self._create_citation(idx, metric, df)
                citations.append(citation)

            if len(row_indices) > 3:
                citations.append(f"... and {len(row_indices) - 3} more rows")

        return {
            'answer': ' '.join(answer_parts),
            'citations': citations
        }

    def _generate_trend_answer(self, question: str, data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Generate trend answer"""
        answer_parts = ["**Rainfall Trend Analysis:**\n\n"]
        citations = []

        # Sort by year
        sorted_data = sorted(data, key=lambda x: x['year'])

        for item in sorted_data:
            year = item['year']
            value = item['value']
            metric = item['metric']

            answer_parts.append(
                f"• **{year}**: {self._format_value(value)} {self._get_unit(metric)}\n"
            )

            # Add citation for first row of each year
            if item.get('row_indices'):
                citation = self._create_citation(item['row_indices'][0], metric, df)
                citations.append(citation)

        # Calculate trend
        if len(sorted_data) >= 2:
            first_value = sorted_data[0]['value']
            last_value = sorted_data[-1]['value']
            change = last_value - first_value
            percent_change = (change / first_value * 100) if first_value != 0 else 0

            trend_word = "increased" if change > 0 else "decreased"
            answer_parts.append(
                f"\n**Overall Trend**: The {self._format_metric_name(sorted_data[0]['metric'])} "
                f"{trend_word} by {abs(percent_change):.1f}% over this period."
            )

        return {
            'answer': ''.join(answer_parts),
            'citations': citations
        }

    def _generate_count_answer(self, question: str, data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Generate count answer"""
        count = data[0]['count']

        answer = f"There are **{count}** record{'s' if count != 1 else ''} matching your query."

        return {
            'answer': answer,
            'citations': []
        }

    def _generate_general_answer(self, question: str, data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Generate general answer"""
        answer_parts = ["Based on the available data:\n\n"]
        citations = []

        for item in data:
            metric = item['metric']

            answer_parts.append(f"**{self._format_metric_name(metric)}**:\n")
            answer_parts.append(f"• Mean: {self._format_value(item['mean'])} {self._get_unit(metric)}\n")
            answer_parts.append(f"• Minimum: {self._format_value(item['min'])} {self._get_unit(metric)}\n")
            answer_parts.append(f"• Maximum: {self._format_value(item['max'])} {self._get_unit(metric)}\n")
            answer_parts.append(f"• Total Records: {item['count']}\n\n")

            # Add sample citations
            sample_indices = item.get('row_indices', [])[:3]
            for idx in sample_indices:
                citation = self._create_citation(idx, metric, df)
                citations.append(citation)

        return {
            'answer': ''.join(answer_parts),
            'citations': citations
        }

    def _create_citation(self, row_idx: int, column: str, df: pd.DataFrame) -> str:
        """
        Create a citation string for a specific data point

        Args:
            row_idx: Row index in dataframe
            column: Column name
            df: DataFrame

        Returns:
            str: Citation string
        """
        try:
            value = df.loc[row_idx, column]
            citation = f"📍 Row {row_idx}, Column '{column}': {value}"

            # Add contextual information
            context_cols = []
            for col in df.columns:
                if col != column and pd.notna(df.loc[row_idx, col]):
                    val = df.loc[row_idx, col]
                    context_cols.append(f"{col}={val}")
                    if len(context_cols) >= 3:
                        break

            if context_cols:
                citation += f" (Context: {', '.join(context_cols)})"

            return citation
        except:
            return f"📍 Row {row_idx}, Column '{column}'"

    def _format_value(self, value: float) -> str:
        """Format numeric value for display"""
        if pd.isna(value):
            return "N/A"

        # Round to 2 decimal places
        if value >= 1000:
            return f"{value:,.2f}"
        else:
            return f"{value:.2f}"

    def _format_metric_name(self, metric: str) -> str:
        """Format metric name for natural language"""
        # Replace underscores with spaces and title case
        formatted = metric.replace('_', ' ').title()
        return formatted

    def _get_unit(self, metric: str) -> str:
        """Get unit for metric"""
        metric_lower = metric.lower()

        if 'mm' in metric_lower or 'millimeter' in metric_lower:
            return 'mm'
        elif 'cm' in metric_lower or 'centimeter' in metric_lower:
            return 'cm'
        elif 'inch' in metric_lower:
            return 'inches'
        elif 'temp' in metric_lower or 'celsius' in metric_lower:
            return '°C'
        elif 'fahrenheit' in metric_lower:
            return '°F'
        else:
            return ''

    def generate_llm_prompt(
            self,
            question: str,
            parsed_query: Dict[str, Any],
            results: Dict[str, Any],
            df: pd.DataFrame
    ) -> str:
        """
        Generate a prompt for an external LLM (like Ollama)

        Args:
            question: Original question
            parsed_query: Parsed query information
            results: Results from data analyzer
            df: Original dataframe

        Returns:
            str: Prompt for LLM
        """
        prompt_parts = [
            "You are a data analysis assistant. Generate a natural language answer to the user's question based on the provided data.\n\n",
            f"User Question: {question}\n\n",
            "Data Analysis Results:\n"
        ]

        # Add results summary
        result_type = results.get('type', 'general')
        data = results.get('data', [])

        prompt_parts.append(f"Query Type: {result_type}\n")
        prompt_parts.append(f"Number of Data Points: {len(data)}\n\n")

        # Add data details
        for i, item in enumerate(data, 1):
            prompt_parts.append(f"Data Point {i}:\n")
            for key, value in item.items():
                prompt_parts.append(f"  - {key}: {value}\n")
            prompt_parts.append("\n")

        prompt_parts.append(
            "\nInstructions:\n"
            "1. Generate a clear, natural language answer\n"
            "2. Include specific numbers and facts from the data\n"
            "3. For each fact, indicate which data point it comes from (e.g., 'Data Point 1')\n"
            "4. Keep the answer concise but informative\n"
            "5. Use a professional but friendly tone\n\n"
            "Answer:"
        )

        return ''.join(prompt_parts)