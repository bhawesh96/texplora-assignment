"""
Problem: Given an unsorted integer array nums, return the smallest missing positive integer.
Approach: Sort and iteratively find the smallest number
Sort: O(n log n)
Search: O(n)
Overall TC: O(n log n)
Overall SC: O(1)
"""

import unittest


"""
Find the smallest missing positive number
:param nums: the array of integers
:return: smallest missing positive number
"""
def smallest_missing_positive(nums):
    nums.sort()  # sort the input array

    smallest_missing_number = 1  # initialise the smallest missing number as 1
    for n in nums:  # iterate over the array
        if n == smallest_missing_number:  # if the number is found, increment the smallest probable number
            smallest_missing_number = smallest_missing_number + 1
        elif n > smallest_missing_number:  # we've found the smallest
            break

    return smallest_missing_number


class TestClass(unittest.TestCase):
    def test_smallest_missing_positive(self):
        self.assertEqual(smallest_missing_positive([3, 4, -1, 1]), 2)
        self.assertEqual(smallest_missing_positive([1, 2, 0]), 3)
        self.assertEqual(smallest_missing_positive([7, 8, 9, 11, 12]), 1)
        self.assertEqual(smallest_missing_positive([1, 2, 3]), 4)
        self.assertEqual(smallest_missing_positive([-1, -2, -3]), 1)


if __name__ == "__main__":
    unittest.main()
