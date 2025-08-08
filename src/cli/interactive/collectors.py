# src/cli/interactive/collectors.py

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from src.config.params import apply_defaults, validate_parameters


class ParameterCollector:
    """Collect experiment parameters and handle custom state wizard."""

    def __init__(self, input_handler, display_manager):
        self.input_handler = input_handler
        self.display_manager = display_manager

    def collect_parameters(
        self,
        interactive: bool = True,
        base_args: Optional[Dict[str, Any]] = None,
        force_state_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        args = apply_defaults(base_args or {})
        if force_state_type is not None:
            args["state_type"] = force_state_type

        if not interactive:
            return validate_parameters(args)

        self.display_manager.display_info_message(
            "🔧 Let's configure your quantum experiment!"
        )

        # Number of qubits
        num_qubits = self.input_handler.get_numeric_input(
            "num_qubits_prompt", str(args["num_qubits"]), expected_type=int
        )
        args["num_qubits"] = int(num_qubits)

        # State type
        if force_state_type is None:
            state_options = [
                ("GHZ", "GHZ State", "g"),
                ("W", "W State", "w"),
                ("CLUSTER", "Cluster State", "c"),
                ("BELL", "Bell State", "b"),
                ("SUPERPOSITION", "Superposition (|+>^n)", "u"),
                ("CUSTOM", "Custom State", "m"),
                ("RANDOM", "Random State", "r"),
            ]
            args["state_type"] = self.input_handler.select_option(
                title="State Type",
                options=state_options,
                default_value=args["state_type"],
                help_context="state_type",
                show_value_column=False,
            )

        if args["state_type"] == "CUSTOM":
            custom_params = self._collect_custom_state_params(args["num_qubits"])
            if custom_params is None:
                raise KeyboardInterrupt()
            args["custom_params"] = custom_params

        # Shots
        shots = self.input_handler.get_numeric_input(
            "shots_prompt", str(args["shots"]), expected_type=int
        )
        args["shots"] = int(shots)

        # Simulation mode
        sim_mode = self.input_handler.select_option(
            title="Simulation Mode",
            options=[
                ("qasm", "QASM (shots)", "q"),
                ("density", "Density Matrix", "d"),
            ],
            default_value=args["sim_mode"],
            help_context="sim_mode",
            show_value_column=False,
        )
        args["sim_mode"] = sim_mode

        # Noise
        noise_enabled = self.input_handler.prompt_yes_no(
            "enable_noise_prompt", "y", help_context="noise"
        )
        args["noise_enabled"] = noise_enabled

        if noise_enabled:
            try:
                from src.core.noise_models.noise_factory import NOISE_CLASSES

                all_noise = list(NOISE_CLASSES.keys())
            except Exception:
                all_noise = [
                    "DEPOLARIZING",
                    "PHASE_FLIP",
                    "BIT_FLIP",
                    "THERMAL_RELAXATION",
                    "AMPLITUDE_DAMPING",
                    "PHASE_DAMPING",
                ]

            if args["sim_mode"] == "density":
                all_noise = [
                    nt
                    for nt in all_noise
                    if nt not in {"AMPLITUDE_DAMPING", "PHASE_DAMPING", "BIT_FLIP"}
                ]

            def _label(nt: str) -> str:
                return nt.replace("_", " ").title()

            noise_options = [(nt, _label(nt), nt[0].lower()) for nt in all_noise]
            args["noise_type"] = self.input_handler.select_option(
                title="Noise Type",
                options=noise_options,
                default_value=args.get("noise_type", "DEPOLARIZING"),
                help_context="noise_type",
                show_value_column=False,
            )

            error_rate = self.input_handler.get_numeric_input(
                "error_rate_prompt", str(args.get("error_rate", 0.1)), float
            )
            try:
                args["error_rate"] = float(error_rate)
            except Exception:
                pass

        # Visualization preference (store only the type; actual plotting is elsewhere)
        enable_viz = self.input_handler.prompt_yes_no(
            "enable_visualization_prompt", "y", help_context="viz"
        )
        if enable_viz:
            viz_type = self.input_handler.select_option(
                title="Visualization Type",
                options=[
                    ("histogram", "Histogram", "h"),
                    ("density_matrix", "Density Matrix", "d"),
                    ("hypergraph", "Hypergraph", "g"),
                ],
                default_value="histogram",
                help_context="viz_type",
                show_value_column=False,
            )
            args["visualization_type"] = viz_type
        else:
            args["visualization_type"] = "none"

        return validate_parameters(args)

    # --- Custom state helpers ---

    def _collect_custom_state_params(
        self, default_num_qubits: int
    ) -> Optional[Dict[str, Any]]:
        custom_params: Dict[str, Any] = {}
        relevant_templates = [
            ("none", "None", "n"),
            ("bell_phi_plus", "Bell |Φ+> (2 qubits)", "1"),
            ("w3_gate", "W(3) gate-based", "2"),
            ("cluster_1d_3", "Cluster 1D (3)", "3"),
            ("ghz_3", "GHZ (3) via gates", "4"),
            ("cancel", "Cancel and go back", "q"),
        ]
        filtered_templates = [
            (v, l, h)
            for (v, l, h) in relevant_templates
            if (
                v in {"none", "cancel"}
                or (v == "bell_phi_plus" and default_num_qubits == 2)
                or (
                    v in {"w3_gate", "cluster_1d_3", "ghz_3"}
                    and default_num_qubits == 3
                )
            )
        ]
        template_choice = self.input_handler.select_option(
            title="Custom Templates (optional)",
            options=filtered_templates or [("cancel", "Cancel and go back", "q")],
            default_value="none",
            show_value_column=False,
        )
        if template_choice == "cancel":
            return None
        if template_choice == "bell_phi_plus":
            return {
                "source": "gates",
                "num_qubits": 2,
                "gates": [{"name": "h", "qargs": [0]}, {"name": "cx", "qargs": [0, 1]}],
            }
        if template_choice == "w3_gate":
            return {
                "source": "gates",
                "num_qubits": 3,
                "gates": [
                    {"name": "u3", "params": [1.910633, 0, 0], "qargs": [0]},
                    {"name": "cx", "qargs": [0, 1]},
                    {"name": "u3", "params": [-1.910633, 0, 0], "qargs": [0]},
                    {"name": "u3", "params": [1.230959, 0, 0], "qargs": [0]},
                    {"name": "cx", "qargs": [0, 2]},
                    {"name": "u3", "params": [-1.230959, 0, 0], "qargs": [0]},
                ],
            }
        if template_choice == "cluster_1d_3":
            return {
                "source": "gates",
                "num_qubits": 3,
                "gates": [
                    {"name": "h", "qargs": [0]},
                    {"name": "h", "qargs": [1]},
                    {"name": "h", "qargs": [2]},
                    {"name": "cz", "qargs": [0, 1]},
                    {"name": "cz", "qargs": [1, 2]},
                ],
            }
        if template_choice == "ghz_3":
            return {
                "source": "gates",
                "num_qubits": 3,
                "gates": [
                    {"name": "h", "qargs": [0]},
                    {"name": "cx", "qargs": [0, 1]},
                    {"name": "cx", "qargs": [1, 2]},
                ],
            }

        # Source selection
        self.display_manager.display_info_message(
            "Simple: Gates JSON (recommended). Advanced: Python builder/OpenQASM (experts)."
        )
        advanced_enabled = False
        while True:
            source_options = [("gates", "Gates JSON", "g")]
            if not advanced_enabled:
                source_options.append(
                    ("advanced", "Show advanced (builder/OpenQASM)", "a")
                )
            else:
                source_options.extend(
                    [
                        ("builder", "Python builder (module:function)", "b"),
                        ("openqasm", "OpenQASM file", "o"),
                    ]
                )
            source_options.append(("cancel", "Cancel and go back", "q"))
            choice = self.input_handler.select_option(
                title="Custom Circuit Source",
                options=source_options,
                default_value="gates",
                show_value_column=False,
            )
            if choice == "advanced":
                advanced_enabled = True
                continue
            if choice == "cancel":
                return None
            custom_params: Dict[str, Any] = {"source": choice}
            break

        # Validate flag
        validate = self.input_handler.prompt_yes_no("custom_state_validate_prompt", "y")
        custom_params["validate"] = bool(validate)

        if choice == "gates":
            custom_params["num_qubits"] = default_num_qubits
            import json as _json

            while True:
                gates_json = self.input_handler.get_input(
                    "custom_state_gates_json_prompt", '[{"name":"h","qargs":[0]}]'
                )
                try:
                    gates = _json.loads(gates_json.replace("'", '"'))
                except Exception as e:
                    self.display_manager.display_error_message(f"Invalid JSON: {e}")
                    if not self.input_handler.prompt_yes_no(
                        "custom_state_validate_prompt", "y"
                    ):
                        return None
                    continue
                ok, reason = self._validate_gates_list(gates)
                if not ok:
                    self.display_manager.display_error_message(
                        f"Invalid gates specification: {reason}"
                    )
                    if not self.input_handler.prompt_yes_no(
                        "custom_state_validate_prompt", "y"
                    ):
                        return None
                    continue
                custom_params["gates"] = gates
                break
        elif choice == "builder":
            while True:
                builder = self.input_handler.get_input(
                    "custom_state_builder_prompt", "mypkg.builders:make_qc"
                )
                if ":" not in builder or builder.count(":") != 1:
                    self.display_manager.display_error_message(
                        "Builder must be in the form 'module.sub:func'"
                    )
                    if not self.input_handler.prompt_yes_no(
                        "custom_state_validate_prompt", "y"
                    ):
                        return None
                    continue
                custom_params["builder"] = builder
                break
            custom_params["num_qubits"] = default_num_qubits
        else:  # openqasm
            from pathlib import Path as _Path

            while True:
                qasm_path = self.input_handler.get_input(
                    "custom_state_qasm_path_prompt", "path/to/circuit.qasm"
                )
                if not _Path(qasm_path).exists():
                    self.display_manager.display_warning_message(
                        "Path not found. Ensure the file exists."
                    )
                    if not self.input_handler.prompt_yes_no(
                        "custom_state_validate_prompt", "y"
                    ):
                        return None
                    continue
                custom_params["openqasm"] = qasm_path
                break
            custom_params["num_qubits"] = default_num_qubits

        return custom_params

    @staticmethod
    def _validate_gates_list(gates_obj: Any) -> Tuple[bool, str]:
        if not isinstance(gates_obj, list):
            return False, "Expected a list of gate objects"
        for idx, item in enumerate(gates_obj):
            if not isinstance(item, dict):
                return False, f"Item {idx} must be an object"
            if "name" not in item or "qargs" not in item:
                return False, f"Item {idx} missing 'name' or 'qargs'"
            if not isinstance(item["name"], str):
                return False, f"Item {idx} 'name' must be string"
            if not isinstance(item["qargs"], list) or not all(
                isinstance(q, int) for q in item["qargs"]
            ):
                return False, f"Item {idx} 'qargs' must be list of integers"
            if "params" in item and not isinstance(item["params"], list):
                return False, f"Item {idx} 'params' must be a list if provided"
        return True, ""
