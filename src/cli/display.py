"""
Display module for rich terminal output in the Quantum Experiment Framework.

This module handles all rich terminal output including tables, progress bars,
and formatted text for the CLI interface.
"""

from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


class DisplayManager:
    """
    Manages rich terminal output for the CLI interface.

    This class handles all display-related functionality including
    parameter summaries, experiment information, and progress indicators.
    """

    def __init__(self, console: Console):
        """
        Initialize the display manager.

        Args:
            console (Console): Rich console instance for output.
        """
        self.console = console

    def display_params_summary(self, args: Dict[str, Any]) -> None:
        """
        Display a formatted summary of experiment parameters.

        Args:
            args (Dict[str, Any]): Experiment parameters to display.
        """
        table = Table(
            title="Experiment Parameters", show_header=True, header_style="bold magenta"
        )
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="green")

        params_to_display = {
            "Number of Qubits": args["num_qubits"],
            "State Type": args["state_type"],
            "Noise Type": args["noise_type"],
            "Noise Enabled": args["noise_enabled"],
            "Shots": args["shots"],
            "Simulation Mode": args["sim_mode"],
            "Error Rate": (
                args["error_rate"] if args["error_rate"] is not None else "Default"
            ),
            "Z Probability": (
                args["z_prob"] if args["z_prob"] is not None else "Default"
            ),
            "I Probability": (
                args["i_prob"] if args["i_prob"] is not None else "Default"
            ),
            "T1": args["t1"] if args["t1"] is not None else "Default",
            "T2": args["t2"] if args["t2"] is not None else "Default",
            "Custom Params": args["custom_params"] if args["custom_params"] else "None",
        }

        # Add stepped noise parameters if present
        if args.get("noise_stepped", False):
            params_to_display.update(
                {
                    "Noise Stepped": "Yes",
                    "Noise Start": args.get("noise_start", 0.0),
                    "Noise End": args.get("noise_end", 0.5),
                    "Noise Steps": args.get("noise_steps", 10),
                }
            )
            if "z_prob_start" in args:
                params_to_display["Z Prob Start"] = args["z_prob_start"]
                params_to_display["Z Prob End"] = args["z_prob_end"]
            if "i_prob_start" in args:
                params_to_display["I Prob Start"] = args["i_prob_start"]
                params_to_display["I Prob End"] = args["i_prob_end"]
            if "t1_start" in args:
                params_to_display["T1 Start"] = args["t1_start"]
                params_to_display["T1 End"] = args["t1_end"]
            if "t2_start" in args:
                params_to_display["T2 Start"] = args["t2_start"]
                params_to_display["T2 End"] = args["t2_end"]

        for param, value in params_to_display.items():
            table.add_row(param, str(value))

        self.console.print(table)

    def display_experiment_info(self, experiment_info: Dict[str, Any]) -> None:
        """
        Display detailed information about an experiment.

        Args:
            experiment_info (Dict[str, Any]): Experiment information to display.
        """
        table = Table(
            title=f"Experiment: {experiment_info['name']}",
            show_header=True,
            header_style="bold blue",
        )
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        info_to_display = {
            "Name": experiment_info["name"],
            "Description": experiment_info["description"],
            "Category": experiment_info["category"],
            "Difficulty": experiment_info["difficulty"],
            "Qubits": experiment_info["config"]["num_qubits"],
            "State Type": experiment_info["config"]["state_type"],
            "Noise Type": experiment_info["config"]["noise_type"],
            "Shots": experiment_info["config"]["shots"],
        }

        for prop, value in info_to_display.items():
            table.add_row(prop, str(value))

        self.console.print(table)

    def create_progress_bar(self, description: str) -> Progress:
        """
        Create a progress bar for long-running operations.

        Args:
            description (str): Description of the operation.

        Returns:
            Progress: Rich progress bar instance.
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        )

    def display_success_message(self, message: str) -> None:
        """
        Display a success message.

        Args:
            message (str): Success message to display.
        """
        self.console.print(f"✅ {message}", style="bold green")

    def display_error_message(self, message: str) -> None:
        """
        Display an error message.

        Args:
            message (str): Error message to display.
        """
        self.console.print(f"❌ {message}", style="bold red")

    def display_warning_message(self, message: str) -> None:
        """
        Display a warning message.

        Args:
            message (str): Warning message to display.
        """
        self.console.print(f"⚠️ {message}", style="bold yellow")

    def display_info_message(self, message: str) -> None:
        """
        Display an info message.

        Args:
            message (str): Info message to display.
        """
        self.console.print(f"ℹ️ {message}", style="bold blue")

    def display_circuit_diagram(self, circuit) -> None:
        """
        Display the quantum circuit diagram.

        Args:
            circuit: Qiskit QuantumCircuit object to display.
        """
        try:
            circuit_text = circuit.draw(output='text', fold=-1)
            self.console.print("\n🔧 Compiled Circuit:")
            self.console.print(str(circuit_text), style="cyan")
            self.console.print("")
        except Exception as e:
            self.console.print(f"⚠️ Could not display circuit: {e}", style="yellow")

    def display_experiment_results(self, result_tuple) -> None:
        """
        Display comprehensive experiment results including circuit and measurements.

        Args:
            result_tuple: Tuple containing (circuit, results_dict) from experiment.
        """
        try:
            if isinstance(result_tuple, tuple) and len(result_tuple) >= 2:
                circuit, results = result_tuple
                
                # Display circuit diagram
                if hasattr(circuit, 'draw'):
                    self.display_circuit_diagram(circuit)
                
                # Display measurement results
                if isinstance(results, dict) and 'counts' in results:
                    counts = results['counts']
                    
                    self.console.print("📊 Measurement Results:")
                    
                    # Create a results table
                    table = Table(
                        title="Quantum Measurement Counts",
                        show_header=True,
                        header_style="bold magenta",
                    )
                    table.add_column("State", style="cyan", width=10)
                    table.add_column("Count", style="green", width=10)
                    table.add_column("Probability", style="yellow", width=12)
                    
                    total_shots = sum(counts.values())
                    
                    # Sort by count (descending)
                    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
                    
                    for state, count in sorted_counts:
                        probability = f"{count/total_shots:.4f}"
                        table.add_row(f"|{state}⟩", str(count), probability)
                    
                    self.console.print(table)
                    self.console.print(f"\n🎯 Total shots: {total_shots}")
                
                # Display metadata file if available
                if isinstance(results, dict) and 'metadata_file' in results:
                    metadata_file = results['metadata_file']
                    if metadata_file != 'results_placeholder':
                        self.console.print(f"📁 Results saved to: {metadata_file}")
                
            else:
                # Fallback to simple display
                self.console.print(f"📁 Results: {result_tuple}")
                
        except Exception as e:
            self.console.print(f"⚠️ Error displaying results: {e}", style="yellow")
            self.console.print(f"📁 Raw results: {result_tuple}")
