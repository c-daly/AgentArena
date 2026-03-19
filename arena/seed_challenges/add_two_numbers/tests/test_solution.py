import pytest
import time
from solution import *


# Helper function to create a linked list from a list
def create_linked_list(values):
    if not values:
        return None
    head = ListNode(values[0])
    current = head
    for val in values[1:]:
        current.next = ListNode(val)
        current = current.next
    return head


# Helper function to convert linked list to list for easy comparison
def linked_list_to_list(node):
    result = []
    current = node
    while current:
        result.append(current.val)
        current = current.next
    return result


class TestAddTwoNumbers:
    """Test suite for adding two numbers represented as linked lists"""

    # Basic correctness tests from problem examples
    def test_example_1(self):
        """Test: 342 + 465 = 807"""
        l1 = create_linked_list([2, 4, 3])
        l2 = create_linked_list([5, 6, 4])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [7, 0, 8]

    def test_example_2(self):
        """Test: 0 + 0 = 0"""
        l1 = create_linked_list([0])
        l2 = create_linked_list([0])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0]

    def test_example_3(self):
        """Test: 9999999 + 9999 = 10009998 (reversed: [8,9,9,9,0,0,0,1])"""
        l1 = create_linked_list([9, 9, 9, 9, 9, 9, 9])
        l2 = create_linked_list([9, 9, 9, 9])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [8, 9, 9, 9, 0, 0, 0, 1]

    # Edge cases: single digit numbers
    def test_single_digit_no_carry(self):
        """Test: 2 + 5 = 7"""
        l1 = create_linked_list([2])
        l2 = create_linked_list([5])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [7]

    def test_single_digit_with_carry(self):
        """Test: 5 + 5 = 10 (reversed: [0, 1])"""
        l1 = create_linked_list([5])
        l2 = create_linked_list([5])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0, 1]

    def test_single_digit_max(self):
        """Test: 9 + 9 = 18 (reversed: [8, 1])"""
        l1 = create_linked_list([9])
        l2 = create_linked_list([9])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [8, 1]

    # Edge cases: different lengths
    def test_different_lengths_shorter_first(self):
        """Test: 99 + 1 = 100 (reversed: [0, 0, 1])"""
        l1 = create_linked_list([9, 9])
        l2 = create_linked_list([1])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0, 0, 1]

    def test_different_lengths_longer_first(self):
        """Test: 1 + 99 = 100 (reversed: [0, 0, 1])"""
        l1 = create_linked_list([1])
        l2 = create_linked_list([9, 9])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0, 0, 1]

    def test_different_lengths_multiple_digits(self):
        """Test: 123 + 4567 = 4690 (reversed: [0, 9, 6, 4])"""
        l1 = create_linked_list([3, 2, 1])
        l2 = create_linked_list([7, 6, 5, 4])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0, 9, 6, 4]

    # Edge cases: all zeros except one
    def test_zero_plus_number(self):
        """Test: 0 + 123 = 123"""
        l1 = create_linked_list([0])
        l2 = create_linked_list([3, 2, 1])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [3, 2, 1]

    def test_number_plus_zero(self):
        """Test: 456 + 0 = 456"""
        l1 = create_linked_list([6, 5, 4])
        l2 = create_linked_list([0])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [6, 5, 4]

    # Edge cases: carry propagation
    def test_carry_propagation_simple(self):
        """Test: 19 + 1 = 20 (reversed: [0, 2])"""
        l1 = create_linked_list([9, 1])
        l2 = create_linked_list([1])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0, 2]

    def test_carry_propagation_multiple(self):
        """Test: 999 + 1 = 1000 (reversed: [0, 0, 0, 1])"""
        l1 = create_linked_list([9, 9, 9])
        l2 = create_linked_list([1])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0, 0, 0, 1]

    def test_carry_propagation_both_lists(self):
        """Test: 999 + 999 = 1998 (reversed: [8, 9, 9, 1])"""
        l1 = create_linked_list([9, 9, 9])
        l2 = create_linked_list([9, 9, 9])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [8, 9, 9, 1]

    # Edge cases: no carry needed
    def test_no_carry_needed(self):
        """Test: 123 + 456 = 579 (reversed: [9, 7, 5])"""
        l1 = create_linked_list([3, 2, 1])
        l2 = create_linked_list([6, 5, 4])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [9, 7, 5]

    # Edge cases: mixed carry and no carry
    def test_mixed_carry_and_no_carry(self):
        """Test: 1234 + 5678 = 6912 (reversed: [2, 1, 9, 6])"""
        l1 = create_linked_list([4, 3, 2, 1])
        l2 = create_linked_list([8, 7, 6, 5])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [2, 1, 9, 6]

    # Edge cases: maximum single digit values
    def test_max_digits_no_carry(self):
        """Test: 9 + 0 = 9"""
        l1 = create_linked_list([9])
        l2 = create_linked_list([0])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [9]

    def test_max_digits_with_carry(self):
        """Test: 9 + 1 = 10 (reversed: [0, 1])"""
        l1 = create_linked_list([9])
        l2 = create_linked_list([1])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0, 1]

    # Edge cases: equal length lists
    def test_equal_length_lists(self):
        """Test: 12 + 34 = 46 (reversed: [6, 4])"""
        l1 = create_linked_list([2, 1])
        l2 = create_linked_list([4, 3])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [6, 4]

    # Edge cases: long lists
    def test_long_lists_no_carry(self):
        """Test with longer lists without carry"""
        l1 = create_linked_list([1, 2, 3, 4, 5])
        l2 = create_linked_list([1, 2, 3, 4, 5])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [2, 4, 6, 8, 0, 1]

    def test_long_lists_with_carry(self):
        """Test with longer lists with carry"""
        l1 = create_linked_list([9, 9, 9, 9, 9])
        l2 = create_linked_list([1])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0, 0, 0, 0, 0, 1]

    # Efficiency test: large input
    def test_efficiency_large_input(self):
        """Test with large linked lists (near maximum constraint of 100 nodes)"""
        # Create two lists with 100 nodes each
        size = 100
        l1_values = [1] * size
        l2_values = [1] * size
        
        l1 = create_linked_list(l1_values)
        l2 = create_linked_list(l2_values)
        
        start_time = time.time()
        result = addTwoNumbers(l1, l2)
        elapsed_time = time.time() - start_time
        
        # Should complete in well under 1 second for a linear algorithm
        assert elapsed_time < 1.0, f"Function took {elapsed_time}s, expected < 1s"
        
        # Verify correctness: 111...1 (100 ones) + 111...1 (100 ones) = 222...2 (100 twos)
        result_list = linked_list_to_list(result)
        assert result_list == [2] * 100

    def test_efficiency_maximum_constraint(self):
        """Test at the maximum constraint boundary (100 nodes each)"""
        size = 100
        l1_values = [9] * size
        l2_values = [9] * size
        
        l1 = create_linked_list(l1_values)
        l2 = create_linked_list(l2_values)
        
        start_time = time.time()
        result = addTwoNumbers(l1, l2)
        elapsed_time = time.time() - start_time
        
        # Should complete in well under 1 second
        assert elapsed_time < 1.0, f"Function took {elapsed_time}s, expected < 1s"
        
        # Verify correctness: 999...9 + 999...9 = 888...8 with a leading 1
        result_list = linked_list_to_list(result)
        expected = [8] * 100 + [1]
        assert result_list == expected

    def test_efficiency_mixed_sizes(self):
        """Test with different sized lists near maximum"""
        l1_values = [5] * 100
        l2_values = [4] * 50
        
        l1 = create_linked_list(l1_values)
        l2 = create_linked_list(l2_values)
        
        start_time = time.time()
        result = addTwoNumbers(l1, l2)
        elapsed_time = time.time() - start_time
        
        # Should complete in well under 1 second
        assert elapsed_time < 1.0, f"Function took {elapsed_time}s, expected < 1s"
        
        # Verify result has correct length
        result_list = linked_list_to_list(result)
        assert len(result_list) == 100

    # Stress test: alternating carries
    def test_alternating_carries(self):
        """Test with pattern that creates alternating carries"""
        l1 = create_linked_list([5, 5, 5, 5, 5])
        l2 = create_linked_list([5, 5, 5, 5, 5])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0, 1, 1, 1, 1, 1]

    # Stress test: zero in middle
    def test_zero_in_middle(self):
        """Test with zeros in the middle of the number"""
        l1 = create_linked_list([1, 0, 1])
        l2 = create_linked_list([2, 0, 2])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [3, 0, 3]

    # Stress test: complex carry chain
    def test_complex_carry_chain(self):
        """Test with complex carry chain"""
        l1 = create_linked_list([9, 9, 9, 9])
        l2 = create_linked_list([9, 9, 9, 9])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [8, 9, 9, 9, 1]

    # Boundary test: constraint minimum
    def test_constraint_minimum(self):
        """Test with minimum constraint (1 node each)"""
        l1 = create_linked_list([0])
        l2 = create_linked_list([0])
        result = addTwoNumbers(l1, l2)
        assert linked_list_to_list(result) == [0]

    # Boundary test: constraint maximum
    def test_constraint_maximum(self):
        """Test with maximum constraint (100 nodes each)"""
        l1 = create_linked_list([1] * 100)
        l2 = create_linked_list([2] * 100)
        result = addTwoNumbers(l1, l2)
        result_list = linked_list_to_list(result)
        assert len(result_list) == 100
        assert result_list[0] == 3  # 1 + 2 = 3 in first position