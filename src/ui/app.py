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


def setup_page():
    """Configure page settings."""
    config = st.session_state.config

    st.set_page_config(
        page_title=config.page_title,
        page_icon=config.page_icon,
        layout=config.layout,
        initial_sidebar_state="expanded"
    )


def render_sidebar():
    """Render the sidebar navigation."""
    st.sidebar.title("Navigation")

    pages = {
        "Home": "home",
        "Run Experiment": "experiment",
        "Analyze Results": "analyze",
        "Visualize Data": "visualize",
        "Compare Translations": "compare"
    }

    selected_page = st.sidebar.radio(
        "Select Page",
        list(pages.keys()),
        key="navigation"
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "Translation Quality Analysis System\n\n"
        "Measure how spelling errors affect translation quality "
        "through a chain of automated language transformations."
    )

    return pages[selected_page]


def main():
    """Main application entry point."""
    initialize_session_state()
    setup_page()

    page = render_sidebar()

    # Import page modules
    from ui.pages import (
        home, experiment, analyze, visualize, compare
    )

    # Route to appropriate page
    page_functions = {
        "home": home.render,
        "experiment": experiment.render,
        "analyze": analyze.render,
        "visualize": visualize.render,
        "compare": compare.render
    }

    page_functions[page]()


if __name__ == "__main__":
    main()
