# goit-algo2-hw-06

Homework for the "Working with Data" module: Bloom filter and HyperLogLog.

## Task 1. Password uniqueness check using a Bloom filter

File: [`task1.py`](./task1.py)

Implements the `BloomFilter` class (`add` and `check` methods) and the
`check_password_uniqueness` function, which checks a list of new passwords
against the provided filter. Passwords are handled as plain strings, the
structure is memory-efficient (a fixed-size bit array regardless of the number
of elements), and it correctly handles invalid values (empty string, `None`,
non-string).

Run:

```bash
python task1.py
```

Expected output:

```
Password 'password123' - already used.
Password 'newpassword' - unique.
Password 'admin123' - already used.
Password 'guest' - unique.
```

## Task 2. Comparing HyperLogLog with exact counting

Files: [`task2.py`](./task2.py), [`hyperloglog.py`](./hyperloglog.py)

`task2.py` loads a log file, extracts IP addresses (invalid lines are ignored),
counts unique IPs exactly via `set`, approximately via a custom HyperLogLog
implementation (`hyperloglog.py`, no external dependencies), and prints a
comparison of execution time and accuracy as a table. The file is read line by
line (a lazy generator), so memory usage does not depend on the log file size.

Run (place `lms-stage-access.log` next to the script or pass the path as an
argument):

```bash
python task2.py
# or
python task2.py /path/to/lms-stage-access.log
```

Sample output:

```
Comparison results:
                                      Exact count         HyperLogLog
Unique elements                          100000.0             99948.2
Execution time (sec.)                      0.3837              0.5565
Relative error (%)                              —                0.05
```

> The log file is too large, so it is not included in the repository
> (see `.gitignore`) and does not need to be attached in the LMS.

## Requirements

Python ≥ 3.10. No external dependencies — only the standard library is used.