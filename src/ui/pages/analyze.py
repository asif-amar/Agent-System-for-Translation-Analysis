"""
Results analysis page.

Handles loading and analyzing experiment results.
"""

import streamlit as st
import pandas as pd
from pathlib import Path


def render():
    """Render the analyze page."""
    st.title("Analyze Results")

    st.markdown("""
    Load experiment results and calculate semantic distance metrics.
    """)

    config = st.session_state.config
    data_loader = st.session_state.data_loader
    runner = st.session_state.experiment_runner

    # Get available results
    results_list = config.get_available_results()

    if not results_list:
        st.warning("No experiment results found.")
        st.info("Run an experiment first or place results files in results/YYYY-MM-DD/input_name/ directory.")
        return

    # Results selection
    st.subheader("Select Results File")

    # Group by date and input name
    result_options = {}
    for res in results_list:
        label = f"{res['date']} - {res['input_name']} ({res['num_results']} sentences)"
        result_options[label] = res

    selected_label = st.selectbox(
        "Choose results to analyze",
        options=list(result_options.keys()),
        help="Select experiment results file"
    )

    selected_result = result_options[selected_label]

    # Display result info
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Experiment ID", selected_result['experiment_id'][:20] + "...")
    with col2:
        st.metric("Mode", selected_result['mode'])
    with col3:
        st.metric("Sentences", selected_result['num_results'])
    with col4:
        st.metric("Date", selected_result['date'])

    # Load and preview results
    with st.expander("Preview Results"):
        try:
            results_data = data_loader.load_results(selected_result['path'])

            summary = data_loader.get_result_summary(results_data)

            st.json(summary)

            # Show sample results
            sample_results = results_data['results'][:3]
            for i, res in enumerate(sample_results):
                st.markdown(f"**Sample {i+1}** (Error Rate: {res['error_rate']*100:.0f}%)")
                st.text(f"Original: {res['original'][:80]}...")
                st.text(f"Final:    {res['final'][:80]}...")
                st.markdown("---")

        except Exception as e:
            st.error(f"Error loading results: {e}")
            return

    # Check if metrics already exist
    metrics_files = config.get_metrics_files(selected_result['path'])
    metrics_exist = metrics_files['metrics_csv'].exists()

    if metrics_exist:
        st.info("Metrics already calculated for this experiment.")

        if st.button("Recalculate Metrics"):
            metrics_exist = False

    # Analysis options
    if not metrics_exist:
        st.subheader("Analysis Options")

        embedding_model = st.selectbox(
            "Embedding Model",
            ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "paraphrase-multilingual-MiniLM-L12-v2"],
            help="Select the embedding model for semantic distance calculation"
        )

        st.markdown("---")

        if st.button("Run Analysis", type="primary", width="stretch"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            def progress_callback(message):
                status_text.text(message)

            try:
                status_text.text("Starting analysis...")
                progress_bar.progress(25)

                result = runner.run_analysis(
                    results_file=selected_result['path'],
                    progress_callback=progress_callback
                )

                progress_bar.progress(100)

                if result['success']:
                    st.success(result['message'])

                    # Display results
                    st.subheader("Analysis Complete")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Generated Files:**")
                        st.code(result['metrics_file'], language="text")
                        st.code(result['graph_file'], language="text")

                    with col2:
                        st.markdown("**Next Steps:**")
                        st.info("Go to **Visualize Data** page to explore interactive charts")

                    # Show output
                    with st.expander("Analysis Output"):
                        st.text(result['output'])

                    st.rerun()
                else:
                    st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f"Error during analysis: {e}")
            finally:
                progress_bar.empty()
                status_text.empty()

    else:
        # Display existing metrics
        st.subheader("Metrics Summary")

        try:
            metrics_df = data_loader.load_metrics(str(metrics_files['metrics_csv']))

            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Min Distance", f"{metrics_df['cosine_distance'].min():.4f}")
            with col2:
                st.metric("Max Distance", f"{metrics_df['cosine_distance'].max():.4f}")
            with col3:
                st.metric("Mean Distance", f"{metrics_df['cosine_distance'].mean():.4f}")
            with col4:
                total_deg = metrics_df['cosine_distance'].iloc[-1] - metrics_df['cosine_distance'].iloc[0]
                st.metric("Total Degradation", f"{total_deg:.4f}")

            # Metrics table
            st.dataframe(
                metrics_df[['error_rate', 'cosine_distance', 'euclidean_distance', 'manhattan_distance']],
                width="stretch"
            )

            # Download metrics
            csv = metrics_df.to_csv(index=False)
            st.download_button(
                "Download Metrics CSV",
                data=csv,
                file_name="metrics.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"Error loading metrics: {e}")
