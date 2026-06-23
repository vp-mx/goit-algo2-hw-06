"""Task 1. Verify password uniqueness using Bloom filter.

Implemented:
* ``BloomFilter`` class — adding elements and checking their presence;
* ``check_password_uniqueness`` function — checks a list of new passwords
  using the provided ``BloomFilter`` instance.

Passwords are processed as plain strings (without prior hashing).
The structure is memory-efficient: only a fixed-size bit array is stored,
regardless of the number of added elements.
"""

import hashlib


class BloomFilter:
    """Probabilistic data structure for membership testing.

    False positives are possible (element appears to be present when it wasn't added),
    but false negatives are not (if an element was added, it will definitely be found).
    """

    def __init__(self, size: int = 1000, num_hashes: int = 3) -> None:
        if not isinstance(size, int) or size <= 0:
            raise ValueError("size must be a positive integer")
        if not isinstance(num_hashes, int) or num_hashes <= 0:
            raise ValueError("num_hashes must be a positive integer")

        self.size = size
        self.num_hashes = num_hashes
        # bytearray uses 1 byte per bit-cell, which is efficient enough;
        # for millions of elements, memory remains fixed (= size).
        self.bit_array = bytearray(size)

    def _hashes(self, item: str):
        """Generate ``num_hashes`` indices in the bit array for the element.

        Uses double hashing (Kirsch–Mitzenmacher):
        h_i(x) = (h1(x) + i * h2(x)) mod size — this provides uniform distribution
        without needing a separate hash function for each index.
        """
        data = item.encode("utf-8")
        h1 = int.from_bytes(hashlib.md5(data).digest(), "big")
        h2 = int.from_bytes(hashlib.sha1(data).digest(), "big")
        for i in range(self.num_hashes):
            yield (h1 + i * h2) % self.size

    def add(self, item: str) -> None:
        """Add an element to the filter."""
        if not isinstance(item, str):
            raise TypeError("BloomFilter works only with strings")
        for index in self._hashes(item):
            self.bit_array[index] = 1

    def __contains__(self, item: str) -> bool:
        return self.check(item)

    def check(self, item: str) -> bool:
        """Check probable presence of an element in the filter."""
        if not isinstance(item, str):
            raise TypeError("BloomFilter works only with strings")
        return all(self.bit_array[index] for index in self._hashes(item))


def check_password_uniqueness(bloom: BloomFilter, passwords) -> dict:
    """Check a list of new passwords for uniqueness using the filter.

    Returns a dictionary ``{password: status}`` where status is
    ``"already used"`` or ``"unique"``.

    Invalid values (empty string, ``None``, non-string) are marked
    with status ``"invalid password"`` and do not raise an error.
    """
    if not isinstance(bloom, BloomFilter):
        raise TypeError("First argument must be a BloomFilter instance")

    results: dict = {}
    for password in passwords:
        if not isinstance(password, str) or password == "":
            results[password] = "invalid password"
            continue
        if bloom.check(password):
            results[password] = "already used"
        else:
            results[password] = "unique"
            # Immediately add new unique password so duplicates within
            # the list itself are also caught.
            bloom.add(password)
    return results


if __name__ == "__main__":
    # Initialize Bloom filter
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Add existing passwords
    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    # Check new passwords
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    # Print results
    for password, status in results.items():
        print(f"Password '{password}' - {status}.")
