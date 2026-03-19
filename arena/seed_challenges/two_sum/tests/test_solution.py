import pytest
import time
from solution import twoSum


class TestTwoSum:
    """Comprehensive test suite for the Two Sum problem."""

    # ==================== Basic Correctness Tests ====================
    def test_example_1(self):
        """Test Example 1: nums = [2,7,11,15], target = 9"""
        nums = [2, 7, 11, 15]
        target = 9
        result = twoSum(nums, target)
        assert sorted(result) == [0, 1]
        assert nums[result[0]] + nums[result[1]] == target

    def test_example_2(self):
        """Test Example 2: nums = [3,2,4], target = 6"""
        nums = [3, 2, 4]
        target = 6
        result = twoSum(nums, target)
        assert sorted(result) == [1, 2]
        assert nums[result[0]] + nums[result[1]] == target

    def test_example_3(self):
        """Test Example 3: nums = [3,3], target = 6"""
        nums = [3, 3]
        target = 6
        result = twoSum(nums, target)
        assert sorted(result) == [0, 1]
        assert nums[result[0]] + nums[result[1]] == target

    # ==================== Edge Cases ====================
    def test_minimum_length_array(self):
        """Test with minimum array length (2 elements)."""
        nums = [1, 2]
        target = 3
        result = twoSum(nums, target)
        assert sorted(result) == [0, 1]
        assert nums[result[0]] + nums[result[1]] == target

    def test_negative_numbers(self):
        """Test with negative numbers."""
        nums = [-1, -2, -3, 5, 10]
        target = 7
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_all_negative_numbers(self):
        """Test with all negative numbers."""
        nums = [-10, -5, -3, -1]
        target = -15
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_zero_in_array(self):
        """Test with zero in the array."""
        nums = [0, 5, 10]
        target = 5
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_zero_target(self):
        """Test with target = 0."""
        nums = [-5, 5, 10]
        target = 0
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_duplicate_values_different_indices(self):
        """Test with duplicate values at different indices."""
        nums = [1, 1, 1, 2, 3]
        target = 2
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target
        assert result[0] != result[1]

    def test_large_positive_numbers(self):
        """Test with large positive numbers."""
        nums = [1000000000, 500000000, 1]
        target = 1500000000
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_large_negative_numbers(self):
        """Test with large negative numbers."""
        nums = [-1000000000, -500000000, -1]
        target = -1500000000
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_mixed_large_values(self):
        """Test with mixed large positive and negative values."""
        nums = [-1000000000, 1000000000, 5]
        target = 0
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_solution_at_boundaries(self):
        """Test where solution involves first and last elements."""
        nums = [1, 2, 3, 4, 5]
        target = 6
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_solution_at_start(self):
        """Test where solution involves first two elements."""
        nums = [1, 2, 100, 200]
        target = 3
        result = twoSum(nums, target)
        assert sorted(result) == [0, 1]

    def test_solution_at_end(self):
        """Test where solution involves last two elements."""
        nums = [100, 200, 1, 2]
        target = 3
        result = twoSum(nums, target)
        assert sorted(result) == [2, 3]

    # ==================== Return Value Validation ====================
    def test_return_type_is_list(self):
        """Verify return type is a list."""
        nums = [2, 7, 11, 15]
        target = 9
        result = twoSum(nums, target)
        assert isinstance(result, list)

    def test_return_length_is_two(self):
        """Verify return value has exactly 2 elements."""
        nums = [2, 7, 11, 15]
        target = 9
        result = twoSum(nums, target)
        assert len(result) == 2

    def test_return_indices_are_integers(self):
        """Verify returned indices are integers."""
        nums = [2, 7, 11, 15]
        target = 9
        result = twoSum(nums, target)
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)

    def test_return_indices_are_valid(self):
        """Verify returned indices are within valid range."""
        nums = [2, 7, 11, 15]
        target = 9
        result = twoSum(nums, target)
        assert 0 <= result[0] < len(nums)
        assert 0 <= result[1] < len(nums)

    def test_return_indices_are_different(self):
        """Verify returned indices are different (not using same element twice)."""
        nums = [2, 7, 11, 15]
        target = 9
        result = twoSum(nums, target)
        assert result[0] != result[1]

    # ==================== Efficiency Tests ====================
    def test_efficiency_large_array_1000_elements(self):
        """Test efficiency with 1000 elements - should complete in < 100ms."""
        nums = list(range(1000))
        target = 1998  # Last two elements
        
        start_time = time.time()
        result = twoSum(nums, target)
        elapsed = time.time() - start_time
        
        assert nums[result[0]] + nums[result[1]] == target
        assert elapsed < 0.1, f"Function took {elapsed:.4f}s, expected < 0.1s"

    def test_efficiency_large_array_10000_elements(self):
        """Test efficiency with 10000 elements - should complete in < 500ms."""
        nums = list(range(10000))
        target = 19998  # Last two elements
        
        start_time = time.time()
        result = twoSum(nums, target)
        elapsed = time.time() - start_time
        
        assert nums[result[0]] + nums[result[1]] == target
        assert elapsed < 0.5, f"Function took {elapsed:.4f}s, expected < 0.5s"

    def test_efficiency_large_array_with_negatives(self):
        """Test efficiency with 10000 elements including negatives."""
        nums = list(range(-5000, 5000))
        target = 9998  # Two large numbers
        
        start_time = time.time()
        result = twoSum(nums, target)
        elapsed = time.time() - start_time
        
        assert nums[result[0]] + nums[result[1]] == target
        assert elapsed < 0.5, f"Function took {elapsed:.4f}s, expected < 0.5s"

    def test_efficiency_random_large_array(self):
        """Test efficiency with random large array."""
        import random
        random.seed(42)
        nums = [random.randint(-1000000, 1000000) for _ in range(5000)]
        # Ensure a valid solution exists
        nums[0] = 100
        nums[1] = 200
        target = 300
        
        start_time = time.time()
        result = twoSum(nums, target)
        elapsed = time.time() - start_time
        
        assert nums[result[0]] + nums[result[1]] == target
        assert elapsed < 0.5, f"Function took {elapsed:.4f}s, expected < 0.5s"

    # ==================== Additional Corner Cases ====================
    def test_solution_with_one_negative_one_positive(self):
        """Test solution with one negative and one positive number."""
        nums = [-100, 50, 100]
        target = 0
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_array_with_repeated_target_sum_pairs(self):
        """Test array where multiple pairs could sum to target (but only one is valid)."""
        nums = [1, 2, 3, 4, 5]
        target = 5
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_very_small_numbers(self):
        """Test with very small numbers."""
        nums = [1, 2]
        target = 3
        result = twoSum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_order_independence(self):
        """Test that result is valid regardless of order."""
        nums = [2, 7, 11, 15]
        target = 9
        result = twoSum(nums, target)
        # Verify both orderings work
        assert (nums[result[0]] + nums[result[1]] == target)
        assert (nums[result[1]] + nums[result[0]] == target)