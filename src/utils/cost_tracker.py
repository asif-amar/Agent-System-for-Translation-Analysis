"""
Cost tracking module for monitoring API usage and costs.

This module tracks token usage and calculates costs for LLM API calls.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class APICall:
    """
    Data class representing a single API call.

    Attributes:
        timestamp: When the call was made
        agent: Name of the agent making the call
        model: Model identifier used
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        cost: Cost in USD
        experiment_id: ID of the experiment (optional)
        duration_seconds: How long the call took (optional)
    """

    timestamp: datetime
    agent: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    experiment_id: Optional[str] = None
    duration_seconds: Optional[float] = None


class CostTracker:
    """
    Track API usage and costs for translation experiments.

    This class logs all API calls with token counts and calculates costs
    based on model pricing. It can generate reports and aggregate statistics.

    Attributes:
        calls: List of all API calls made
        pricing: Pricing information for different models

    Example:
        >>> tracker = CostTracker()
        >>> tracker.log_call(
        ...     agent="EnglishToFrenchAgent",
        ...     model="claude-3-5-sonnet",
        ...     input_tokens=150,
        ...     output_tokens=120,
        ...     experiment_id="exp_001"
        ... )
        >>> print(tracker.get_total_cost())
        0.012
    """

    # Pricing per 1M tokens (as of 2025)
    DEFAULT_PRICING = {
        "claude-3-5-sonnet-20250929": {
            "input": 3.00 / 1_000_000,   # $3 per 1M input tokens
            "output": 15.00 / 1_000_000,  # $15 per 1M output tokens
        },
        "claude-3-5-sonnet": {
            "input": 3.00 / 1_000_000,
            "output": 15.00 / 1_000_000,
        },
        "claude-3-opus": {
            "input": 15.00 / 1_000_000,
            "output": 75.00 / 1_000_000,
        },
        "gpt-4-turbo": {
            "input": 10.00 / 1_000_000,
            "output": 30.00 / 1_000_000,
        },
        "gpt-4": {
            "input": 30.00 / 1_000_000,
            "output": 60.00 / 1_000_000,
        },
        "gpt-3.5-turbo": {
            "input": 0.50 / 1_000_000,
            "output": 1.50 / 1_000_000,
        },
    }

    def __init__(self, custom_pricing: Optional[Dict] = None):
        """
        Initialize the cost tracker.

        Args:
            custom_pricing: Optional custom pricing dictionary
                           Format: {"model_name": {"input": price, "output": price}}
        """
        self.calls: List[APICall] = []
        self.pricing = {**self.DEFAULT_PRICING}

        if custom_pricing:
            self.pricing.update(custom_pricing)

        self.logger = logging.getLogger(self.__class__.__name__)

    def log_call(
        self,
        agent: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        experiment_id: Optional[str] = None,
        duration_seconds: Optional[float] = None,
    ) -> float:
        """
        Log an API call with token usage.

        Args:
            agent: Name of the agent making the call
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            experiment_id: Optional experiment identifier
            duration_seconds: Optional duration of the call

        Returns:
            Cost of this call in USD

        Raises:
            ValueError: If token counts are negative
        """
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("Token counts cannot be negative")

        cost = self._calculate_cost(model, input_tokens, output_tokens)

        call = APICall(
            timestamp=datetime.now(),
            agent=agent,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            experiment_id=experiment_id,
            duration_seconds=duration_seconds,
        )

        self.calls.append(call)

        self.logger.debug(
            f"Logged API call: {agent} | {model} | "
            f"tokens: {input_tokens}+{output_tokens} | cost: ${cost:.4f}"
        )

        return cost

    def _calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for an API call.

        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        if model not in self.pricing:
            self.logger.warning(
                f"Model '{model}' not in pricing table. Using default pricing."
            )
            # Use average pricing as fallback
            input_price = 3.00 / 1_000_000
            output_price = 15.00 / 1_000_000
        else:
            input_price = self.pricing[model]["input"]
            output_price = self.pricing[model]["output"]

        cost = (input_tokens * input_price) + (output_tokens * output_price)
        return cost

    def get_total_cost(self) -> float:
        """
        Get total cost of all API calls.

        Returns:
            Total cost in USD
        """
        return sum(call.cost for call in self.calls)

    def get_total_tokens(self) -> Dict[str, int]:
        """
        Get total token usage across all calls.

        Returns:
            Dictionary with 'input', 'output', and 'total' token counts
        """
        input_total = sum(call.input_tokens for call in self.calls)
        output_total = sum(call.output_tokens for call in self.calls)

        return {
            "input": input_total,
            "output": output_total,
            "total": input_total + output_total,
        }

    def get_cost_by_agent(self) -> Dict[str, float]:
        """
        Get cost breakdown by agent.

        Returns:
            Dictionary mapping agent names to their total costs
        """
        costs_by_agent = {}

        for call in self.calls:
            if call.agent not in costs_by_agent:
                costs_by_agent[call.agent] = 0.0
            costs_by_agent[call.agent] += call.cost

        return costs_by_agent

    def get_cost_by_experiment(self) -> Dict[str, float]:
        """
        Get cost breakdown by experiment.

        Returns:
            Dictionary mapping experiment IDs to their total costs
        """
        costs_by_experiment = {}

        for call in self.calls:
            exp_id = call.experiment_id or "unknown"
            if exp_id not in costs_by_experiment:
                costs_by_experiment[exp_id] = 0.0
            costs_by_experiment[exp_id] += call.cost

        return costs_by_experiment

    def generate_report(self) -> pd.DataFrame:
        """
        Generate a detailed cost report as a DataFrame.

        Returns:
            Pandas DataFrame with all API call details
        """
        if not self.calls:
            return pd.DataFrame()

        data = [asdict(call) for call in self.calls]
        df = pd.DataFrame(data)

        # Format timestamp
        df['date'] = df['timestamp'].dt.date
        df['time'] = df['timestamp'].dt.time

        # Reorder columns
        columns = [
            'date', 'time', 'experiment_id', 'agent', 'model',
            'input_tokens', 'output_tokens', 'cost', 'duration_seconds'
        ]
        df = df[columns]

        return df

    def save_report(self, filepath: str) -> None:
        """
        Save cost report to CSV file.

        Args:
            filepath: Path to save the CSV file
        """
        df = self.generate_report()
        df.to_csv(filepath, index=False)
        self.logger.info(f"Cost report saved to: {filepath}")

    def get_summary(self) -> Dict:
        """
        Get a summary of costs and usage.

        Returns:
            Dictionary with summary statistics
        """
        if not self.calls:
            return {
                "total_calls": 0,
                "total_cost": 0.0,
                "total_tokens": {"input": 0, "output": 0, "total": 0},
                "cost_by_agent": {},
                "cost_by_experiment": {},
            }

        return {
            "total_calls": len(self.calls),
            "total_cost": self.get_total_cost(),
            "total_tokens": self.get_total_tokens(),
            "cost_by_agent": self.get_cost_by_agent(),
            "cost_by_experiment": self.get_cost_by_experiment(),
            "average_cost_per_call": self.get_total_cost() / len(self.calls),
        }

    def print_summary(self) -> None:
        """Print a formatted summary to console."""
        summary = self.get_summary()

        print("\n" + "=" * 60)
        print("COST TRACKING SUMMARY")
        print("=" * 60)
        print(f"Total API Calls: {summary['total_calls']}")
        print(f"Total Cost: ${summary['total_cost']:.4f}")
        print(f"Average Cost per Call: ${summary.get('average_cost_per_call', 0):.4f}")
        print(f"\nTotal Tokens:")
        print(f"  Input:  {summary['total_tokens']['input']:,}")
        print(f"  Output: {summary['total_tokens']['output']:,}")
        print(f"  Total:  {summary['total_tokens']['total']:,}")

        if summary['cost_by_agent']:
            print(f"\nCost by Agent:")
            for agent, cost in sorted(summary['cost_by_agent'].items()):
                print(f"  {agent}: ${cost:.4f}")

        if summary['cost_by_experiment']:
            print(f"\nCost by Experiment:")
            for exp_id, cost in sorted(summary['cost_by_experiment'].items()):
                print(f"  {exp_id}: ${cost:.4f}")

        print("=" * 60 + "\n")

    def clear(self) -> None:
        """Clear all logged calls."""
        self.calls = []
        self.logger.info("Cost tracker cleared")
