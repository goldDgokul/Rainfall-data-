# 🌧️ Rainfall Data Q&A System

A Streamlit-based prototype that allows users to upload rainfall CSV files and ask natural language questions about the data. The system analyzes the data and provides answers with direct citations.

## Features

- **CSV Upload**: Upload rainfall statistics CSV files
- **Data Preview**: View and understand your data structure
- **Natural Language Queries**: Ask questions in plain English
- **Intelligent Parsing**: Extracts entities (states, years, metrics) from questions
- **Citation System**: Every answer includes direct citations to source data
- **Chat Interface**: Conversational UI with chat history
- **LLM Integration Ready**: Prepared for integration with local LLMs like Ollama

## Project Structure

```
rainfall-qa-system/
├── app.py                  # Main Streamlit application
├── data_loader.py          # CSV loading and preprocessing
├── query_parser.py         # Natural language query parsing
├── data_analyzer.py        # Data analysis and query execution
├── answer_generator.py     # Answer generation with citations
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step-by-Step Setup

1. **Clone or download the project files** to a directory on your computer:

```bash
mkdir rainfall-qa-system
cd rainfall-qa-system
```

2. **Create a virtual environment** (recommended):

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

## Running the Application

1. **Start the Streamlit app**:

```bash
streamlit run app.py
```

2. **Access the application**:
   - The app will automatically open in your default browser
   - If not, navigate to `http://localhost:8501`

3. **Upload a CSV file**:
   - Click "Browse files" in the sidebar
   - Select your rainfall CSV file
   - The system will automatically load and preview the data

4. **Ask questions**:
   - Type your question in the chat input at the bottom
   - Press Enter or click the send button
   - View the answer with citations

## CSV Format Requirements

Your CSV file should contain:

### Required Columns (at least one of each type):

1. **Geographic Identifier**: 
   - State, Region, District, Area, or Location
   - Example: `State`, `District`, `Region`

2. **Time Period**:
   - Year column (1900-2100 range)
   - Example: `Year`, `Yr`

3. **Rainfall Metrics** (numeric):
   - Rainfall measurements in any unit
   - Example: `Annual_Rainfall_mm`, `Monsoon_Rainfall`, `Total_Precipitation`

### Optional Columns:
- Month (`Month`, `Mon`)
- Season (`Season`)
- Temperature data
- Other climate metrics

### Example CSV Structure:

```csv
State,Year,Annual_Rainfall_mm,Monsoon_Rainfall_mm
Maharashtra,2015,1200.5,850.3
Maharashtra,2016,1350.2,920.1
Tamil Nadu,2015,950.8,680.5
Tamil Nadu,2016,1020.3,710.2
Karnataka,2015,1100.4,780.6
```

## Example Questions

### Comparison Queries:
- "Compare annual rainfall between Maharashtra and Tamil Nadu for 2015–2020."
- "Show me rainfall differences between Karnataka and Kerala."

### Maximum/Minimum Queries:
- "Which year had the highest rainfall in Karnataka?"
- "What was the lowest rainfall recorded in Rajasthan?"
- "Which state had the most rainfall in 2018?"

### Average Queries:
- "What was the average rainfall in Kerala during 2015-2020?"
- "Calculate the mean monsoon rainfall for Maharashtra."

### Trend Analysis:
- "Show me rainfall trends for Rajasthan from 2010 to 2020."
- "How has rainfall changed in Tamil Nadu over the years?"

## Module Descriptions

### 1. `app.py`
Main Streamlit application that:
- Handles file uploads
- Manages UI components
- Coordinates between different modules
- Displays chat interface and data preview

### 2. `data_loader.py`
Handles CSV processing:
- Loads CSV files
- Cleans column names (lowercase, underscores)
- Detects and converts data types (years, numeric values)
- Removes empty rows/columns
- Stores original column mappings

### 3. `query_parser.py`
Parses natural language questions:
- Extracts query intent (compare, maximum, minimum, etc.)
- Identifies entities (states, years, months, seasons)
- Detects relevant metrics (rainfall columns)
- Builds filter dictionaries

### 4. `data_analyzer.py`
Executes data queries:
- Applies filters to dataframe
- Performs aggregations (mean, sum, min, max)
- Groups data by entities
- Tracks row indices for citations
- Returns structured results

### 5. `answer_generator.py`
Generates natural language answers:
- Converts query results to readable text
- Creates citations with row/column references
- Formats numbers and units
- Generates context for citations
- Includes LLM prompt generation function

## LLM Integration (Ollama)

The system is designed to work with local LLMs. Here's how to integrate Ollama:

### Setup Ollama Integration:

1. **Install Ollama** (if not already installed):
   ```bash
   # Visit https://ollama.ai for installation instructions
   ```

2. **Create an LLM integration file** (`llm_integration.py`):

```python
import requests
import json

def query_ollama(prompt: str, model: str = "llama2") -> str:
    """
    Query Ollama local LLM
    
    Args:
        prompt: The prompt to send to the LLM
        model: Model name (default: llama2)
        
    Returns:
        str: LLM response
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except Exception as e:
        return f"Error querying Ollama: {str(e)}"
```

3. **Modify `answer_generator.py`** to use LLM:

```python
from llm_integration import query_ollama

# In AnswerGenerator class, add this method:
def generate_answer_with_llm(self, question, parsed_query, results, df):
    """Generate answer using local LLM"""
    prompt = self.generate_llm_prompt(question, parsed_query, results, df)
    llm_answer = query_ollama(prompt)
    
    # Still generate citations from results
    citations = self._extract_citations_from_results(results, df)
    
    return {
        'answer': llm_answer,
        'citations': citations
    }
```

## Troubleshooting

### Issue: CSV not loading
- **Solution**: Check that your CSV has proper headers and is comma-separated
- Ensure no special characters in column names
- Verify the file is not corrupted

### Issue: Questions not understood
- **Solution**: Be specific in your questions
- Mention exact column names or states as they appear in data
- Include year ranges explicitly (e.g., "2015 to 2020" instead of "recent years")

### Issue: No citations displayed
- **Solution**: This usually means no matching data was found
- Check if the entities (states, years) in your question exist in the data
- Review the data preview to understand available columns

### Issue: Streamlit won't start
- **Solution**: Ensure all dependencies are installed
- Check that port 8501 is not in use
- Try: `streamlit run app.py --server.port 8502`

## Customization

### Adding New Question Types:

1. **Update `query_parser.py`**:
   - Add new intent patterns in `intent_patterns` dictionary

2. **Update `data_analyzer.py`**:
   - Add new query execution method
   - Update `execute_query()` to handle new intent

3. **Update `answer_generator.py`**:
   - Add new answer generation method
   - Update `generate_answer()` to format new result type

### Customizing Citation Format:

Edit the `_create_citation()` method in `answer_generator.py`:

```python
def _create_citation(self, row_idx: int, column: str, df: pd.DataFrame) -> str:
    # Customize citation format here
    return f"Source: Row {row_idx}, {column}"
```

## Performance Considerations

- **Large CSV files**: The system loads the entire CSV into memory. For files >1GB, consider:
  - Chunked loading
  - Database backend (SQLite, PostgreSQL)
  - Filtering data before upload

- **Complex queries**: For queries involving multiple joins or complex aggregations, consider:
  - Implementing SQL query generation
  - Using Dask for parallel processing
  - Caching frequently accessed results

## Future Enhancements

Potential improvements:
- [ ] Multiple CSV file comparison
- [ ] Data visualization (charts/graphs)
- [ ] Export answers as PDF reports
- [ ] Voice input for questions
- [ ] Advanced statistical analysis
- [ ] Time series forecasting
- [ ] Database backend for large datasets
- [ ] User authentication and saved queries

## Contributing

Feel free to enhance the system:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available for educational and commercial use.

## Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review example questions
- Ensure CSV format matches requirements

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web application framework
- [Pandas](https://pandas.pydata.org/) - Data analysis library
- Python standard libraries

---

**Happy Data Analyzing! 🌧️📊**