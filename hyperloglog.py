"""Custom implementation of HyperLogLog algorithm (no external dependencies).

HyperLogLog is a probabilistic algorithm for estimating the number of unique
elements (cardinality) in large datasets with fixed memory cost (m registers,
one byte each).
"""

import hashlib
from math import log


class HyperLogLog:
    """HyperLogLog cardinality estimator.

    :param p: precision. Number of registers m = 2**p.
              Larger p means smaller error (≈ 1.04 / sqrt(m)),
              but more memory. p=14 -> m=16384, error ≈ 0.8%.
    """

    def __init__(self, p: int = 14) -> None:
        if not 4 <= p <= 16:
            raise ValueError("p must be in range [4, 16]")
        self.p = p
        self.m = 1 << p  # number of registers = 2**p
        self.registers = bytearray(self.m)
        self.alpha = self._get_alpha(self.m)

    @staticmethod
    def _get_alpha(m: int) -> float:
        """Bias correction coefficient depending on the number of registers."""
        if m == 16:
            return 0.673
        if m == 32:
            return 0.697
        if m == 64:
            return 0.709
        return 0.7213 / (1 + 1.079 / m)

    def add(self, item) -> None:
        """Add an element to the estimator."""
        # 64-bit hash of the element
        x = int.from_bytes(
            hashlib.sha1(str(item).encode("utf-8")).digest()[:8], "big"
        )
        # First p bits — register index
        j = x >> (64 - self.p)
        # Remaining bits — for counting position of first one
        w = x & ((1 << (64 - self.p)) - 1)
        rank = self._rho(w, 64 - self.p)
        if rank > self.registers[j]:
            self.registers[j] = rank

    @staticmethod
    def _rho(w: int, max_bits: int) -> int:
        """Position of first set bit (counting from the left) + 1."""
        if w == 0:
            return max_bits + 1
        rank = 1
        # Check bits from most significant to least significant
        bit = 1 << (max_bits - 1)
        while bit and not (w & bit):
            rank += 1
            bit >>= 1
        return rank

    def count(self) -> float:
        """Return the estimate of the number of unique elements."""
        # "Raw" estimate via harmonic mean
        z = sum(2.0 ** -reg for reg in self.registers)
        estimate = self.alpha * self.m * self.m / z

        # Correction for small values (linear counting)
        if estimate <= 2.5 * self.m:
            zeros = self.registers.count(0)
            if zeros != 0:
                estimate = self.m * log(self.m / zeros)

        # Correction for very large values (for 64-bit hash
        # practically doesn't apply, but included for completeness)
        two_32 = 1 << 32
        if estimate > two_32 / 30.0:
            estimate = -two_32 * log(1 - estimate / two_32)

        return estimate

    def __len__(self) -> int:
        return round(self.count())
