"""Entry point for `uvx umlforge` and `python -m connector`."""
from connector.server import mcp


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
