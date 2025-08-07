"""
Interactive CLI module for the Quantum Experiment Framework.

This module handles the interactive command-line interface for running
quantum experiments with user-friendly prompts and rich output.
"""

import uuid
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table

from src.config.quick_experiments import QUICK_EXPERIMENTS, get_experiment_info
from src.config.params import apply_defaults, validate_parameters
from src.utils.input_handler import InputHandler
from src.utils.messages import MESSAGES
from src.utils import logger as logger_utils
from .display import DisplayManager


class InteractiveCLI:
    """
    Interactive command-line interface for quantum experiments.

    This class handles the interactive session, including parameter
    collection, experiment selection, and user interaction.
    """

    def __init__(self):
        """Initialize the interactive CLI."""
        self.console = Console()
        self.input_handler = InputHandler(self.console, MESSAGES)
        self.display_manager = DisplayManager(self.console)
        self.logger = logger_utils.setup_logger(
            log_level="INFO",
            log_to_file=True,
            log_to_console=True,
            structured_log_file="logs/structured_logs.json",
        )

    def print_message(self, key: str, **kwargs) -> None:
        """
        Print a console message from the MESSAGES lookup table.

        Args:
            key (str): The key to look up the message in MESSAGES.
            **kwargs: Values to format the message with.
        """
        message = MESSAGES.get(
            key, f"[bold red]Missing prompt for key: {key}[/bold red]"
        )
        self.console.print(message.format(**kwargs))

    def display_quick_options(self) -> None:
        """
        Display the available quick experiment options with categories and difficulty levels.
        """
        table = Table(
            title="🚀 Quick Experiment Options",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Name", style="green", width=25)
        table.add_column("Category", style="blue", width=12)
        table.add_column("Difficulty", style="magenta", width=12)
        table.add_column("Description", style="yellow")

        for key, option in QUICK_EXPERIMENTS.items():
            category = option.get("category", "unknown")
            difficulty = option.get("difficulty", "unknown")
            table.add_row(
                key, option["name"], category, difficulty, option["description"]
            )

        self.console.print(table)
        self.console.print(
            "\n💡 Choose an option number or press 'c' for custom parameters"
        )
        self.console.print(
            "📚 Categories: entanglement, topological, analysis, scaling, dynamics"
        )
        self.console.print("🎯 Difficulty: beginner, intermediate, advanced")

    def collect_parameters(self, interactive: bool = True) -> Dict[str, Any]:
        """
        Collect experiment parameters either interactively or from command-line arguments.

        Args:
            interactive (bool): Whether to collect parameters interactively.

        Returns:
            Dict[str, Any]: Collected experiment parameters.
        """
        # Start with default parameters
        args = apply_defaults({})

        if interactive:
            # Interactive parameter collection using InputHandler
            self.display_manager.display_info_message("🔧 Let's configure your quantum experiment!")

            # Number of qubits
            num_qubits = self.input_handler.get_numeric_input(
                "num_qubits_prompt",
                str(args["num_qubits"]),
                expected_type=int
            )
            args["num_qubits"] = int(num_qubits)

            # State type
            state_type = self.input_handler.get_input(
                "state_type_prompt",
                args["state_type"],
                valid_options=["ghz", "w", "cluster", "bell", "random"],
                valid_options_display=["GHZ", "W", "CLUSTER", "BELL", "RANDOM"]
            )
            args["state_type"] = state_type.upper()

            # Noise configuration
            noise_enabled = self.input_handler.prompt_yes_no("enable_noise_prompt", "y")
            args["noise_enabled"] = noise_enabled

            if noise_enabled:
                noise_type = self.input_handler.get_input(
                    "noise_type_prompt",
                    args.get("noise_type", "DEPOLARIZING"),
                    valid_options=["depolarizing", "phase_flip", "bit_flip", "thermal_relaxation"],
                    valid_options_display=["DEPOLARIZING", "PHASE_FLIP", "BIT_FLIP", "THERMAL_RELAXATION"]
                )
                args["noise_type"] = noise_type.upper()

                # Error rate
                error_rate = self.input_handler.get_numeric_input(
                    "error_rate_prompt",
                    str(args.get("error_rate", 0.1)),
                    expected_type=float
                )
                args["error_rate"] = float(error_rate)

            # Shots
            shots = self.input_handler.get_numeric_input(
                "shots_prompt",
                str(args["shots"]),
                expected_type=int
            )
            args["shots"] = int(shots)

            # Simulation mode
            sim_mode = self.input_handler.get_input(
                "sim_mode_prompt",
                args["sim_mode"],
                valid_options=["qasm", "statevector"],
                valid_options_display=["QASM", "Statevector"]
            )
            args["sim_mode"] = sim_mode.lower()

            # Visualization preferences
            enable_viz = self.input_handler.prompt_yes_no("enable_visualization_prompt", "y")
            if enable_viz:
                viz_type = self.input_handler.get_input(
                    "visualization_type_prompt",
                    "histogram",
                    valid_options=["histogram", "density_matrix", "hypergraph"],
                    valid_options_display=["Histogram", "Density Matrix", "Hypergraph"]
                )
                args["visualization_type"] = viz_type.lower()
            else:
                args["visualization_type"] = "none"

        return validate_parameters(args)

    def run_quick_experiment(self, choice: str) -> Dict[str, Any]:
        """
        Run a quick experiment based on user choice.

        Args:
            choice (str): The experiment choice from the user.

        Returns:
            Dict[str, Any]: The experiment configuration.
        """
        if choice == "c":
            return self.collect_parameters(interactive=True)

        if choice not in QUICK_EXPERIMENTS:
            self.print_message("invalid_choice")
            return self.collect_parameters(interactive=True)

        # Use predefined configuration
        selected_option = QUICK_EXPERIMENTS[choice]
        self.console.print(f"\n✅ Selected: {selected_option['name']}")
        args = apply_defaults(selected_option["config"])
        args = validate_parameters(args)

        return args

    def run_interactive_session(self) -> None:
        """
        Run the main interactive session loop.
        """
        while True:
            self.print_message("welcome")
            self.print_message("choose_option")
            self.print_message("skip_option")
            self.print_message("new_option")
            self.print_message("quit_option")

            choice = self.input_handler.get_input("your_choice", "s", ["s", "n", "q"])

            if choice == "s":
                self.print_message("running_with_defaults")
                self.display_quick_options()

                # Get available options
                valid_choices = list(QUICK_EXPERIMENTS.keys()) + ["c"]

                quick_choice = self.input_handler.get_input(
                    "quick_experiment_choice", "1", valid_choices
                )

                args = self.run_quick_experiment(quick_choice)

            elif choice == "n":
                args = self.collect_parameters(interactive=True)
            elif choice == "q":
                self.print_message("goodbye")
                return
            else:
                self.print_message("invalid_choice")
                continue

            # Display parameter summary
            self.display_manager.display_params_summary(args)

            # Confirm before running
            if self.input_handler.get_input("proceed_prompt", "y", ["y", "n"]) != "y":
                self.print_message("params_discarded")
                continue

            # Run the experiment
            try:
                from src.experiments.manager import get_experiment_manager
                
                self.display_manager.display_info_message("🚀 Running quantum experiment...")
                
                # Get experiment manager and run experiment
                em = get_experiment_manager()
                
                # Run experiment using user parameters as custom params
                # Filter out metadata that shouldn't go to the experiment runner
                experiment_params = {k: v for k, v in args.items() 
                                   if k not in ['name', 'description', 'category', 'difficulty']}
                
                result = em.run_experiment("ghz_basic", custom_params=experiment_params)
                
                if result:
                    self.display_manager.display_success_message("✅ Experiment completed successfully!")
                    self.display_manager.display_info_message(f"📁 Results: {result}")
                else:
                    self.display_manager.display_error_message("❌ Experiment failed")
                    
            except Exception as e:
                self.display_manager.display_error_message(f"❌ Error running experiment: {str(e)}")
                continue


def run_interactive() -> None:
    """
    Run the interactive CLI session.

    This is the main entry point for the interactive mode.
    """
    cli = InteractiveCLI()
    cli.run_interactive_session()
