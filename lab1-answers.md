Q1
pyproject.toml - project metadata and dependencies
.python-version - python version for the project (3.11)
README.md - empty
src/mlops_lab_1/__init__.py - the package
uv.lock and .venv/ appear after the first uv add

Q2
.dvc/config - dvc config, push
.dvc/.gitignore - ignores cache/tmp/config.local, push
.dvcignore - paths dvc skips, push
.dvc/cache/ - the data objects, don't push
.dvc/tmp/ - locks and scratch, don't push
.dvc/config.local - machine config and secrets, don't push

Q3
In the user level config outside the repo:
C:\Users\jadal\AppData\Local\iterative\dvc\config
Other options: --local (.dvc/config.local), no flag / --project (.dvc/config), --system.
No, credentials should not be pushed to github.

Q4
dvc add appended /data to .gitignore, so git ignores the data folder and tracks data.dvc instead.

Q5
Yes, data.dvc. It contains the md5 of the data folder, the size, the number of files, and the path.

Q6
Code: yes. Data: no. data.dvc points to the data. On dagshub the data shows after dvc push.

Q7
No data folder, only data.dvc. Need dvc pull.

Q8
After git checkout alone: yes, still there.
After dvc checkout: no, only food11_raw is left.
