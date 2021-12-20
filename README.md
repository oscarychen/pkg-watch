# pkg-watch

A super-light weight python script that watches the list of currently installed packages on Mac OS and tracks changes overtime, notify user of changes in list of package id using Mac OS Notification (if set up using cron).
It has no Python dependency outside of Python 3's standard modules.
It relies on the pkgutil that comes with Mac OS.

## Usage

#### Running manually

You can run the `run.py` manually, ie:

```
python run.py
```

Each time it is executed, a list of packages will be write to file in the `log/` directory, next time the `run.py` is executed again, it will compare the current list of packages against the one in the log direcotry from previous time, and then print out a report. A detailed list of packages installed and removed will be saved in the `reports/` directory.

#### Setup for automatic execution

From Terminal:

```
crontab -e
```

and insert the following line:

```
* * * * * /PATH_TO_YOUR_PYTHON_/bin/python /PATH_TO_/pkg-watch/run.py --user
```

For debugging, you can use the following to print output of the python script:

```
* * * * *  /.../bin/python  /.../pkg-watch/run.py  --user  >> out.txt 2>&1
```

See more about crontab scheduling: https://crontab.guru

#### Reset and clear log and report files

```
python run.py --clear
```
