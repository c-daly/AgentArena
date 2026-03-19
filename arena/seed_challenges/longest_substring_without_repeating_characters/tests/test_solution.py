import pytest
import time
from solution import *


class TestLengthOfLongestSubstring:
    """Test suite for longest substring without duplicate characters."""

    # Basic correctness tests from examples
    def test_example_1(self):
        """Test example 1: s = "abcabcbb" -> 3"""
        assert lengthOfLongestSubstring("abcabcbb") == 3

    def test_example_2(self):
        """Test example 2: s = "bbbbb" -> 1"""
        assert lengthOfLongestSubstring("bbbbb") == 1

    def test_example_3(self):
        """Test example 3: s = "pwwkew" -> 3"""
        assert lengthOfLongestSubstring("pwwkew") == 3

    # Edge cases
    def test_empty_string(self):
        """Test empty string."""
        assert lengthOfLongestSubstring("") == 0

    def test_single_character(self):
        """Test single character string."""
        assert lengthOfLongestSubstring("a") == 1

    def test_two_characters_same(self):
        """Test two identical characters."""
        assert lengthOfLongestSubstring("aa") == 1

    def test_two_characters_different(self):
        """Test two different characters."""
        assert lengthOfLongestSubstring("ab") == 2

    def test_all_unique_characters(self):
        """Test string with all unique characters."""
        assert lengthOfLongestSubstring("abcdefghij") == 10

    def test_all_same_characters(self):
        """Test string with all same characters."""
        assert lengthOfLongestSubstring("aaaaaaaaaa") == 1

    def test_duplicate_at_end(self):
        """Test duplicate character at the end."""
        assert lengthOfLongestSubstring("abcda") == 4

    def test_duplicate_at_start(self):
        """Test duplicate character at the start."""
        assert lengthOfLongestSubstring("aabcdef") == 6

    def test_longest_at_end(self):
        """Test longest substring at the end."""
        assert lengthOfLongestSubstring("aabcdefghij") == 10

    def test_longest_at_start(self):
        """Test longest substring at the start."""
        assert lengthOfLongestSubstring("abcdefghijaa") == 10

    def test_longest_in_middle(self):
        """Test longest substring in the middle."""
        assert lengthOfLongestSubstring("aabcdefghijaa") == 10

    def test_with_digits(self):
        """Test string with digits."""
        assert lengthOfLongestSubstring("a1b2c3a") == 7

    def test_with_special_characters(self):
        """Test string with special characters."""
        assert lengthOfLongestSubstring("a!b@c#a") == 7

    def test_with_spaces(self):
        """Test string with spaces."""
        assert lengthOfLongestSubstring("a b c a") == 4

    def test_repeated_pattern(self):
        """Test repeated pattern."""
        assert lengthOfLongestSubstring("abcabcabcabc") == 3

    def test_long_unique_followed_by_repeats(self):
        """Test long unique substring followed by repeats."""
        assert lengthOfLongestSubstring("abcdefghijklmnopqrstuvwxyzabc") == 26

    def test_single_repeat_in_long_string(self):
        """Test single repeated character in long string."""
        assert lengthOfLongestSubstring("abcdefghijklmnopqrstuvwxyza") == 26

    def test_alternating_pattern(self):
        """Test alternating pattern."""
        assert lengthOfLongestSubstring("ababab") == 2

    def test_complex_pattern(self):
        """Test complex pattern."""
        assert lengthOfLongestSubstring("dvdf") == 3

    def test_au_pattern(self):
        """Test 'au' pattern."""
        assert lengthOfLongestSubstring("au") == 2

    def test_aab_pattern(self):
        """Test 'aab' pattern."""
        assert lengthOfLongestSubstring("aab") == 2

    def test_abba_pattern(self):
        """Test 'abba' pattern."""
        assert lengthOfLongestSubstring("abba") == 2

    def test_tmmzuxt_pattern(self):
        """Test 'tmmzuxt' pattern."""
        assert lengthOfLongestSubstring("tmmzuxt") == 5

    # Performance test - should handle large inputs efficiently
    def test_large_input_performance(self):
        """Test performance with large input (50,000 characters)."""
        # Create a large string with repeating pattern
        # This should be solvable in O(n) time
        large_string = "a" * 25000 + "b" * 25000
        
        start_time = time.time()
        result = lengthOfLongestSubstring(large_string)
        elapsed_time = time.time() - start_time
        
        # Should complete in under 1 second for O(n) solution
        # Brute force O(n²) would likely take much longer
        assert elapsed_time < 1.0, f"Performance test failed: took {elapsed_time}s"
        assert result == 2

    def test_large_input_all_unique(self):
        """Test performance with large input of all unique characters."""
        # Create a large string with unique characters
        large_string = "".join(chr(i % 256) for i in range(50000))
        
        start_time = time.time()
        result = lengthOfLongestSubstring(large_string)
        elapsed_time = time.time() - start_time
        
        # Should complete in under 1 second for O(n) solution
        assert elapsed_time < 1.0, f"Performance test failed: took {elapsed_time}s"
        assert result == 256

    def test_large_input_worst_case(self):
        """Test performance with worst case scenario."""
        # Create a string where longest substring grows gradually
        large_string = "".join(chr(97 + (i % 26)) for i in range(50000))
        
        start_time = time.time()
        result = lengthOfLongestSubstring(large_string)
        elapsed_time = time.time() - start_time
        
        # Should complete in under 1 second for O(n) solution
        assert elapsed_time < 1.0, f"Performance test failed: took {elapsed_time}s"
        assert result == 26

    def test_max_constraint_length(self):
        """Test with maximum constraint length (5 * 10^4)."""
        # Create a string at the maximum constraint
        large_string = "a" * 50000
        
        start_time = time.time()
        result = lengthOfLongestSubstring(large_string)
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 1.0, f"Performance test failed: took {elapsed_time}s"
        assert result == 1

    # Additional edge cases
    def test_unicode_characters(self):
        """Test with unicode characters."""
        assert lengthOfLongestSubstring("αβγαβ") == 3

    def test_mixed_case_letters(self):
        """Test that case matters (uppercase and lowercase are different)."""
        assert lengthOfLongestSubstring("aAbBcC") == 6

    def test_numbers_as_strings(self):
        """Test numeric strings."""
        assert lengthOfLongestSubstring("123121") == 3

    def test_whitespace_characters(self):
        """Test with different whitespace."""
        assert lengthOfLongestSubstring("a b\tc\na") == 4