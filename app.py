"""
app.py - Main Streamlit Application for Rainfall Data Q&A System
"""

import streamlit as st
import pandas as pd
from data_loader import DataLoader
from query_parser import QueryParser
from data_analyzer import DataAnalyzer
from answer_generator import AnswerGenerator

# Page configuration
st.set_page_config(
    page_title="Rainfall Data Q&A System",
    page_icon="🌧️",
    layout="wide"
)

# Initialize session state
if 'data_loader' not in st.session_state:
    st.session_state.data_loader = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Title and description
st.title("🌧️ Rainfall Data Q&A System")
st.markdown("""
Upload your rainfall CSV file and ask questions in natural language. 
The system will analyze the data and provide answers with direct citations.
""")

# Sidebar for file upload
with st.sidebar:
    st.header("📁 Data Upload")
    uploaded_file = st.file_uploader(
        "Upload Rainfall CSV",
        type=['csv'],
        help="Upload a CSV file containing rainfall statistics"
    )

    if uploaded_file is not None:
        try:
            # Load and process data
            data_loader = DataLoader()
            df = data_loader.load_csv(uploaded_file)
            st.session_state.data_loader = data_loader

            st.success(f"✅ Loaded {len(df)} rows")
            st.info(f"**Columns:** {', '.join(df.columns.tolist())}")

        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            st.session_state.data_loader = None

# Main content area
if st.session_state.data_loader is not None:
    df = st.session_state.data_loader.df

    # Create tabs
    tab1, tab2 = st.tabs(["💬 Chat Interface", "📊 Data Preview"])

    with tab1:
        st.subheader("Ask Questions About Your Data")

        # Display chat history
        for i, chat in enumerate(st.session_state.chat_history):
            with st.chat_message("user"):
                st.write(chat['question'])
            with st.chat_message("assistant"):
                st.write(chat['answer'])
                if chat.get('citations'):
                    with st.expander("📎 View Citations"):
                        for citation in chat['citations']:
                            st.caption(citation)

        # Question input
        question = st.chat_input("Type your question here...")

        if question:
            # Display user question
            with st.chat_message("user"):
                st.write(question)

            # Process question
            with st.chat_message("assistant"):
                with st.spinner("Analyzing data..."):
                    try:
                        # Parse query
                        parser = QueryParser()
                        parsed_query = parser.parse(question, df)

                        # Analyze data
                        analyzer = DataAnalyzer(df)
                        results = analyzer.execute_query(parsed_query)

                        # Generate answer
                        generator = AnswerGenerator()
                        answer_data = generator.generate_answer(
                            question=question,
                            parsed_query=parsed_query,
                            results=results,
                            df=df
                        )

                        # Display answer
                        st.write(answer_data['answer'])

                        # Display citations
                        if answer_data['citations']:
                            with st.expander("📎 View Citations"):
                                for citation in answer_data['citations']:
                                    st.caption(citation)

                        # Save to chat history
                        st.session_state.chat_history.append({
                            'question': question,
                            'answer': answer_data['answer'],
                            'citations': answer_data['citations']
                        })

                    except Exception as e:
                        st.error(f"Error processing question: {str(e)}")
                        st.info("Please rephrase your question or check the data format.")

    with tab2:
        st.subheader("Data Preview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            numeric_cols = df.select_dtypes(include=['number']).columns
            st.metric("Numeric Columns", len(numeric_cols))

        # Display first rows
        st.write("**First 10 rows:**")
        st.dataframe(df.head(10), use_container_width=True)

        # Display column info
        st.write("**Column Information:**")
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.astype(str),
            'Non-Null Count': df.count(),
            'Sample Values': [str(df[col].dropna().iloc[0]) if len(df[col].dropna()) > 0 else 'N/A' for col in
                              df.columns]
        })
        st.dataframe(col_info, use_container_width=True)

        # Display statistics for numeric columns
        if len(numeric_cols) > 0:
            st.write("**Numeric Column Statistics:**")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)

else:
    # Welcome screen
    st.info("👈 Please upload a rainfall CSV file using the sidebar to get started.")

    st.markdown("""
    ### Example Questions You Can Ask:

    - "Compare annual rainfall between Maharashtra and Tamil Nadu for 2015–2020."
    - "Which year had the highest rainfall in Karnataka?"
    - "What was the average rainfall in Kerala during monsoon season?"
    - "Show me rainfall trends for Rajasthan from 2010 to 2020."
    - "Which state had the lowest rainfall in 2018?"

    ### Expected CSV Format:

    Your CSV should contain columns like:
    - **State/Region names** (e.g., Maharashtra, Karnataka)
    - **Year** (e.g., 2015, 2016)
    - **Rainfall measurements** (e.g., annual_rainfall_mm, monthly_rainfall)
    - **Optional:** Season, Month, District, etc.
    """)

# Footer
st.markdown("---")
st.caption("Rainfall Data Q&A System | Built with Streamlit")