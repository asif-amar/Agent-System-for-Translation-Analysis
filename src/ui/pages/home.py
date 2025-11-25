"""
Home page module.

Displays welcome message, system overview, and quick stats.
"""

import streamlit as st
from pathlib import Path


def render():
    """Render the home page."""
    st.title("Translation Quality Analysis System")

    st.markdown("""
    ### Welcome to the Translation Quality Analysis System

    This system measures how spelling errors affect translation quality through
    a chain of automated language transformations: **EN → FR → HE → EN**

    #### Features:

    - **Run Experiments**: Execute translation chains on pre-corrupted datasets
    - **Analyze Results**: Calculate semantic distance metrics (Cosine, Euclidean, Manhattan)
    - **Visualize Data**: Interactive graphs showing error rate vs semantic distance
    - **Compare Translations**: Side-by-side comparison of original vs final translations

    #### Quick Start:

    1. Navigate to **Run Experiment** to prepare and execute experiments
    2. Go to **Analyze Results** to load existing results and calculate metrics
    3. Use **Visualize Data** for interactive charts and dashboards
    4. Explore **Compare Translations** for detailed text comparisons
    """)

    # Display system statistics
    st.markdown("---")
    st.subheader("System Overview")

    config = st.session_state.config
    data_loader = st.session_state.data_loader

    col1, col2, col3 = st.columns(3)

    with col1:
        datasets = config.get_available_datasets()
        st.metric("Available Datasets", len(datasets))

        if datasets:
            with st.expander("View Datasets"):
                for ds in datasets:
                    st.write(f"- **{ds['name']}** ({ds['num_sentences']} sentences)")

    with col2:
        results = config.get_available_results()
        st.metric("Experiment Results", len(results))

        if results:
            with st.expander("Recent Results"):
                for i, res in enumerate(results[:5]):
                    st.write(f"- {res['date']} - {res['input_name']}")
                if len(results) > 5:
                    st.write(f"...and {len(results) - 5} more")

    with col3:
        st.metric("Distance Metrics", len(config.distance_metrics))

        with st.expander("View Metrics"):
            for metric in config.distance_metrics:
                st.write(f"- {metric.replace('_', ' ').title()}")

    st.markdown("---")

    # Project information
    st.subheader("About")

    st.markdown("""
    This system is part of a research project investigating the robustness
    of machine translation systems to input noise. By introducing controlled
    spelling errors and measuring semantic drift through a translation chain,
    we can quantify translation quality degradation.

    **Technology Stack:**
    - Python 3.11+
    - Streamlit for UI
    - Sentence Transformers for embeddings
    - Plotly for interactive visualizations
    - Anthropic Claude for translations
    """)

    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Run New Experiment", type="primary", width="stretch"):
            st.info("👆 Select 'Run Experiment' from the navigation menu above to get started")

    with col2:
        if st.button("Analyze Results", type="secondary", width="stretch"):
            st.info("👆 Select 'Analyze Results' from the navigation menu above to view results")
