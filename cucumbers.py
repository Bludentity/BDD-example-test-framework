"""
This module contains a simple class modelling a cucumber basket.
Cucumbers can be added to the basket and removed from it.
The basket has a limited capacity.
"""

from tests.basketconfig import basket_capacity

class CucumberBasket:

    def __init__(self, initial_count=0, max_count=basket_capacity):
        if initial_count < 0:
            raise ValueError("Initial count cannot be negative")
        if max_count < 0:
            raise ValueError("Max count cannot be negative")

        self._count = initial_count
        self._max_count = max_count

    @property
    def count(self):
        return self._count

    @property
    def full(self):
        return self.count == self.max_count

    @property
    def empty(self):
        return self.count == 0

    @property
    def max_count(self):
        return self._max_count

    def add(self, count=1):
        new_count = self.count + count
        if new_count > self.max_count:
            raise ValueError("Attempted to add too many cucumbers")
        self._count = new_count

    def remove(self, count=1):
        new_count = self.count - count
        if new_count < 0:
            raise ValueError("Basket is already empty")
        self._count = new_count