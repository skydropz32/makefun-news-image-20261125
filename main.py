#!/usr/bin/env python3
"""news-image-20261125 entry (Python 3.13, standard library only).

The front-page image is the entry.png beside this file, drawn by render.py
on the build machine; this program copies it to /output/entry.png. The copy
pattern is the kit starter's: the grader's container is python:3.13-slim
with no Pillow installed, so the program itself uses only the standard
library and the image ships pre-rendered in the repository.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import shutil
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

SRC = HERE / "entry.png"
DST = OUT_DIR / "entry.png"

data = SRC.read_bytes()
assert data[:8] == b"\x89PNG\r\n\x1a\n", "entry.png is not a PNG"
width, height = struct.unpack(">II", data[16:24])
assert (width, height) == (1024, 1024), f"entry.png is {width}x{height}"
assert len(data) <= 1048576, f"entry.png is {len(data)} bytes (> 1 MiB)"

shutil.copyfile(SRC, DST)
print(f"wrote {DST} | {width}x{height} | bytes: {len(data)} | "
      f"sha256: {hashlib.sha256(data).hexdigest()}")
