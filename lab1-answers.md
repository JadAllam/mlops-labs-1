# Lab 1 answers

## Q1 - Files created by `uv init`

- `pyproject.toml` - project name, version, requires-python, dependencies, build backend.
- `.python-version` - pins the interpreter for this folder (3.11).
- `README.md` - empty.
- `src/mlops_lab_1/__init__.py` - the package.

After the first `uv add`: `uv.lock` (resolved exact versions, commit it) and `.venv/` (don't commit it).

## Q2 - Files created by `dvc init`

- `.dvc/config` - repo dvc config. Push.
- `.dvc/.gitignore` - excludes cache, tmp, config.local. Push.
- `.dvcignore` - paths dvc should skip. Push.
- `.dvc/cache/` - the actual data objects. Don't push.
- `.dvc/tmp/` - locks and scratch. Don't push.
- `.dvc/config.local` - per-machine config, where secrets go. Don't push.

dvc writes `.dvc/.gitignore` itself so the cache can't be committed by accident.

## Q3 - Credentials

`--global` writes to the user-level config outside the repo:
`C:\Users\jadal\AppData\Local\iterative\dvc\config` (Linux: `~/.config/dvc/config`).

Other options:
- `--local` -> `.dvc/config.local`, gitignored, per-repo.
- no flag (`--project`) -> `.dvc/config`, committed.
- `--system` -> machine-wide.

Narrowest wins: local > project > global > system.

They should not be pushed to github. Only `[core] remote = origin` ended up in `.dvc/config`.

Side effect of using `--global` for the URL too: a fresh clone on another machine has no
remote defined and `dvc pull` fails until the `dvc remote` commands are re-run.

## Q4 - .gitignore

`dvc add data` appended `/data` to `.gitignore`. Git now ignores the data directory and
tracks only `data.dvc`, so the two tools don't both try to version the same files.

## Q5 - The .dvc file

`data.dvc`, at the repo root. After adding only the raw data:

```yaml
outs:
- md5: a3a457d03c51ff8b037a833440f6ad13.dir
  size: 1188442712
  nfiles: 16643
  hash: md5
  path: data
```

The `.dir` md5 is the hash of a manifest listing every file and its own md5, stored in
`.dvc/cache`. `size` and `nfiles` describe the tree.

## Q6 - GitHub and DagsHub

On GitHub: the code, `.dvc/config`, `.dvcignore` and `data.dvc` are there. The 36,578
images are not - `/data` is gitignored. The whole repo is 156K.

`data.dvc` is the file that points to the data. It points by hash, not by location;
the remote config says where to fetch it from.

On DagsHub, after `dvc push`, the data shows under the Data tab.

## Q7 - Fresh clone

```
$ git clone https://github.com/JadAllam/mlops-labs-1.git && cd mlops-labs-1
$ ls data
ls: cannot access 'data': No such file or directory
$ du -sh .
156K    .
$ dvc status
data.dvc:
        changed outs:
                not in cache:       data
```

No data folder, only `data.dvc`. The command needed is `dvc pull`.

## Q8 - Old commit

After `git checkout d869093` alone: yes, both folders were still there. Git moved
`data.dvc` back to the raw-only hash but can't touch `data/` because it's gitignored.

After `dvc checkout`: no, they're gone.

```
$ dvc checkout
M       data\
$ ls data/
food11_raw
$ find data -type f | wc -l
16643
```

Back on main:

```
$ git checkout main && dvc checkout
$ ls data/
food11_processed  food11_processed_mini  food11_raw
$ find data -type f | wc -l
36578
```

`git checkout` moves the pointer, `dvc checkout` moves the data to match it. Both are needed.
