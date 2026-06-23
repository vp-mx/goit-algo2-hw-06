"""Task 2. Compare HyperLogLog performance with exact counting.

Script:
1. Loads log file and extracts IP addresses, ignoring invalid lines.
2. Exactly counts unique IPs using ``set``.
3. Approximately counts the same quantity using HyperLogLog.
4. Compares methods by execution time and outputs a results table.

Usage:
    python task2.py [path_to_log_file]

If the path is not provided, ``lms-stage-access.log`` in the current directory is used.
"""

import re
import sys
import time
from typing import Iterator

from hyperloglog import HyperLogLog

# Regular expression for IPv4 address at the start of a log file line.
IP_PATTERN = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3})")


def _is_valid_ip(ip: str) -> bool:
    """Check that each octet of IPv4 is in the range 0–255."""
    parts = ip.split(".")
    return len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)


def load_ip_addresses(file_path: str) -> Iterator[str]:
    """Lazy generator of IP addresses from a log file.

    Invalid lines (without a valid IP address) are ignored. The file is read
    line by line, so memory does not depend on its size — this makes
    the solution suitable for very large datasets.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            match = IP_PATTERN.match(line)
            if not match:
                continue
            ip = match.group(1)
            if _is_valid_ip(ip):
                yield ip


def exact_count_unique_ips(file_path: str) -> int:
    """Exact count of unique IP addresses using set."""
    unique = set()
    for ip in load_ip_addresses(file_path):
        unique.add(ip)
    return len(unique)


def hyperloglog_count_unique_ips(file_path: str, p: int = 14) -> float:
    """Approximate count of unique IP addresses using HyperLogLog."""
    hll = HyperLogLog(p=p)
    for ip in load_ip_addresses(file_path):
        hll.add(ip)
    return hll.count()


def _timed(func, *args, **kwargs):
    """Call func, return (result, time_in_seconds)."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed


def print_comparison_table(exact: int, exact_time: float,
                           approx: float, approx_time: float) -> None:
    """Print comparison results as a table."""
    error = abs(exact - approx) / exact * 100 if exact else 0.0
    print("\nComparison results:")
    print(f"{'':30}{'Exact count':>20}{'HyperLogLog':>20}")
    print(f"{'Unique elements':30}{exact:>20.1f}{approx:>20.1f}")
    print(f"{'Execution time (sec.)':30}{exact_time:>20.4f}{approx_time:>20.4f}")
    print(f"{'Relative error (%)':30}{'—':>20}{error:>20.2f}")


def main(file_path: str) -> None:
    exact, exact_time = _timed(exact_count_unique_ips, file_path)
    approx, approx_time = _timed(hyperloglog_count_unique_ips, file_path)
    print_comparison_table(exact, exact_time, approx, approx_time)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "lms-stage-access.log"
    try:
        main(path)
    except FileNotFoundError:
        print(
            f"File '{path}' not found.\n"
            "Download lms-stage-access.log and place it next to the script "
            "or pass the path as an argument: python task2.py /path/to/file.log"
        )
        sys.exit(1)
