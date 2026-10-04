"""Resize every PNG under a folder to a square size (default 32x32) with Pillow.

Each image is scaled to fit inside the target size, keeping its aspect ratio,
then centred on a transparent canvas. Pixel art uses nearest-neighbour scaling
so it stays sharp. Files already at the target size are skipped.

Folders in SKIP_DIRS (sprite sheets and UI art) keep their native size.

The originals are overwritten, so run with --dry-run first to see what changes.

Usage:
    python tools/resize_assets.py --dry-run
    python tools/resize_assets.py
    python tools/resize_assets.py --dir assets/images --size 32
"""
import argparse
from pathlib import Path

from PIL import Image

DEFAULT_DIR = Path(__file__).resolve().parent.parent / "assets" / "images"

# Folders under the image root that keep their native size (sprite sheets, UI art).
SKIP_DIRS = {"ui"}


def fit(img, size):
    img = img.convert("RGBA")
    scale = min(size / img.width, size / img.height)
    new_size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
    scaled = img.resize(new_size, Image.Resampling.NEAREST)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = ((size - new_size[0]) // 2, (size - new_size[1]) // 2)
    canvas.paste(scaled, offset, scaled)
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR, help="folder to scan (recursive)")
    parser.add_argument("--size", type=int, default=32, help="target width and height in pixels")
    parser.add_argument("--dry-run", action="store_true", help="list changes without writing files")
    args = parser.parse_args()

    changed = skipped = 0
    for path in sorted(args.dir.rglob("*.png")):
        if SKIP_DIRS & set(path.relative_to(args.dir).parts[:-1]):
            continue
        img = Image.open(path)
        if img.size == (args.size, args.size):
            img.close()
            skipped += 1
            continue

        original_size = img.size
        result = fit(img, args.size)
        img.close()

        print(f"{original_size[0]}x{original_size[1]} -> {args.size}x{args.size}  {path}")
        if not args.dry_run:
            result.save(path)
        changed += 1

    action = "would resize" if args.dry_run else "resized"
    print(f"\n{action} {changed} file(s), {skipped} already {args.size}x{args.size}")


if __name__ == "__main__":
    main()
