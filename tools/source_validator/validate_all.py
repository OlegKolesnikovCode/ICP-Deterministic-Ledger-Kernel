from pathlib import Path
import sys


def _load_main():
    try:
        from source_validator.all_cli import main
    except ModuleNotFoundError:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from source_validator.all_cli import main
    return main


if __name__ == "__main__":
    raise SystemExit(_load_main()())

