import pytest
import time
from solution import *


class TestFindMedianSortedArrays:
    """Test suite for finding median of two sorted arrays."""
    
    # Basic correctness tests from examples
    def test_example1_odd_length(self):
        """Example 1: merged array has odd length."""
        nums1 = [1, 3]
        nums2 = [2]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 2.0
    
    def test_example2_even_length(self):
        """Example 2: merged array has even length."""
        nums1 = [1, 2]
        nums2 = [3, 4]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 2.5
    
    # Edge cases: empty arrays
    def test_first_array_empty(self):
        """First array is empty."""
        nums1 = []
        nums2 = [1]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 1.0
    
    def test_second_array_empty(self):
        """Second array is empty."""
        nums1 = [2]
        nums2 = []
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 2.0
    
    def test_both_arrays_single_element(self):
        """Both arrays have single element."""
        nums1 = [1]
        nums2 = [2]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 1.5
    
    def test_first_array_single_element(self):
        """First array has single element, second has multiple."""
        nums1 = [3]
        nums2 = [1, 2, 4]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 2.5
    
    def test_second_array_single_element(self):
        """Second array has single element, first has multiple."""
        nums1 = [1, 2, 4]
        nums2 = [3]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 2.5
    
    # Edge cases: negative numbers
    def test_negative_numbers(self):
        """Arrays contain negative numbers."""
        nums1 = [-2, -1]
        nums2 = [-3, 0]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [-3, -2, -1, 0], median = (-2 + -1) / 2 = -1.5
        assert result == -1.5
    
    def test_all_negative(self):
        """All numbers are negative."""
        nums1 = [-5, -3]
        nums2 = [-4, -2]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [-5, -4, -3, -2], median = (-4 + -3) / 2 = -3.5
        assert result == -3.5
    
    def test_mixed_sign_numbers(self):
        """Arrays with mixed positive and negative."""
        nums1 = [-1, 0, 1]
        nums2 = [-2, 2]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [-2, -1, 0, 1, 2], median = 0
        assert result == 0.0
    
    # Edge cases: duplicate elements
    def test_duplicate_elements(self):
        """Arrays contain duplicate elements."""
        nums1 = [1, 1, 1]
        nums2 = [1, 1]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [1, 1, 1, 1, 1], median = 1
        assert result == 1.0
    
    # Edge cases: large values
    def test_large_positive_values(self):
        """Arrays with large positive values."""
        nums1 = [1000000]
        nums2 = [999999]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 999999.5
    
    def test_large_negative_values(self):
        """Arrays with large negative values."""
        nums1 = [-1000000]
        nums2 = [-999999]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == -999999.5
    
    # Edge cases: one array much larger
    def test_first_array_much_larger(self):
        """First array is much larger than second."""
        nums1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        nums2 = [5]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [1, 2, 3, 4, 5, 5, 6, 7, 8, 9, 10], median = 5
        assert result == 5.0
    
    def test_second_array_much_larger(self):
        """Second array is much larger than first."""
        nums1 = [5]
        nums2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [1, 2, 3, 4, 5, 5, 6, 7, 8, 9, 10], median = 5
        assert result == 5.0
    
    # Correctness tests with various sizes
    def test_equal_size_arrays(self):
        """Arrays of equal size."""
        nums1 = [1, 3, 5]
        nums2 = [2, 4, 6]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [1, 2, 3, 4, 5, 6], median = (3 + 4) / 2 = 3.5
        assert result == 3.5
    
    def test_no_overlap(self):
        """Arrays with no overlapping values."""
        nums1 = [1, 2, 3]
        nums2 = [4, 5, 6]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [1, 2, 3, 4, 5, 6], median = (3 + 4) / 2 = 3.5
        assert result == 3.5
    
    def test_complete_overlap(self):
        """Arrays with complete value overlap."""
        nums1 = [1, 2, 3]
        nums2 = [1, 2, 3]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [1, 1, 2, 2, 3, 3], median = (2 + 2) / 2 = 2.0
        assert result == 2.0
    
    def test_interleaved_arrays(self):
        """Arrays that interleave perfectly."""
        nums1 = [1, 3, 5, 7]
        nums2 = [2, 4, 6, 8]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [1, 2, 3, 4, 5, 6, 7, 8], median = (4 + 5) / 2 = 4.5
        assert result == 4.5
    
    # Efficiency test: O(log(m+n)) requirement
    def test_efficiency_large_arrays(self):
        """Test that solution runs in O(log(m+n)) time with large arrays."""
        # Create large sorted arrays
        nums1 = list(range(0, 2000, 2))  # 1000 elements
        nums2 = list(range(1, 2000, 2))  # 1000 elements
        
        start_time = time.time()
        result = findMedianSortedArrays(nums1, nums2)
        elapsed = time.time() - start_time
        
        # O(log(m+n)) should be very fast even for 2000 elements
        # Allow generous 1 second threshold to reject only O(n²) approaches
        assert elapsed < 1.0, f"Function took {elapsed}s, expected O(log(m+n))"
        
        # Verify correctness: merged array is [0, 1, 2, ..., 1999]
        # median of 2000 elements is (999 + 1000) / 2 = 999.5
        assert result == 999.5
    
    def test_efficiency_maximum_size(self):
        """Test with maximum constraint size (m+n = 2000)."""
        nums1 = list(range(1000))  # 1000 elements
        nums2 = list(range(1000, 2000))  # 1000 elements
        
        start_time = time.time()
        result = findMedianSortedArrays(nums1, nums2)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"Function took {elapsed}s"
        # merged: [0, 1, ..., 1999], median = (999 + 1000) / 2 = 999.5
        assert result == 999.5
    
    # Additional correctness edge cases
    def test_single_combined_element(self):
        """Only one element total across both arrays."""
        nums1 = []
        nums2 = [42]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 42.0
    
    def test_two_combined_elements_first_smaller(self):
        """Two elements total, first array has smaller."""
        nums1 = [1]
        nums2 = [3]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 2.0
    
    def test_two_combined_elements_second_smaller(self):
        """Two elements total, second array has smaller."""
        nums1 = [3]
        nums2 = [1]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 2.0
    
    def test_zero_values(self):
        """Arrays containing zeros."""
        nums1 = [0]
        nums2 = [0]
        result = findMedianSortedArrays(nums1, nums2)
        assert result == 0.0
    
    def test_zero_with_positive(self):
        """Mix of zero and positive values."""
        nums1 = [0, 1]
        nums2 = [0, 1]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [0, 0, 1, 1], median = (0 + 1) / 2 = 0.5
        assert result == 0.5
    
    def test_zero_with_negative(self):
        """Mix of zero and negative values."""
        nums1 = [-1, 0]
        nums2 = [-1, 0]
        result = findMedianSortedArrays(nums1, nums2)
        # merged: [-1, -1, 0, 0], median = (-1 + 0) / 2 = -0.5
        assert result == -0.5


# Standalone test functions for parametrized testing
@pytest.mark.parametrize("nums1,nums2,expected", [
    ([1, 3], [2], 2.0),
    ([1, 2], [3, 4], 2.5),
    ([], [1], 1.0),
    ([1], [], 1.0),
    ([1], [2], 1.5),
    ([1, 2, 3], [4, 5, 6], 3.5),
    ([-2, -1], [-3, 0], -1.5),
    ([0], [0], 0.0),
])
def test_findMedianSortedArrays_parametrized(nums1, nums2, expected):
    """Parametrized tests for various inputs."""
    result = findMedianSortedArrays(nums1, nums2)
    assert result == expected