from argparse import Namespace
from pathlib import Path

from dhv.dhv import DHV

app = DHV(
    Namespace(
        theme="textual-mono",
        source=Path(__file__).parent.parent.parent / "src/dhv/dhv.py",
    )
)
if __name__ == "__main__":
    app.run()
