"""
Home page module.

Displays welcome message, system overview, and quick stats.
"""

import streamlit as st
from pathlib import Path
import numpy as np


def render():
    """Render the home page."""
    st.title("Translation Quality Analysis System")

    st.markdown("""
    ### Welcome to the Translation Quality Analysis System

    This system measures how spelling errors affect translation quality through
    a chain of automated language transformations: **EN → FR → HE → EN**
    """)

    # Interactive Translation Demo
    st.markdown("---")
    st.subheader("🔬 Try it Yourself - Live Translation Demo")

    st.markdown("""
    Enter an English sentence below and watch it transform through the translation chain.
    See the semantic drift in real-time!
    """)

    # Input section
    user_input = st.text_area(
        "Enter your English sentence:",
        placeholder="Type an English sentence here...",
        height=100,
        key="demo_input"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        translate_button = st.button("🌐 Translate", type="primary", use_container_width=True)

    # Process translation
    if translate_button and user_input.strip():
        _render_translation_demo(user_input.strip())

    elif translate_button and not user_input.strip():
        st.warning("Please enter a sentence to translate.")

    # Features section
    st.markdown("---")
    st.markdown("""
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


def _render_translation_demo(input_text: str):
    """
    Render the interactive translation demo with chat-style interface.

    Args:
        input_text: The English sentence to translate
    """
    runner = st.session_state.experiment_runner

    # Create container for translation chain
    st.markdown("### 🔄 Translation Chain")

    # Progress indicator
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Step 1: Original Input
        progress_bar.progress(0)
        status_text.text("Starting translation chain...")

        with st.container():
            st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h4 style='margin: 0; color: #1f77b4;'>🇬🇧 Original (English)</h4>
            </div>
            """, unsafe_allow_html=True)
            st.text_area("", value=input_text, height=80, disabled=True, key="demo_original", label_visibility="collapsed")

        # Step 2: EN -> FR
        progress_bar.progress(25)
        status_text.text("Translating English to French...")

        french = runner._translate_with_retry(runner._translate_en_to_fr, input_text)

        with st.container():
            st.markdown("""
            <div style='background-color: #e8f4f8; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h4 style='margin: 0; color: #2ca02c;'>🇫🇷 Step 1: French Translation</h4>
            </div>
            """, unsafe_allow_html=True)
            st.text_area("", value=french, height=80, disabled=True, key="demo_french", label_visibility="collapsed")

        # Step 3: FR -> HE
        progress_bar.progress(50)
        status_text.text("Translating French to Hebrew...")

        hebrew = runner._translate_with_retry(runner._translate_fr_to_he, french)

        with st.container():
            st.markdown("""
            <div style='background-color: #fff4e6; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h4 style='margin: 0; color: #ff7f0e;'>🇮🇱 Step 2: Hebrew Translation</h4>
            </div>
            """, unsafe_allow_html=True)
            st.text_area("", value=hebrew, height=80, disabled=True, key="demo_hebrew", label_visibility="collapsed")

        # Step 4: HE -> EN
        progress_bar.progress(75)
        status_text.text("Translating Hebrew back to English...")

        final = runner._translate_with_retry(runner._translate_he_to_en, hebrew)

        with st.container():
            st.markdown("""
            <div style='background-color: #f0e6ff; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h4 style='margin: 0; color: #9467bd;'>🎯 Final Result (English)</h4>
            </div>
            """, unsafe_allow_html=True)
            st.text_area("", value=final, height=80, disabled=True, key="demo_final", label_visibility="collapsed")

        progress_bar.progress(100)
        status_text.text("Calculating semantic metrics...")

        # Calculate metrics
        _render_metrics(input_text, final)

        progress_bar.empty()
        status_text.empty()

        st.success("✅ Translation complete!")

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Error during translation: {str(e)}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())


def _render_metrics(original: str, final: str):
    """
    Calculate and display semantic distance metrics.

    Args:
        original: Original English text
        final: Final English text after translation chain
    """
    from sentence_transformers import SentenceTransformer
    from scipy.spatial.distance import cosine, euclidean, cityblock
    import numpy as np

    st.markdown("---")
    st.markdown("### 📊 Semantic Distance Metrics")

    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;'>
        <p style='margin: 0; color: #666;'>
        These metrics measure how much meaning was preserved through the translation chain.
        Lower values indicate better preservation of semantic meaning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Computing embeddings..."):
        # Load embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Generate embeddings
        original_embedding = model.encode(original)
        final_embedding = model.encode(final)

        # Calculate distances
        cosine_dist = cosine(original_embedding, final_embedding)
        euclidean_dist = euclidean(original_embedding, final_embedding)
        manhattan_dist = cityblock(original_embedding, final_embedding)

    # Display metrics in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Cosine Distance",
            value=f"{cosine_dist:.4f}",
            delta=None,
            help="Measures angular distance between embeddings (0 = identical, 2 = opposite)"
        )

    with col2:
        st.metric(
            label="Euclidean Distance",
            value=f"{euclidean_dist:.4f}",
            delta=None,
            help="Straight-line distance between embedding vectors"
        )

    with col3:
        st.metric(
            label="Manhattan Distance",
            value=f"{manhattan_dist:.4f}",
            delta=None,
            help="Sum of absolute differences between embedding dimensions"
        )

    # Similarity score (inverse of cosine distance)
    similarity = (1 - cosine_dist) * 100

    # Visual quality indicator
    st.markdown("### 🎯 Translation Quality Score")

    quality_color = "#4caf50" if similarity >= 80 else "#ff9800" if similarity >= 60 else "#f44336"

    st.markdown(f"""
    <div style='background: linear-gradient(90deg, {quality_color} 0%, {quality_color} {similarity}%, #e0e0e0 {similarity}%, #e0e0e0 100%);
                height: 40px; border-radius: 20px; position: relative; margin: 20px 0;'>
        <div style='position: absolute; width: 100%; text-align: center; line-height: 40px; font-weight: bold; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>
            {similarity:.1f}% Semantic Similarity
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interpretation
    if similarity >= 80:
        st.success("🌟 Excellent! The translation chain preserved most of the original meaning.")
    elif similarity >= 60:
        st.warning("⚠️ Good, but some meaning was lost in the translation chain.")
    else:
        st.error("❌ Significant semantic drift detected. Much of the original meaning was lost.")

    # Text comparison
    st.markdown("### 📝 Text Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Original:**")
        st.info(original)

    with col2:
        st.markdown("**Final Result:**")
        st.info(final)

    # Word count comparison
    original_words = len(original.split())
    final_words = len(final.split())
    word_diff = abs(original_words - final_words)

    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px; margin: 10px 0;'>
        <p style='margin: 0;'>
        <strong>Word Count:</strong> Original: {original_words} words | Final: {final_words} words | Difference: {word_diff} words
        </p>
    </div>
    """, unsafe_allow_html=True)
