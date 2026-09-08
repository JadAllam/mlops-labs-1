# Lab 1 — Answers

Environment: Windows 11, Python 3.11.9, uv 0.12.10, dvc 3.67.1 (+ `dvc-http` for the
DagsHub HTTPS remote), git 2.54.

---

## Question 1 — Observe the files created by `uv init`, what do you think they contain?

```
.python-version              3.11
pyproject.toml               project metadata + dependencies
README.md                    empty placeholder
src/mlops_lab_1/__init__.py  the importable package
```

- **`pyproject.toml`** is the single source of truth for the project: name, version,
  `requires-python`, the `dependencies` list that `uv add` edits, the console-script
  entry point, and the build backend (`uv_build`). This is the file a human edits.
- **`.python-version`** pins the interpreter *for this folder*. `uv run` reads it and
  will download/select CPython 3.11 rather than using whatever `python` happens to be
  on `PATH`. This is what makes the project reproducible across machines.
- **`README.md`** — empty, just referenced by `readme = "README.md"` in the metadata.
- **`src/<pkg>/__init__.py`** — the src-layout package. Code under `src/` is only
  importable after the project is installed, which stops "works on my machine because
  the file happens to be in the cwd" bugs.

Two more files appear on the first `uv add` / `uv run`:

- **`uv.lock`** — the fully resolved dependency graph with exact versions and hashes.
  This is the *lockfile*: `pyproject.toml` says "pillow", `uv.lock` says
  "pillow 12.3.0, this hash, for these platforms". **Commit it** — it is what makes
  everyone's environment byte-identical.
- **`.venv/`** — the actual virtualenv. **Never commit it**; it is machine-specific and
  fully regenerable with `uv sync`.

---

## Question 2 — What are the files created by `dvc init`? What are they for? Which should be pushed to git?

```
.dvc/config       ✅ push   repo-level dvc config — currently just the default remote name
.dvc/.gitignore   ✅ push   written by dvc; excludes cache/, tmp/, config.local
.dvcignore        ✅ push   like .gitignore, but tells dvc which paths to skip when hashing
.dvc/cache/       ❌ no     the local content-addressed object store (the actual data bytes)
.dvc/tmp/         ❌ no     locks, run cache, state db — pure scratch
.dvc/config.local ❌ no     per-machine overrides; where secrets go if you use --local
```

The rule is the same one that governs the whole lab: **git gets the configuration and
the pointers, never the payload.** Note that dvc is self-defending here — it wrote
`.dvc/.gitignore` for you so that `cache`, `tmp` and `config.local` cannot be committed
by accident.

`.dvc/.gitignore` as generated:

```
/config.local
/tmp
/cache
```

---

## Question 3 — Where are the credentials stored? What are the options other than `--global`? Should they be pushed to github?

**Where.** `--global` writes to the *user-level* dvc config, outside the repository:

| OS | Path |
|---|---|
| Windows | `%LOCALAPPDATA%\iterative\dvc\config` → `C:\Users\jadal\AppData\Local\iterative\dvc\config` |
| Linux | `~/.config/dvc/config` |
| macOS | `~/Library/Application Support/dvc/config` |

Contents on this machine:

```ini
['remote "origin"']
    url = https://dagshub.com/JadAllam/mlops-labs-1.dvc
    auth = basic
    user = JadAllam
    password = <the DagsHub token>
```

**The other scopes**, from narrowest to widest:

| Flag | File | In git? | Use for |
|---|---|---|---|
| `--local` | `.dvc/config.local` | no — gitignored by dvc | secrets, *per-repo* |
| *(none)* = `--project` | `.dvc/config` | **yes** — committed | the remote URL, default remote |
| `--global` | user config dir | no — outside the repo | secrets shared across all your repos |
| `--system` | machine-wide | no | shared build agents |

They are merged narrowest-wins: `config.local` overrides `config`, which overrides
`--global`.

**Should they be pushed? No — never.** A DagsHub token is a bearer credential; anyone
who reads it can read and overwrite your remote, and rewriting git history to remove a
leaked secret does not un-leak it. Only the *non-secret* half goes in `.dvc/config`:

```ini
[core]
    remote = origin
```

The URL, user and password all live in the global config here. That is the safest of
the working options, but it has a real cost: a fresh clone of this repo knows the
*name* `origin` and nothing else, so `dvc pull` fails until the new machine also runs
the three `dvc remote` commands. The common middle ground is to commit the URL with
`dvc remote add origin <url>` (project scope, non-secret) and keep only
`user`/`password` in `--local` or `--global`. For CI, skip config files entirely and
use the environment variables `DVC_REMOTE_ORIGIN_USER` / `DVC_REMOTE_ORIGIN_PASSWORD`.

---

## Question 4 — Take a look at the `.gitignore` file. Explain what happened.

`dvc add data` **appended `/data` to `.gitignore`**:

```diff
  # OS
  Thumbs.db
  .DS_Store
+ /data
```

dvc did this on its own, and it is the whole trick of the git+dvc pairing. The two
tools would otherwise fight over the same 16,643 files. So dvc takes ownership of the
directory and, in the same breath, tells git to stop looking at it — then hands git one
small text file (`data.dvc`) to track instead.

After this line exists, `git status` will never show a single image, no matter how much
data you add. The repository stays small forever while still describing exactly which
data it belongs with.

---

## Question 5 — Do you see a `.dvc` file? What does it contain?

Yes — `data.dvc`, at the repo root, 6 lines of YAML. After adding only the raw data:

```yaml
outs:
- md5: a3a457d03c51ff8b037a833440f6ad13.dir
  size: 1188442712
  nfiles: 16643
  hash: md5
  path: data
```

- **`path: data`** — the working-tree directory this pointer stands for.
- **`md5: ….dir`** — the key. The `.dir` suffix means it is not the hash of a file but
  of a *manifest*: a JSON listing of every file in the tree with its own md5. That
  manifest lives in the dvc cache under `.dvc/cache/files/md5/a3/a457…`, and the
  individual image blobs are stored next to it, each under its own hash.
- **`size` / `nfiles`** — 1,188,442,712 bytes across 16,643 files, cached so dvc can
  report progress without re-walking the tree.

Because it is content-addressed, the hash *is* the identity of the dataset. Change one
pixel of one image and the top-level md5 changes — which is precisely what makes a
git commit of this 6-line file a complete, verifiable reference to 1.2 GB of data.
