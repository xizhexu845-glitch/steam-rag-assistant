"""Start the demo from a reproducible source checkout."""
import argparse
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-json", type=Path, help="Build/update local index from JSON you may use")
    args = parser.parse_args()
    if not os.environ.get("ZHIPUAI_API_KEY"):
        parser.error("Set ZHIPUAI_API_KEY in your environment; do not put secrets in source files.")
    root = Path(__file__).resolve().parent
    source = args.build_json.resolve() if args.build_json else None
    os.chdir(root)
    if source:
        from DataProcess.chroma import chroma_update
        chroma_update(str(source))
        return
    if not (root / "data_base/vector_db/chroma").exists():
        parser.error("Build an index first: python start.py --build-json examples/games.synthetic.json")
    import sys
    from streamlit.web import cli
    sys.argv = ["streamlit", "run", str(root / "webui/streamlit.py")]
    raise SystemExit(cli.main())

if __name__ == "__main__":
    main()
