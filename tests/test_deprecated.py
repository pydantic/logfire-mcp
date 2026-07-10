import pytest

from logfire_mcp.__main__ import main


def test_cli_exits_with_remote_server_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('sys.argv', ['logfire-mcp', '--read-token', 'fake-token'])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert 'Use the remote Logfire MCP server' in str(exc_info.value.code)


def test_version_still_works(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('sys.argv', ['logfire-mcp', '--version'])

    main()

    assert 'Logfire MCP v' in capsys.readouterr().out
