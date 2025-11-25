"""
Experiment execution page.

Handles experiment preparation and execution.
"""

import streamlit as st
from pathlib import Path


def render():
    """Render the experiment page."""
    st.title("Run Experiment")

    st.markdown("""
    Prepare and execute translation chain experiments on pre-corrupted datasets.
    """)

    config = st.session_state.config
    runner = st.session_state.experiment_runner

    # Get available datasets
    datasets = config.get_available_datasets()

    if not datasets:
        st.warning("No input datasets found in data/input/ directory.")
        st.info("Please add JSON files with pre-corrupted sentences to continue.")
        return

    # Dataset selection
    st.subheader("1. Select Input Dataset")

    dataset_options = {ds['name']: ds for ds in datasets}
    selected_name = st.selectbox(
        "Choose dataset",
        options=list(dataset_options.keys()),
        help="Select the input dataset containing sentences with different error rates"
    )

    selected_dataset = dataset_options[selected_name]

    # Display dataset info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sentences", selected_dataset['num_sentences'])
    with col2:
        st.metric("Type", selected_dataset['type'])
    with col3:
        st.metric("Created", selected_dataset['created_at'])

    if selected_dataset['description']:
        st.info(selected_dataset['description'])

    # Preview dataset
    with st.expander("Preview Dataset"):
        try:
            data_loader = st.session_state.data_loader
            data = data_loader.load_input_dataset(selected_dataset['path'])

            sentences = data.get('sentences', [])
            if sentences:
                st.write(f"**Total sentences:** {len(sentences)}")

                # Show first few sentences
                for i, sent in enumerate(sentences[:3]):
                    st.markdown(f"**Sentence {i+1}** (Error Rate: {sent['error_rate']*100:.0f}%)")
                    st.text(f"Original:   {sent['original'][:80]}...")
                    st.text(f"Misspelled: {sent['misspelled'][:80]}...")
                    st.markdown("---")

                if len(sentences) > 3:
                    st.write(f"...and {len(sentences) - 3} more sentences")
        except Exception as e:
            st.error(f"Error loading dataset: {e}")

    # Experiment configuration
    st.subheader("2. Configure Experiment")

    output_location = st.radio(
        "Output Location",
        ["Auto-generate (results/YYYY-MM-DD/dataset_name/)",
         "Custom directory"],
        help="Choose where to save experiment outputs"
    )

    custom_output = None
    if output_location == "Custom directory":
        custom_output = st.text_input(
            "Output Directory",
            value=str(config.results_dir / "custom_experiment")
        )

    # Execution mode
    st.subheader("3. Execution Mode")

    mode = st.radio(
        "Choose execution mode",
        ["Prepare Only (Generate prompts for manual execution)",
         "Prepare and Analyze (If results already exist)"],
        help="Select how to execute the experiment"
    )

    # Action buttons
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        prepare_button = st.button(
            "Prepare Experiment",
            type="primary",
            width="stretch",
            help="Generate experiment configuration and agent prompts"
        )

    with col2:
        if mode == "Prepare and Analyze (If results already exist)":
            analyze_button = st.button(
                "Analyze Results",
                type="secondary",
                width="stretch",
                disabled=True,
                help="Available after preparing experiment"
            )

    # Handle prepare action
    if prepare_button:
        with st.spinner("Preparing experiment..."):
            try:
                output_dir = custom_output if custom_output else None
                result = runner.prepare_experiment(
                    input_file=selected_dataset['path'],
                    output_dir=output_dir
                )

                if result['success']:
                    st.success(result['message'])

                    # Display generated files
                    st.subheader("Generated Files")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Configuration Files:**")
                        st.code(result['config_file'], language="text")
                        st.code(result['template_file'], language="text")

                    with col2:
                        st.markdown("**Prompts File:**")
                        st.code(result['prompts_file'], language="text")

                    # Next steps
                    st.info("""
                    **Next Steps:**

                    1. Open the `agent_prompts.txt` file
                    2. Run each prompt with Claude Code or manually with translation agents
                    3. Fill in `results_template.json` with translation outputs
                    4. Rename to `results_YYYYMMDD_HHMMSS.json`
                    5. Go to **Analyze Results** page to calculate metrics
                    """)

                    # Provide download for prompts file
                    prompts_path = Path(result['prompts_file'])
                    if prompts_path.exists():
                        with open(prompts_path, 'r', encoding='utf-8') as f:
                            prompts_content = f.read()

                        st.download_button(
                            label="Download Agent Prompts",
                            data=prompts_content,
                            file_name="agent_prompts.txt",
                            mime="text/plain"
                        )
                else:
                    st.error(f"Preparation failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f"Error during preparation: {e}")
