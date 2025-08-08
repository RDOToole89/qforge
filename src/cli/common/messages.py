"""
Centralized lookup table for console messages used in the Quantum Experiment Interactive Runner.
"""

MESSAGES = {
    # Welcome and main menu messages
    "welcome": "[bold green]🚀 Welcome to the Quantum Experiment Interactive Runner![/bold green]",
    # Kept minimal top-level helpers
    "invalid_choice": "[bold red]⚠️ Invalid choice.[/bold red]",
    # (legacy prompts removed)
    # (unused stepped prompts removed)
    # Hypergraph-specific prompts
    "hypergraph_max_order_prompt": "Maximum correlation order (2-3) [{default}]: ",
    "hypergraph_threshold_prompt": "Correlation threshold for hypergraph [{default}]: ",
    "hypergraph_symmetry_analysis_prompt": "Perform symmetry analysis? (y/n) [{default}]: ",
    "hypergraph_plot_transitions_prompt": "Plot error transitions over time? (y/n) [{default}]: ",
    # Prompt for proceeding with parameters
    "proceed_prompt": "Proceed with these parameters? (y/n) [{default}]: ",
    # Validation warnings and prompts
    "invalid_input": "[bold red]⚠️ Invalid input: '{input}'. Please choose from {options}.[/bold red]",
    "operation_cancelled": "\n[bold yellow]Operation cancelled, returning to prompt...[/bold yellow]",
    "single_qubit_noise_warning": (
        "[bold yellow]⚠️ Warning: {noise_type} noise is designed for single-qubit systems, "
        "but you requested {num_qubits} qubits. This noise will only be applied to "
        "single-qubit gates ('id', 'u1', 'u2', 'u3').[/bold yellow]"
    ),
    "single_qubit_noise_prompt": (
        "Would you like to proceed with this configuration, switch to a multi-qubit noise type (e.g., DEPOLARIZING), or cancel? (p/switch/c) [{default}]: "
    ),
    "density_noise_warning": (
        "[bold yellow]⚠️ Warning: {noise_type} noise only applies to single-qubit gates, which are skipped in density matrix simulation mode. "
        "No noise will be applied with this configuration.[/bold yellow]"
    ),
    "density_noise_prompt": (
        "Would you like to proceed with noise disabled, switch to a multi-qubit noise type (e.g., DEPOLARIZING), or cancel? (p/switch/c) [{default}]: "
    ),
    "hypergraph_single_qubit_warning": (
        "[bold yellow]⚠️ Warning: {noise_type} noise with {num_qubits} qubits may not be meaningful for hypergraph visualization. "
        "Single-qubit noise only applies to single-qubit gates and won't affect multi-qubit correlations (e.g., entanglement between qubits). "
        "The hypergraph may only show the ideal correlations of the state without noise impact.[/bold yellow]"
    ),
    "hypergraph_single_qubit_prompt": (
        "Would you like to proceed with this configuration, switch to a multi-qubit noise type (e.g., DEPOLARIZING), or change visualization type? (p/switch/v) [{default}]: "
    ),
    "hypergraph_density_no_noise_warning": (
        "[bold yellow]⚠️ Warning: Hypergraph visualization in density matrix simulation mode with no noise enabled may not be insightful. "
        "The hypergraph will only show the ideal correlations of the {state_type} state without noise effects.[/bold yellow]"
    ),
    "hypergraph_density_no_noise_prompt": (
        "Would you like to proceed with this configuration, enable noise, or change visualization type? (p/e/v) [{default}]: "
    ),
    "hypergraph_plot_bloch_prompt": "Plot Bloch vectors? (y/n) [{default}]: ",
    "suggested_multi_qubit_noise_types": "[bold blue]Suggested multi-qubit noise types: DEPOLARIZING, PHASE_FLIP, THERMAL_RELAXATION[/bold blue]",
    "switched_noise_type": "[bold green]Switched noise type to {noise_type}.[/bold green]",
    "noise_disabled": "[bold yellow]Noise has been disabled for this configuration.[/bold yellow]",
    "switched_to_plot": "[bold blue]Switching visualization type to 'plot' (histogram/density matrix).[/bold blue]",
    "switched_to_plot_density": "[bold blue]Switching visualization type to 'plot' (density matrix).[/bold blue]",
    "noise_enabled": "[bold green]Noise has been enabled for this configuration.[/bold green]",
    # (unused legacy prompts removed)
    # Experiment execution messages
    "running_with_defaults": "\n[bold blue]⚡ Running with default configuration...[/bold blue]\n",
    "experiment_completed": "[bold green]✅ Experiment completed successfully![/bold green]\n📁 Results saved in `{filename}`",
    "plot_closed_ctrl_c": "\n[bold yellow]Plot closed with Ctrl+C, returning to prompt...[/bold yellow]",
    "current_params": "\n[bold blue]🔄 Current parameters:[/bold blue] {params}",
    "rerun_plot_prompt": "[bold yellow]Plot was closed with Ctrl+C. Would you like to run the experiment again with the same parameters?[/bold yellow]",
    "rerun_choice_prompt": "Run again? (y/n) [{default}]: ",
    "rerun_same": "\n[bold blue]🔁 Rerunning with same parameters...[/bold blue]\n",
    "restart_params": "\n[bold blue]🆕 Restarting parameter selection...[/bold blue]\n",
    "rerun_prompt": "\n➡️ Rerun? (r/same, n/new, q/quit) [{default}]: ",
    "running_step": "Running step {step} of {total}: error_rate={error_rate}, z_prob={z_prob}, i_prob={i_prob}, t1={t1}, t2={t2}",
    "params_discarded": "[bold yellow]Parameters discarded. Returning to prompt...[/bold yellow]",
    "goodbye": "\n[bold yellow]👋 Exiting Quantum Experiment Runner. Goodbye![/bold yellow]",
    # Interactive parameter collection prompts
    "num_qubits_prompt": "🔢 Number of qubits [{default}]: ",
    "state_type_prompt": "🌀 Quantum state type (GHZ/W/CLUSTER/BELL/RANDOM) [{default}]: ",
    "enable_noise_prompt": "🔊 Enable noise? (y/n): ",
    "noise_type_prompt": "⚡ Noise type (DEPOLARIZING/PHASE_FLIP/BIT_FLIP/THERMAL_RELAXATION) [{default}]: ",
    "error_rate_prompt": "📊 Error rate (0.0-1.0) [{default}]: ",
    "shots_prompt": "🎯 Number of shots [{default}]: ",
    "sim_mode_prompt": "💻 Simulation mode (qasm/statevector) [{default}]: ",
    "enable_visualization_prompt": "📊 Enable visualization? (y/n): ",
    "visualization_type_prompt": "🎨 Visualization type (histogram/density_matrix/hypergraph) [{default}]: ",
    "insights_details_prompt": "Show detailed metrics? (y/n) [{default}]: ",
    # Recent results menu
    "recent_results_title": "Recent Results",
    "no_results_found": "[bold yellow]No recent results found.[/bold yellow]",
    # Preset details and clone
    "clone_edit_title": "Clone & Edit?",
    # Custom wizard templates
    "custom_template_prompt": "Choose a template (optional) [{default}]: ",
    # Recent results actions
    "recent_action_title": "Result Actions",
    "recent_action_prompt": "Select action [{default}]: ",
    "recent_compare_title": "Compare Results",
    # Help & glossary
    "help_title": "Help & Glossary",
    "help_search_prompt": "Search term (Enter to list all) [{default}]: ",
    # Custom preview
    "custom_preview_prompt": "Preview custom circuit? (y/n) [{default}]: ",
    "custom_invalid_params": "[bold red]Invalid custom parameters: {reason}[/bold red]",
    # Custom state prompts
    "custom_state_source_prompt": "Custom source (gates/builder/openqasm) [{default}]: ",
    "custom_state_validate_prompt": "Validate custom state? (y/n) [{default}]: ",
    "custom_state_gates_json_prompt": 'Enter gates JSON (e.g., [{"name":"h","qargs":[0]}]) [{default}]: ',
    "custom_state_builder_prompt": "Enter builder dotted path (module:callable) [{default}]: ",
    "custom_state_qasm_path_prompt": "Enter OpenQASM file path [{default}]: ",
    # Presets browser prompts
    "preset_search_prompt": "🔎 Search presets (Enter to skip) [{default}]: ",
    "preset_show_options_help": "Show preset options/help? (y/n) [{default}]: ",
}
