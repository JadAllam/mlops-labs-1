"""Prepare the Food-11 dataset for training with torchvision's ImageFolder.

Reads ./data/food11_raw/{training,evaluation,validation}/<label>_<n>.jpg and writes
two ImageFolder-shaped datasets under ./data:

  food11_processed/<split>/<Category>/<label>_<n>.jpg       all images, 128x128
  food11_processed_mini/<split>/<Category>/<label>_<n>.jpg  <=100 images per category

ResNet (torchvision.models.resnet*) is trained through torchvision.datasets.ImageFolder,
which infers the class from the *directory* holding each image -- hence the per-category
folders. The tensors it consumes are 224x224 by default; we store 128x128 to keep the
lab dataset small and let the training transform handle the final resize.

Run with:  uv run python ./src/food11/data.py
"""

from __future__ import annotations

import shutil
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image

# Index in this list == the numeric prefix of the raw file names.
CATEGORIES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]

SPLITS = ["training", "evaluation", "validation"]
IMAGE_SIZE = (128, 128)
MINI_PER_CATEGORY = 100

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "food11_raw"
PROCESSED_DIR = DATA_DIR / "food11_processed"
MINI_DIR = DATA_DIR / "food11_processed_mini"


def category_of(path: Path) -> str:
    """'3_1204.jpg' -> 'Egg'. Raises on anything that is not a Food-11 file name."""
    label = int(path.stem.split("_")[0])
    return CATEGORIES[label]


def resize_one(job: tuple[Path, Path]) -> None:
    src, dst = job
    with Image.open(src) as img:
        img.convert("RGB").resize(IMAGE_SIZE, Image.BILINEAR).save(dst, quality=95)


def build_split(split: str) -> tuple[int, int]:
    """Resize every image of one split into food11_processed, then mirror a capped
    subset of it into food11_processed_mini. Returns (full_count, mini_count)."""
    src_split = RAW_DIR / split
    if not src_split.is_dir():
        sys.exit(f"missing raw split: {src_split}")

    images = sorted(p for p in src_split.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})

    # Group by category so the mini cap is applied per category, not per split.
    by_category: dict[str, list[Path]] = {name: [] for name in CATEGORIES}
    for path in images:
        by_category[category_of(path)].append(path)

    jobs: list[tuple[Path, Path]] = []
    mini_pairs: list[tuple[Path, Path]] = []
    for category, paths in by_category.items():
        full_dir = PROCESSED_DIR / split / category
        mini_dir = MINI_DIR / split / category
        full_dir.mkdir(parents=True, exist_ok=True)
        mini_dir.mkdir(parents=True, exist_ok=True)
        for i, src in enumerate(paths):
            dst = full_dir / src.name
            jobs.append((src, dst))
            if i < MINI_PER_CATEGORY:
                # Copy the already-resized file rather than decoding the original twice.
                mini_pairs.append((dst, mini_dir / src.name))

    with ProcessPoolExecutor() as pool:
        list(pool.map(resize_one, jobs, chunksize=64))

    for processed, mini in mini_pairs:
        shutil.copyfile(processed, mini)

    print(f"  {split:<11} {len(jobs):>6} images -> processed, {len(mini_pairs):>5} -> mini")
    return len(jobs), len(mini_pairs)


def main() -> None:
    print(f"raw:  {RAW_DIR}")
    print(f"full: {PROCESSED_DIR}")
    print(f"mini: {MINI_DIR}  (<= {MINI_PER_CATEGORY} per category)\n")

    total_full = total_mini = 0
    for split in SPLITS:
        full, mini = build_split(split)
        total_full += full
        total_mini += mini

    print(f"\ndone: {total_full} processed images, {total_mini} mini images")


if __name__ == "__main__":
    main()
