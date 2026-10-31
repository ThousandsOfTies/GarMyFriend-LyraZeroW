"""Product entry point; deployment mechanism lives in the pinned gar-tools."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"sources/gar-tools/composition"))
from device import main

if __name__=="__main__": main(ROOT)
