"""
Visualization page.

Interactive charts and graphs for exploring results.
"""

import streamlit as st
from pathlib import Path


def render():
    """Render the visualize page."""
    st.title("Visualize Data")

    st.markdown("""
    Explore experiment results with interactive visualizations.
    """)

    config = st.session_state.config
    data_loader = st.session_state.data_loader
    visualizer = st.session_state.visualizer

    # Get results with metrics
    results_list = config.get_available_results()

    if not results_list:
        st.warning("No experiment results found.")
        return

    # Filter results that have metrics
    results_with_metrics = []
    for res in results_list:
        metrics_files = config.get_metrics_files(res['path'])
        if metrics_files['metrics_csv'].exists():
            results_with_metrics.append(res)

    if not results_with_metrics:
        st.warning("No results with calculated metrics found.")
        st.info("Go to **Analyze Results** page to calculate metrics first.")
        return

    # Select result
    st.subheader("Select Dataset")

    result_options = {}
    for res in results_with_metrics:
        label = f"{res['date']} - {res['input_name']}"
        result_options[label] = res

    selected_label = st.selectbox(
        "Choose dataset to visualize",
        options=list(result_options.keys())
    )

    selected_result = result_options[selected_label]
    metrics_files = config.get_metrics_files(selected_result['path'])

    # Load data
    try:
        metrics_df = data_loader.load_metrics(str(metrics_files['metrics_csv']))
        results_data = data_loader.load_results(selected_result['path'])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    # Visualization options
    st.subheader("Visualization Options")

    viz_type = st.selectbox(
        "Chart Type",
        [
            "Error Rate vs Distance",
            "Multiple Metrics Comparison",
            "Distance Distribution",
            "Comprehensive Dashboard"
        ]
    )

    # Metric selection for single plots
    if viz_type != "Multiple Metrics Comparison":
        metric = st.selectbox(
            "Distance Metric",
            config.distance_metrics,
            format_func=lambda x: x.replace('_', ' ').title()
        )
    else:
        metrics_to_plot = st.multiselect(
            "Select Metrics",
            config.distance_metrics,
            default=config.distance_metrics,
            format_func=lambda x: x.replace('_', ' ').title()
        )

    st.markdown("---")

    # Generate visualization
    try:
        if viz_type == "Error Rate vs Distance":
            st.subheader("Error Rate vs Semantic Distance")

            fig = visualizer.plot_error_vs_distance(
                df=metrics_df,
                metric=metric,
                title=f"Translation Degradation - {metric.replace('_', ' ').title()}"
            )

            st.plotly_chart(fig, width="stretch")

            # Summary statistics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Initial Distance (0% error)",
                    f"{metrics_df[metric].iloc[0]:.4f}"
                )
            with col2:
                st.metric(
                    "Final Distance (50% error)",
                    f"{metrics_df[metric].iloc[-1]:.4f}"
                )
            with col3:
                degradation = metrics_df[metric].iloc[-1] - metrics_df[metric].iloc[0]
                st.metric("Total Degradation", f"{degradation:.4f}")

        elif viz_type == "Multiple Metrics Comparison":
            st.subheader("Multiple Distance Metrics")

            if not metrics_to_plot:
                st.warning("Please select at least one metric")
                return

            fig = visualizer.plot_multiple_metrics(
                df=metrics_df,
                metrics=metrics_to_plot,
                title="Comparison of Distance Metrics"
            )

            st.plotly_chart(fig, width="stretch")

            # Comparison table
            st.subheader("Metrics at Key Error Rates")

            key_rates = [0, 10, 25, 50]
            comparison_data = []

            for rate in key_rates:
                row = metrics_df[metrics_df['error_rate'] == rate]
                if not row.empty:
                    data_point = {'Error Rate': f"{rate}%"}
                    for m in metrics_to_plot:
                        if m in row.columns:
                            data_point[m.replace('_', ' ').title()] = f"{row[m].iloc[0]:.4f}"
                    comparison_data.append(data_point)

            if comparison_data:
                import pandas as pd
                st.table(pd.DataFrame(comparison_data))

        elif viz_type == "Distance Distribution":
            st.subheader("Distribution of Distance Values")

            fig = visualizer.plot_distribution(
                df=metrics_df,
                metric=metric,
                title=f"{metric.replace('_', ' ').title()} Distribution"
            )

            st.plotly_chart(fig, width="stretch")

            # Statistical summary
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Mean", f"{metrics_df[metric].mean():.4f}")
            with col2:
                st.metric("Median", f"{metrics_df[metric].median():.4f}")
            with col3:
                st.metric("Std Dev", f"{metrics_df[metric].std():.4f}")
            with col4:
                st.metric("Range", f"{metrics_df[metric].max() - metrics_df[metric].min():.4f}")

        elif viz_type == "Comprehensive Dashboard":
            st.subheader("Analysis Dashboard")

            fig = visualizer.create_dashboard(
                df=metrics_df,
                metric=metric
            )

            st.plotly_chart(fig, width="stretch")

    except Exception as e:
        st.error(f"Error generating visualization: {e}")

    # Static graphs section
    st.markdown("---")
    st.subheader("Static Visualizations")

    if metrics_files['distance_graph'].exists():
        col1, col2 = st.columns(2)

        with col1:
            st.image(
                str(metrics_files['distance_graph']),
                caption="Error vs Distance (Matplotlib)",
                width="stretch"
            )

        with col2:
            if metrics_files['dashboard'].exists():
                st.image(
                    str(metrics_files['dashboard']),
                    caption="Summary Dashboard",
                    width="stretch"
                )
