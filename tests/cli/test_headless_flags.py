import sys
from io import StringIO


def test_quiet_and_json_flags_do_not_error(monkeypatch):
    # Simulate args and capture stdout/stderr
    from main import main

    monkeypatch.setenv("QUANTUM_INTERACTIVE", "false")
    monkeypatch.setattr(sys, "argv", ["prog", "--list", "-q", "-J", "--stream-logs"])

    # Should not raise; just run
    main()
