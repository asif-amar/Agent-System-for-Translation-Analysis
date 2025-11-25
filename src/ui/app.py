"""
Main Streamlit application for Translation Quality Analysis System.

This module provides the main entry point for the web-based UI.
Run with: streamlit run src/ui/app.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from ui.config import UIConfig
from ui.data_loader import DataLoader
from ui.experiment_runner import ExperimentRunner
from ui.visualization import InteractiveVisualizer
from ui.comparison import ResultsAnalyzer


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'config' not in st.session_state:
        st.session_state.config = UIConfig()

    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = DataLoader()

    if 'experiment_runner' not in st.session_state:
        st.session_state.experiment_runner = ExperimentRunner(
            str(st.session_state.config.project_root)
        )

    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = InteractiveVisualizer()

    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = ResultsAnalyzer()

    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"


def main():
    """Main application entry point."""
    # Configure page settings FIRST before any other st commands
    st.set_page_config(
        page_title="Translation Quality Analysis",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    initialize_session_state()

    # Add custom CSS for left-aligned sidebar buttons
    st.markdown("""
        <style>
        .stSidebar button {
            text-align: left !important;
            justify-content: flex-start !important;
        }
        .stSidebar button div {
            display: flex;
            justify-content: flex-start !important;
            text-align: left !important;
        }
        .stSidebar button p {
            text-align: left !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    pages = ["Home", "Run Experiment", "Analyze Results", "Visualize Data", "Compare Translations"]
    icons = ["🏠", "🧪", "📊", "📈", "🔄"]

    # Create clickable navigation with left-aligned text
    for page, icon in zip(pages, icons):
        button_label = f"{icon} {page}"
        if st.sidebar.button(button_label, key=page, use_container_width=True):
            st.session_state.current_page = page

    st.sidebar.markdown("---")
    st.sidebar.info(
        "Translation Quality Analysis System\n\n"
        "Measure how spelling errors affect translation quality "
        "through a chain of automated language transformations."
    )

    # Import page modules
    from ui.page_modules import home, experiment, analyze, visualize, compare

    # Route to appropriate page based on session state
    page_mapping = {
        "Home": home.render,
        "Run Experiment": experiment.render,
        "Analyze Results": analyze.render,
        "Visualize Data": visualize.render,
        "Compare Translations": compare.render
    }

    # Render the current page
    current_page = st.session_state.current_page
    if current_page in page_mapping:
        page_mapping[current_page]()
    else:
        home.render()


if __name__ == "__main__":
    main()
