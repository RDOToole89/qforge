# src/utils/input_handler.py

from typing import Optional, List, Union, Type
from rich.console import Console
from src.utils.validation import InputValidator


class InputHandler:
    """Handles user input with validation and formatting using rich console."""

    def __init__(self, console: Console, messages: dict, help_manager=None):
        """
        Initializes the InputHandler with a rich console and messages dictionary.

        Args:
            console (Console): The rich console instance for rendering prompts.
            messages (dict): The dictionary of message templates.
        """
        self.console = console
        self.messages = messages
        self.validator = InputValidator()
        self.help_manager = help_manager

    def get_input(
        self,
        prompt_key: str,
        default: str,
        valid_options: Optional[List[str]] = None,
        valid_options_display: Optional[List[str]] = None,
        help_context: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Gets user input with case-insensitive handling and validation.

        Args:
            prompt_key (str): The key for the prompt message in MESSAGES.
            default (str): Default value if user presses Enter.
            valid_options (list, optional): List of valid options for validation.
            valid_options_display (list, optional): List of options to display in the prompt.
            **kwargs: Additional values to format the prompt message with.

        Returns:
            str: User input or default, normalized to lowercase.
        """
        while True:
            try:
                prompt = self.messages.get(
                    prompt_key,
                    f"[bold red]Missing prompt for key: {prompt_key}[/bold red]",
                )
                format_kwargs = {"default": default}
                if valid_options is not None:
                    format_kwargs["valid_options"] = (
                        valid_options_display
                        if valid_options_display is not None
                        else valid_options
                    )
                format_kwargs.update(kwargs)
                extra = " [? for help]" if self.help_manager else ""
                self.console.print((prompt + extra).format(**format_kwargs), end="")
                raw = input().strip()
                if self.help_manager and raw == "?":
                    try:
                        self.help_manager.show()
                    except Exception:
                        pass
                    # reprint prompt after help
                    continue
                user_input = (raw or default).lower()
                if self.validator.validate_choice(user_input, valid_options):
                    return user_input
                self.console.print(
                    self.messages["invalid_input"].format(
                        input=user_input, options=valid_options
                    )
                )
            except KeyboardInterrupt:
                self.console.print(self.messages["operation_cancelled"])
                return default.lower()

    def get_numeric_input(
        self,
        prompt_key: str,
        default: str,
        expected_type: Type[Union[int, float]] = int,
    ) -> Union[int, float]:
        """
        Prompts the user for a numeric input, handling errors gracefully.

        Args:
            prompt_key (str): The key for the prompt message in MESSAGES.
            default (str): Default value as a string.
            expected_type (type): Expected type (int or float).

        Returns:
            Union[int, float]: The numeric value.

        Raises:
            ValueError: If the input cannot be converted to the expected type.
        """
        while True:
            user_input = self.get_input(prompt_key, default)
            value = self.validator.validate_numeric(user_input, expected_type)
            if value is not None:
                return value
            self.console.print(
                self.messages["invalid_input"].format(
                    input=user_input, options=[expected_type.__name__]
                )
            )
            # keep looping until valid input is provided

    def prompt_yes_no(
        self, key: str, default: str = "n", help_context: Optional[str] = None
    ) -> bool:
        """
        Prompts the user for a yes/no answer.

        Args:
            key (str): The key for the prompt message in MESSAGES.
            default (str): Default value ("y" or "n").

        Returns:
            bool: True if yes, False if no.
        """
        user_input = self.get_input(
            key,
            default,
            ["y", "yes", "t", "true", "n", "no", "f", "false"],
            help_context=help_context,
        )
        return self.validator.validate_yes_no(user_input)

    def select_option(
        self,
        title: str,
        options: list,
        default_value: str,
        hotkey_map: Optional[dict] = None,
        help_context: Optional[str] = None,
        enable_arrow_navigation: bool = True,
    ) -> str:
        """Interactive selection helper with numbers, hotkeys, and defaults.

        Args:
            title: Heading for the selection menu.
            options: List of tuples (value, label, hotkey) or (value, label).
            default_value: The default option value if user presses Enter.
            hotkey_map: Optional dict mapping hotkey -> value to override per-option hotkeys.

        Returns:
            The selected option value (string).
        """
        from rich.table import Table

        # Normalize options to (value, label, hotkey)
        normalized = []
        for item in options:
            if len(item) == 3:
                value, label, hotkey = item
            elif len(item) == 2:
                value, label = item
                hotkey = None
            else:
                raise ValueError("Each option must be (value,label[,hotkey])")
            if hotkey_map and value in hotkey_map:
                hotkey = hotkey_map[value]
            normalized.append((str(value), str(label), (hotkey or "").lower()))

        # Compute default index
        values = [v for v, _l, _h in normalized]
        try:
            default_index = values.index(str(default_value))
        except ValueError:
            default_index = 0
            default_value = values[0]

        while True:
            # Fancy arrow-key UI if available
            if enable_arrow_navigation:
                try:
                    import sys
                    if sys.stdin.isatty():
                        import questionary
                        choices = []
                        for idx, (value, label, hotkey) in enumerate(normalized, start=1):
                            is_default = (idx - 1) == default_index
                            title_text = f"{label} ({value})" + (" [default]" if is_default else "")
                            choices.append(questionary.Choice(title_text, value))
                        answer = questionary.select(
                            title,
                            choices=choices,
                            default=normalized[default_index][0],
                        ).ask()
                        if answer is not None:
                            return str(answer)
                except Exception:
                    # Fall back to rich table UI
                    pass

            table = Table(title=title, show_header=True, header_style="bold magenta")
            table.add_column("#", style="cyan", width=4)
            table.add_column("Option", style="green")
            table.add_column("Hotkey", style="yellow", width=8)
            table.add_column("Value", style="blue")
            for idx, (value, label, hotkey) in enumerate(normalized, start=1):
                label_display = label
                if idx - 1 == default_index:
                    label_display = f"{label} [default]"
                table.add_row(str(idx), label_display, hotkey or "-", value)

            self.console.print(table)
            suffix = " [? for help]" if self.help_manager else ""
            self.console.print(
                f"Select option number, hotkey, or value [{default_index+1}]{suffix}: ",
                end="",
            )
            raw = input().strip()
            if self.help_manager and raw == "?":
                try:
                    self.help_manager.show()
                except Exception:
                    pass
                continue
            if raw == "":
                return values[default_index]

            choice = raw.lower()

            # Numeric index
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(normalized):
                    return normalized[idx - 1][0]

            # Hotkey
            # Build hotkey -> value map
            hotkeys = {h: v for v, _l, h in normalized if h}
            if hotkey_map:
                # Merge additional hotkeys
                for hk, val in hotkey_map.items():
                    hotkeys[str(hk).lower()] = str(val)
            if choice in hotkeys:
                return hotkeys[choice]

            # Direct value match (case-insensitive)
            for v in values:
                if v.lower() == choice:
                    return v

            self.console.print(
                self.messages["invalid_input"].format(
                    input=raw, options=[str(i) for i in range(1, len(normalized) + 1)]
                )
            )
