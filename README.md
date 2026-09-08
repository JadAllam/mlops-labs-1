# mlops-labs-1 — Food-11

Lab 1 of the MLOps series: git + dvc side by side, and the data preparation script.

- **git** tracks the code and the *data pointers* (`data.dvc`).
- **dvc** tracks the *data itself*; the bytes live in the DagsHub remote, not in GitHub.

## Layout

```
data/food11_raw/{training,evaluation,validation}/<label>_<n>.jpg   512x512, flat
data/food11_processed/<split>/<Category>/<label>_<n>.jpg           128x128, ImageFolder
data/food11_processed_mini/<split>/<Category>/<label>_<n>.jpg      same, <=100 per category
src/food11/data.py                                                 builds the two processed sets
```

`data/` itself is git-ignored — only `data.dvc` is committed.

## Setup

```bash
uv sync                                  # python deps
dvc pull                                 # fetch data/ from the DagsHub remote
uv run python ./src/food11/data.py       # rebuild the processed datasets from raw
```

The dvc remote credentials are stored in the **global** dvc config
(`%LOCALAPPDATA%\iterative\dvc\config`), never in this repo. See `lab1-answers.md`.

## Categories

`0 Bread · 1 Dairy product · 2 Dessert · 3 Egg · 4 Fried food · 5 Meat ·
6 Noodles-Pasta · 7 Rice · 8 Seafood · 9 Soup · 10 Vegetable-Fruit`

The numeric prefix of each raw file name is the label index.
