def test_settings_edit_smoke():
    # Import and instantiate CLI; we won't drive interactive inputs here.
    from src.cli.interactive import InteractiveCLI

    cli = InteractiveCLI()
    assert hasattr(cli, "show_settings_stub")
