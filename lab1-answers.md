Q1
uv init made pyproject.toml, .python-version, README.md and src/mlops_lab_1/__init__.py.
pyproject.toml has the project name and the dependencies list, .python-version just says 3.11
so uv knows which python to use, README is empty and the src folder is the package.
uv.lock and .venv showed up later when I ran uv add pillow. The lock has the exact versions.

Q2
It made .dvc/config, .dvc/.gitignore and .dvcignore, plus .dvc/cache and .dvc/tmp.
config is the dvc settings, .dvcignore works like gitignore but for dvc, cache is where the
actual data files get stored and tmp is just temp stuff.
The ones that go to git are .dvc/config, .dvc/.gitignore and .dvcignore. The cache and tmp
should not, dvc already ignores them itself. config.local also stays out since that's where
secrets go.

Q3
Not in the repo. --global puts them in
C:\Users\jadal\AppData\Local\iterative\dvc\config
The other options are --local which writes to .dvc/config.local, no flag at all which writes to
.dvc/config, and --system for the whole machine.
I ended up using --local since that's what dagshub gives you, so the token is in
.dvc/config.local. dvc already ignores that file in .dvc/.gitignore.
No they shouldn't be pushed to github, anyone with the token could read and overwrite the remote.

Q4
dvc added /data at the end of .gitignore. So git stops tracking the data folder and only tracks
data.dvc, that way git and dvc aren't both trying to version the same files.

Q5
Yes, data.dvc in the root. It has the md5 of the whole data folder, the size in bytes, how many
files there are and the path. It's only 6 lines for 1.2GB of images.

Q6
The code is on github, the data isn't. data.dvc is the file that points to it.
On dagshub the data shows up under the data tab once you dvc push.

Q7
No data folder in the clone, just data.dvc. You need dvc pull to get it.

Q8
Right after git checkout they were still there, because git can't touch data since it's ignored.
Once I ran dvc checkout they were gone and only food11_raw was left. So you need both commands,
git for the pointer and dvc for the actual data.
