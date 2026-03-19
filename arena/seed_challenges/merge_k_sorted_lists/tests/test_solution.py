import pytest
import time
from typing import Optional, List
from solution import mergeKLists


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def list_to_array(node: Optional[ListNode]) -> List[int]:
    """Convert a linked list to an array for easy comparison."""
    result = []
    current = node
    while current:
        result.append(current.val)
        current = current.next
    return result


def array_to_list(arr: List[int]) -> Optional[ListNode]:
    """Convert an array to a linked list."""
    if not arr:
        return None
    head = ListNode(arr[0])
    current = head
    for val in arr[1:]:
        current.next = ListNode(val)
        current = current.next
    return head


class TestMergeKLists:
    """Test suite for merging k sorted linked lists."""

    def test_example_1(self):
        """Test with the first example from the problem."""
        lists = [
            array_to_list([1, 4, 5]),
            array_to_list([1, 3, 4]),
            array_to_list([2, 6])
        ]
        result = mergeKLists(lists)
        assert list_to_array(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2(self):
        """Test with empty list of lists."""
        lists = []
        result = mergeKLists(lists)
        assert result is None

    def test_example_3(self):
        """Test with list containing one empty list."""
        lists = [None]
        result = mergeKLists(lists)
        assert result is None

    def test_single_list_single_element(self):
        """Test with a single list containing one element."""
        lists = [array_to_list([1])]
        result = mergeKLists(lists)
        assert list_to_array(result) == [1]

    def test_single_list_multiple_elements(self):
        """Test with a single list containing multiple elements."""
        lists = [array_to_list([1, 2, 3, 4, 5])]
        result = mergeKLists(lists)
        assert list_to_array(result) == [1, 2, 3, 4, 5]

    def test_multiple_empty_lists(self):
        """Test with multiple empty lists."""
        lists = [None, None, None]
        result = mergeKLists(lists)
        assert result is None

    def test_mixed_empty_and_non_empty(self):
        """Test with a mix of empty and non-empty lists."""
        lists = [
            None,
            array_to_list([1, 3]),
            None,
            array_to_list([2, 4])
        ]
        result = mergeKLists(lists)
        assert list_to_array(result) == [1, 2, 3, 4]

    def test_two_lists(self):
        """Test merging two sorted lists."""
        lists = [
            array_to_list([1, 3, 5]),
            array_to_list([2, 4, 6])
        ]
        result = mergeKLists(lists)
        assert list_to_array(result) == [1, 2, 3, 4, 5, 6]

    def test_lists_with_duplicates(self):
        """Test lists with duplicate values."""
        lists = [
            array_to_list([1, 1, 1]),
            array_to_list([1, 1, 1]),
            array_to_list([1, 1, 1])
        ]
        result = mergeKLists(lists)
        assert list_to_array(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_negative_values(self):
        """Test with negative values."""
        lists = [
            array_to_list([-5, -2, 0]),
            array_to_list([-4, -1, 3]),
            array_to_list([-3, 1, 2])
        ]
        result = mergeKLists(lists)
        assert list_to_array(result) == [-5, -4, -3, -2, -1, 0, 1, 2, 3]

    def test_large_negative_and_positive(self):
        """Test with extreme values within constraints."""
        lists = [
            array_to_list([-10000, -5000, 0]),
            array_to_list([-9999, 5000, 10000]),
            array_to_list([-1, 1, 9999])
        ]
        result = mergeKLists(lists)
        expected = [-10000, -9999, -5000, -1, 0, 1, 5000, 9999, 10000]
        assert list_to_array(result) == expected

    def test_unequal_length_lists(self):
        """Test with lists of very different lengths."""
        lists = [
            array_to_list([1]),
            array_to_list([2, 3, 4, 5, 6, 7, 8, 9, 10]),
            array_to_list([11])
        ]
        result = mergeKLists(lists)
        assert list_to_array(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    def test_many_single_element_lists(self):
        """Test with many lists each containing a single element."""
        lists = [array_to_list([i]) for i in range(1, 11)]
        result = mergeKLists(lists)
        assert list_to_array(result) == list(range(1, 11))

    def test_already_sorted_order(self):
        """Test when lists are already in sorted order."""
        lists = [
            array_to_list([1, 2, 3]),
            array_to_list([4, 5, 6]),
            array_to_list([7, 8, 9])
        ]
        result = mergeKLists(lists)
        assert list_to_array(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_reverse_sorted_lists(self):
        """Test when lists are in reverse order of their values."""
        lists = [
            array_to_list([7, 8, 9]),
            array_to_list([4, 5, 6]),
            array_to_list([1, 2, 3])
        ]
        result = mergeKLists(lists)
        assert list_to_array(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_interleaved_values(self):
        """Test with interleaved values across lists."""
        lists = [
            array_to_list([1, 4, 7]),
            array_to_list([2, 5, 8]),
            array_to_list([3, 6, 9])
        ]
        result = mergeKLists(lists)
        assert list_to_array(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_efficiency_large_input(self):
        """Test efficiency with large input to ensure O(n log k) or better."""
        # Create k=100 lists, each with 100 elements
        k = 100
        elements_per_list = 100
        total_elements = k * elements_per_list
        
        lists = []
        for i in range(k):
            # Each list contains elements: i, i+k, i+2k, ...
            arr = [i + j * k for j in range(elements_per_list)]
            lists.append(array_to_list(arr))
        
        start_time = time.time()
        result = mergeKLists(lists)
        elapsed = time.time() - start_time
        
        # Verify correctness
        result_array = list_to_array(result)
        assert len(result_array) == total_elements
        assert result_array == sorted(result_array)
        
        # Assert efficiency: should complete in reasonable time
        # O(n log k) where n = total_elements, k = number of lists
        # For n=10000, k=100: should be very fast (< 1 second)
        assert elapsed < 1.0, f"Efficiency test failed: took {elapsed:.3f}s"

    def test_efficiency_many_lists(self):
        """Test efficiency with many lists to ensure good heap performance."""
        # Create k=1000 lists with 10 elements each
        k = 1000
        elements_per_list = 10
        total_elements = k * elements_per_list
        
        lists = []
        for i in range(k):
            arr = list(range(i, i + elements_per_list * k, k))
            lists.append(array_to_list(arr))
        
        start_time = time.time()
        result = mergeKLists(lists)
        elapsed = time.time() - start_time
        
        # Verify correctness
        result_array = list_to_array(result)
        assert len(result_array) == total_elements
        assert result_array == sorted(result_array)
        
        # Should complete in reasonable time
        assert elapsed < 2.0, f"Efficiency test failed: took {elapsed:.3f}s"

    def test_efficiency_long_lists(self):
        """Test efficiency with fewer but longer lists."""
        # Create k=10 lists with 1000 elements each
        k = 10
        elements_per_list = 1000
        total_elements = k * elements_per_list
        
        lists = []
        for i in range(k):
            arr = list(range(i, i + elements_per_list * k, k))
            lists.append(array_to_list(arr))
        
        start_time = time.time()
        result = mergeKLists(lists)
        elapsed = time.time() - start_time
        
        # Verify correctness
        result_array = list_to_array(result)
        assert len(result_array) == total_elements
        assert result_array == sorted(result_array)
        
        # Should complete very quickly
        assert elapsed < 1.0, f"Efficiency test failed: took {elapsed:.3f}s"

    def test_result_is_sorted(self):
        """Verify that the result is always sorted."""
        lists = [
            array_to_list([5, 10, 15]),
            array_to_list([1, 11, 20]),
            array_to_list([3, 7, 12])
        ]
        result = mergeKLists(lists)
        result_array = list_to_array(result)
        assert result_array == sorted(result_array)

    def test_all_elements_preserved(self):
        """Verify that all elements are preserved in the merge."""
        lists = [
            array_to_list([1, 4, 5]),
            array_to_list([1, 3, 4]),
            array_to_list([2, 6])
        ]
        result = mergeKLists(lists)
        result_array = list_to_array(result)
        
        # Count elements
        expected_count = 3 + 3 + 2
        assert len(result_array) == expected_count
        
        # Verify all original elements are present
        original_elements = [1, 4, 5, 1, 3, 4, 2, 6]
        assert sorted(result_array) == sorted(original_elements)