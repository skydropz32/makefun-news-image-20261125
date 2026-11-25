"""Entrypoint for The Daily Dispatch front page (news-image-20261125).

Renders the 1024x1024 front page and writes it to entry.png inside the
output directory: MAKEFUN_OUTPUT_DIR when set, otherwise /output.
Validates the PNG (signature, size, dimensions, byte budget) before
writing anything. Pure standard library.
"""

import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import render


def check_png(png):
    """Return (width, height) or raise on any failed check."""
    if len(png) < 33 or png[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    if png[12:16] != b"IHDR":
        raise ValueError("first chunk is not IHDR")
    width, height, depth, color = struct.unpack(">IIBB", png[16:26])
    if (width, height) != (1024, 1024):
        raise ValueError("wrong size %dx%d" % (width, height))
    if depth != 8 or color != 2:
        raise ValueError("need 8-bit RGB, got depth %d color %d"
                         % (depth, color))
    if len(png) > 1024 * 1024:
        raise ValueError("over 1 MiB: %d bytes" % len(png))
    return width, height


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    png = render.render_page()
    width, height = check_png(png)
    if render.LAST_Y > height:
        raise ValueError("layout overflows the page: ends at y=%d"
                         % render.LAST_Y)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png)
    # Round-trip check: what landed on disk must be exactly the bytes
    # we validated.
    with open(path, "rb") as fh:
        written = fh.read()
    if written != png:
        raise ValueError("written file differs from validated bytes")
    print("wrote %s (%d bytes, %dx%d, layout ends y=%d, sha256 %s)"
          % (path, len(png), width, height, render.LAST_Y,
             hashlib.sha256(png).hexdigest()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
