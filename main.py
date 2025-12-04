"""Entry point for the Zenoti tooling CLI.

Allows running the Typer application via ``python main.py`` in addition to
``python -m zenoti_tool.cli``.
"""
from zenoti_tool.cli import app


if __name__ == "__main__":
    app()
