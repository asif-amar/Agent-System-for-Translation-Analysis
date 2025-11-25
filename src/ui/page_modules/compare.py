"""
Comparison page.

Side-by-side comparison of original and translated texts.
"""

import streamlit as st
import pandas as pd


def render():
    """Render the compare page."""
    st.title("Compare Translations")

    st.markdown("""
    Detailed side-by-side comparison of translations at each stage.
    """)

    config = st.session_state.config
    data_loader = st.session_state.data_loader
    analyzer = st.session_state.analyzer

    # Get available results
    results_list = config.get_available_results()

    if not results_list:
        st.warning("No experiment results found.")
        return

    # Select result
    result_options = {}
    for res in results_list:
        label = f"{res['date']} - {res['input_name']}"
        result_options[label] = res

    selected_label = st.selectbox(
        "Choose dataset",
        options=list(result_options.keys())
    )

    selected_result = result_options[selected_label]

    # Load data
    try:
        results_data = data_loader.load_results(selected_result['path'])
        comparison_df = analyzer.create_comparison_dataframe(results_data)

        # Load metrics if available
        metrics_files = config.get_metrics_files(selected_result['path'])
        if metrics_files['metrics_csv'].exists():
            metrics_df = data_loader.load_metrics(str(metrics_files['metrics_csv']))
            # Merge metrics into comparison
            comparison_df = comparison_df.merge(
                metrics_df[['error_rate', 'cosine_distance', 'cosine_similarity']],
                on='error_rate',
                how='left'
            )
        else:
            metrics_df = None

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    # Filter options
    st.subheader("Filter Options")

    col1, col2 = st.columns(2)

    with col1:
        min_error = st.slider(
            "Minimum Error Rate",
            min_value=0.0,
            max_value=0.5,
            value=0.0,
            step=0.05,
            format="%.0f%%",
            key="min_error"
        ) * 100

    with col2:
        max_error = st.slider(
            "Maximum Error Rate",
            min_value=0.0,
            max_value=0.5,
            value=0.5,
            step=0.05,
            format="%.0f%%",
            key="max_error"
        ) * 100

    # Apply filter
    filtered_df = comparison_df[
        (comparison_df['error_rate'] >= min_error) &
        (comparison_df['error_rate'] <= max_error)
    ]

    st.info(f"Showing {len(filtered_df)} of {len(comparison_df)} sentences")

    # Comparison view type
    view_type = st.radio(
        "View Type",
        ["Detailed Comparison", "Summary Table", "Text Changes Analysis"],
        horizontal=True
    )

    st.markdown("---")

    if view_type == "Detailed Comparison":
        # Detailed side-by-side view
        for idx, row in filtered_df.iterrows():
            with st.container():
                st.subheader(f"Error Rate: {row['error_rate']:.0f}%")

                if metrics_df is not None and 'cosine_distance' in row:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.caption(f"Sentence ID: {row['id']}")
                    with col2:
                        st.metric("Distance", f"{row['cosine_distance']:.4f}")
                else:
                    st.caption(f"Sentence ID: {row['id']}")

                # Create tabs for each stage
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "Original",
                    "Misspelled",
                    "French",
                    "Hebrew",
                    "Final English"
                ])

                with tab1:
                    st.text_area(
                        "Original English",
                        value=row['original'],
                        height=100,
                        disabled=True,
                        key=f"orig_{idx}"
                    )
                    st.caption(f"Words: {row['word_count']}")

                with tab2:
                    st.text_area(
                        "Misspelled English",
                        value=row['misspelled'],
                        height=100,
                        disabled=True,
                        key=f"miss_{idx}"
                    )

                    # Highlight differences
                    if row['original'] != row['misspelled']:
                        changes = analyzer.calculate_text_changes(
                            row['original'],
                            row['misspelled']
                        )
                        st.caption(
                            f"Changed words: {changes['removed_words']} removed, "
                            f"{changes['added_words']} added"
                        )

                with tab3:
                    st.text_area(
                        "French Translation",
                        value=row['french'],
                        height=100,
                        disabled=True,
                        key=f"fr_{idx}",
                        label_visibility="collapsed"
                    )

                with tab4:
                    st.text_area(
                        "Hebrew Translation",
                        value=row['hebrew'],
                        height=100,
                        disabled=True,
                        key=f"he_{idx}",
                        label_visibility="collapsed"
                    )

                with tab5:
                    st.text_area(
                        "Final English",
                        value=row['final'],
                        height=100,
                        disabled=True,
                        key=f"final_{idx}"
                    )

                    # Compare with original
                    changes = analyzer.calculate_text_changes(
                        row['original'],
                        row['final']
                    )

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Common Words", changes['common_words'])
                    with col2:
                        st.metric("Words Removed", changes['removed_words'])
                    with col3:
                        st.metric("Words Added", changes['added_words'])

                st.markdown("---")

    elif view_type == "Summary Table":
        # Table view
        st.subheader("Summary Table")

        # Select columns to display
        display_cols = ['error_rate', 'word_count']
        if 'cosine_distance' in filtered_df.columns:
            display_cols.extend(['cosine_distance', 'cosine_similarity'])

        st.dataframe(
            filtered_df[display_cols],
            width="stretch"
        )

        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "Download Comparison Data",
            data=csv,
            file_name="comparison.csv",
            mime="text/csv"
        )

    elif view_type == "Text Changes Analysis":
        # Analysis of text changes
        st.subheader("Text Changes Analysis")

        changes_data = []
        for idx, row in filtered_df.iterrows():
            changes = analyzer.calculate_text_changes(row['original'], row['final'])
            changes['error_rate'] = row['error_rate']
            changes_data.append(changes)

        changes_df = pd.DataFrame(changes_data)

        # Plot changes
        import plotly.express as px

        fig = px.line(
            changes_df,
            x='error_rate',
            y=['common_words', 'added_words', 'removed_words'],
            title="Word Changes Across Error Rates",
            labels={'value': 'Word Count', 'error_rate': 'Error Rate (%)'},
            markers=True
        )

        st.plotly_chart(fig, width="stretch")

        # Statistics
        st.subheader("Change Statistics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Avg Retention Rate",
                f"{changes_df['word_retention_rate'].mean()*100:.1f}%"
            )
        with col2:
            st.metric(
                "Avg Words Removed",
                f"{changes_df['removed_words'].mean():.1f}"
            )
        with col3:
            st.metric(
                "Avg Words Added",
                f"{changes_df['added_words'].mean():.1f}"
            )
