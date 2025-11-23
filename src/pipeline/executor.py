"""
Pipeline executor for coordinating SKILL-based translation agents.

This module provides orchestration for the translation chain experiment,
coordinating the execution of SKILL-based agents and managing data flow.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


logger = logging.getLogger(__name__)


class TranslationPipeline:
    """
    Orchestrate the translation chain experiment workflow.

    This class manages the complete workflow for running translation experiments
    using SKILL-based agents. It handles data preparation, result collection,
    and analysis coordination.

    Attributes:
        experiment_id: Unique identifier for the experiment
        output_dir: Directory for storing results
        logger: Logger instance
    """

    def __init__(
        self,
        experiment_id: Optional[str] = None,
        output_dir: str = "./results",
    ):
        """
        Initialize the translation pipeline.

        Args:
            experiment_id: Unique experiment identifier (auto-generated if None)
            output_dir: Directory for storing results
        """
        if experiment_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            experiment_id = f"exp_{timestamp}"

        self.experiment_id = experiment_id
        self.output_dir = Path(output_dir) / experiment_id
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initialized pipeline: {experiment_id}")

    def prepare_experiment_data(
        self,
        original_text: str,
        error_rates: List[float],
        misspelled_versions: Optional[List[str]] = None,
    ) -> Dict:
        """
        Prepare experiment data structure.

        Args:
            original_text: Original English sentence
            error_rates: List of error rates to test
            misspelled_versions: Pre-generated misspelled versions (optional)

        Returns:
            Dictionary with experiment configuration

        Raises:
            ValueError: If word count is less than 15
        """
        word_count = len(original_text.split())
        if word_count < 15:
            raise ValueError(
                f"Sentence must have at least 15 words (got {word_count})"
            )

        self.logger.info(
            f"Preparing experiment with {len(error_rates)} error rates"
        )

        experiment_data = {
            "experiment_id": self.experiment_id,
            "timestamp": datetime.now().isoformat(),
            "original_text": original_text,
            "word_count": word_count,
            "error_rates": error_rates,
            "test_cases": [],
        }

        # Create test cases for each error rate
        for i, rate in enumerate(error_rates):
            test_case = {
                "case_id": f"{self.experiment_id}_er{int(rate*100)}",
                "error_rate": rate,
                "original": original_text,
                "misspelled": misspelled_versions[i] if misspelled_versions else None,
                "translations": {
                    "french": None,
                    "hebrew": None,
                    "final_english": None,
                },
                "metadata": {
                    "status": "pending",
                    "created_at": datetime.now().isoformat(),
                },
            }
            experiment_data["test_cases"].append(test_case)

        # Save experiment configuration
        config_file = self.output_dir / "experiment_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Experiment configuration saved: {config_file}")

        return experiment_data

    def generate_agent_prompts(
        self,
        experiment_data: Dict,
        output_file: Optional[str] = None,
    ) -> Path:
        """
        Generate ready-to-use prompts for Claude Code agents.

        Args:
            experiment_data: Experiment configuration dictionary
            output_file: Output file path (auto-generated if None)

        Returns:
            Path to generated prompts file
        """
        if output_file is None:
            output_file = self.output_dir / "agent_prompts.txt"
        else:
            output_file = Path(output_file)

        self.logger.info(f"Generating agent prompts: {output_file}")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("CLAUDE CODE AGENT PROMPTS\n")
            f.write(f"Experiment ID: {self.experiment_id}\n")
            f.write("=" * 70 + "\n\n")

            f.write("Instructions:\n")
            f.write("1. Copy each prompt below into Claude Code CLI\n")
            f.write("2. Record the output for each step\n")
            f.write("3. Use the output as input for the next agent in the chain\n\n")

            for test_case in experiment_data["test_cases"]:
                error_rate = test_case["error_rate"]
                misspelled = test_case.get("misspelled", test_case["original"])

                f.write("\n" + "=" * 70 + "\n")
                f.write(f"Test Case: {int(error_rate*100)}% Error Rate\n")
                f.write("=" * 70 + "\n\n")

                # Agent 1: EN→FR
                f.write(f"# Step 1: English → French (Agent: agent-en-to-fr)\n")
                f.write(f'claude-code "Translate to French: {misspelled}"\n\n')

                # Agent 2: FR→HE
                f.write(f"# Step 2: French → Hebrew (Agent: agent-fr-to-he)\n")
                f.write(f'# Replace [FRENCH_OUTPUT] with the result from Step 1\n')
                f.write(f'claude-code "Translate to Hebrew: [FRENCH_OUTPUT]"\n\n')

                # Agent 3: HE→EN
                f.write(f"# Step 3: Hebrew → English (Agent: agent-he-to-en)\n")
                f.write(f'# Replace [HEBREW_OUTPUT] with the result from Step 2\n')
                f.write(f'claude-code "Translate to English: [HEBREW_OUTPUT]"\n\n')

                f.write(f"# Expected: Record all outputs in results.json\n\n")

        self.logger.info(f"Agent prompts saved: {output_file}")
        return output_file

    def create_results_template(
        self,
        experiment_data: Dict,
        output_file: Optional[str] = None,
    ) -> Path:
        """
        Create a template file for recording agent outputs.

        Args:
            experiment_data: Experiment configuration dictionary
            output_file: Output file path (auto-generated if None)

        Returns:
            Path to results template file
        """
        if output_file is None:
            output_file = self.output_dir / "results_template.json"
        else:
            output_file = Path(output_file)

        results_template = {
            "experiment_id": self.experiment_id,
            "timestamp": datetime.now().isoformat(),
            "results": [],
        }

        for test_case in experiment_data["test_cases"]:
            result_entry = {
                "error_rate": test_case["error_rate"],
                "original": test_case["original"],
                "misspelled": test_case.get("misspelled", test_case["original"]),
                "french": "TODO: Paste Agent 1 output here",
                "hebrew": "TODO: Paste Agent 2 output here",
                "final": "TODO: Paste Agent 3 output here",
                "word_count": test_case.get("word_count", len(test_case["original"].split())),
            }
            results_template["results"].append(result_entry)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_template, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Results template saved: {output_file}")
        return output_file

    def validate_results(self, results_file: str) -> bool:
        """
        Validate completed results file.

        Args:
            results_file: Path to results JSON file

        Returns:
            True if results are valid, False otherwise
        """
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)

            if "results" not in results:
                self.logger.error("Missing 'results' key in results file")
                return False

            for i, result in enumerate(results["results"]):
                required_fields = ["error_rate", "original", "final"]
                missing = [f for f in required_fields if f not in result]

                if missing:
                    self.logger.error(
                        f"Result {i} missing fields: {missing}"
                    )
                    return False

                # Check for TODO placeholders
                if "TODO" in str(result.get("final", "")):
                    self.logger.warning(
                        f"Result {i} contains TODO placeholder"
                    )
                    return False

            self.logger.info("Results validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False

    def get_experiment_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the experiment.

        Returns:
            Dictionary with experiment summary information
        """
        config_file = self.output_dir / "experiment_config.json"

        if not config_file.exists():
            return {
                "experiment_id": self.experiment_id,
                "status": "not_configured",
            }

        with open(config_file, 'r') as f:
            config = json.load(f)

        return {
            "experiment_id": self.experiment_id,
            "output_dir": str(self.output_dir),
            "timestamp": config.get("timestamp"),
            "original_text": config.get("original_text"),
            "word_count": config.get("word_count"),
            "num_test_cases": len(config.get("test_cases", [])),
            "error_rates": config.get("error_rates", []),
        }
