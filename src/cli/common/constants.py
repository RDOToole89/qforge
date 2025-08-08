# Centralized constants for CLI labels, keys, and prompts

MAIN_MENU_OPTIONS = [
    ("1", "Quick Start (curated presets)", "1"),
    ("2", "Browse Presets", "2"),
    ("3", "Build Custom State", "3"),
    ("4", "Recent Results", "4"),
    ("5", "Settings", "5"),
    ("q", "Quit", "q"),
]

SETTINGS_MENU_OPTIONS = [
    ("settings", "Settings", "s"),
    ("help", "Help & Glossary", "h"),
    ("back", "Back", "b"),
]

FOOTER_HINTS = ["numbers=select", "enter=default", "?=help", "q=quit"]

CURATED_PRESETS = [
    ("ghz_basic", "GHZ State Basics", "GHZ", "3-qubit GHZ state baseline"),
    ("ghz_noise", "GHZ with Noise", "GHZ", "GHZ with depolarizing noise"),
    (
        "density_analysis",
        "Density Matrix Analysis",
        "GHZ",
        "Statevector analysis for GHZ",
    ),
    (
        "ghz_structured_decoherence_ref",
        "Structured Decoherence (Ref)",
        "GHZ",
        "Research preset",
    ),
]

# Use message keys directly; keep for future remapping if needed
