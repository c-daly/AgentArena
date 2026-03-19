import pytest
import time
from solution import *


class TestLongestPalindrome:
    """Test suite for longest palindromic substring problem."""

    # Basic correctness tests from examples
    def test_example1_babad(self):
        """Test with example 1: 'babad'."""
        result = longestPalindrome("babad")
        assert result in ["bab", "aba"]
        assert len(result) == 3
        assert result == result[::-1]  # Verify it's a palindrome

    def test_example2_cbbd(self):
        """Test with example 2: 'cbbd'."""
        result = longestPalindrome("cbbd")
        assert result == "bb"
        assert result == result[::-1]

    # Edge cases
    def test_single_character(self):
        """Test with single character."""
        result = longestPalindrome("a")
        assert result == "a"

    def test_two_same_characters(self):
        """Test with two identical characters."""
        result = longestPalindrome("aa")
        assert result == "aa"

    def test_two_different_characters(self):
        """Test with two different characters."""
        result = longestPalindrome("ab")
        assert result in ["a", "b"]
        assert len(result) == 1

    def test_entire_string_is_palindrome(self):
        """Test when entire string is a palindrome."""
        result = longestPalindrome("racecar")
        assert result == "racecar"

    def test_entire_string_is_palindrome_even_length(self):
        """Test when entire string is a palindrome with even length."""
        result = longestPalindrome("abba")
        assert result == "abba"

    def test_no_palindrome_longer_than_one(self):
        """Test when no palindrome longer than single character exists."""
        result = longestPalindrome("abcdef")
        assert len(result) == 1
        assert result in ["a", "b", "c", "d", "e", "f"]

    def test_palindrome_at_start(self):
        """Test when longest palindrome is at the start."""
        result = longestPalindrome("abaxyz")
        assert result == "aba"

    def test_palindrome_at_end(self):
        """Test when longest palindrome is at the end."""
        result = longestPalindrome("xyzaba")
        assert result == "aba"

    def test_palindrome_in_middle(self):
        """Test when longest palindrome is in the middle."""
        result = longestPalindrome("xabay")
        assert result == "aba"

    def test_multiple_palindromes_same_length(self):
        """Test when multiple palindromes of same length exist."""
        result = longestPalindrome("abaxyz")
        assert len(result) == 3
        assert result == result[::-1]

    def test_odd_length_palindrome(self):
        """Test odd-length palindrome."""
        result = longestPalindrome("abcba")
        assert result == "abcba"

    def test_even_length_palindrome(self):
        """Test even-length palindrome."""
        result = longestPalindrome("abccba")
        assert result == "abccba"

    def test_nested_palindromes(self):
        """Test string with nested palindromes."""
        result = longestPalindrome("abacabad")
        # "abacaba" is the longest palindrome
        assert len(result) >= 7
        assert result == result[::-1]

    def test_repeated_characters(self):
        """Test with repeated characters."""
        result = longestPalindrome("aaaa")
        assert result == "aaaa"

    def test_repeated_pattern(self):
        """Test with repeated pattern."""
        result = longestPalindrome("ababab")
        assert len(result) >= 5
        assert result == result[::-1]

    def test_digits_only(self):
        """Test with digits only."""
        result = longestPalindrome("12321")
        assert result == "12321"

    def test_mixed_alphanumeric(self):
        """Test with mixed alphanumeric characters."""
        result = longestPalindrome("a1b1a")
        assert result == "a1b1a"

    def test_case_sensitive(self):
        """Test that function is case-sensitive."""
        result = longestPalindrome("Aa")
        assert len(result) == 1

    def test_long_string_with_palindrome_at_end(self):
        """Test longer string with palindrome at the end."""
        s = "abcdefghijklmnopqrstuvwxyzzyxwvutsrqponmlkjihgfedcba"
        result = longestPalindrome(s)
        assert result == result[::-1]
        assert len(result) >= 26

    def test_result_is_palindrome(self):
        """Verify that result is always a palindrome."""
        test_strings = [
            "babad",
            "cbbd",
            "racecar",
            "abcdef",
            "xyzzyxabc",
            "12345654321",
        ]
        for s in test_strings:
            result = longestPalindrome(s)
            assert result == result[::-1], f"Result '{result}' is not a palindrome for input '{s}'"

    def test_result_is_substring(self):
        """Verify that result is a substring of input."""
        test_strings = [
            "babad",
            "cbbd",
            "racecar",
            "abcdef",
            "xyzzyxabc",
        ]
        for s in test_strings:
            result = longestPalindrome(s)
            assert result in s, f"Result '{result}' is not a substring of '{s}'"

    # Efficiency test
    def test_efficiency_large_input(self):
        """Test that solution handles large input efficiently (O(n) or O(n log n))."""
        # Create a large string with a palindrome in the middle
        n = 1000
        s = "a" * (n // 2) + "b" + "a" * (n // 2)
        
        start_time = time.time()
        result = longestPalindrome(s)
        elapsed = time.time() - start_time
        
        # Should complete in well under 1 second for O(n) or O(n log n) solution
        # Brute force O(n²) or worse would likely exceed this for n=1000
        assert elapsed < 1.0, f"Solution took {elapsed:.3f}s, likely too slow"
        assert result == result[::-1]
        assert len(result) >= n // 2

    def test_efficiency_worst_case_palindrome(self):
        """Test efficiency with worst-case palindrome."""
        # Entire string is a palindrome
        n = 1000
        s = "a" * (n // 2) + "b" + "a" * (n // 2)
        
        start_time = time.time()
        result = longestPalindrome(s)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"Solution took {elapsed:.3f}s"
        assert result == s

    def test_efficiency_no_palindrome(self):
        """Test efficiency when no long palindrome exists."""
        # String with no palindromes longer than 1
        n = 1000
        s = "".join(chr(ord('a') + (i % 26)) for i in range(n))
        
        start_time = time.time()
        result = longestPalindrome(s)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"Solution took {elapsed:.3f}s"
        assert len(result) == 1
        assert result == result[::-1]

    def test_efficiency_many_palindromes(self):
        """Test efficiency with many overlapping palindromes."""
        n = 1000
        # Create string with repeating pattern that has many palindromes
        s = "aba" * (n // 3)
        
        start_time = time.time()
        result = longestPalindrome(s)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"Solution took {elapsed:.3f}s"
        assert result == result[::-1]
        assert len(result) >= 3

    def test_maximum_constraint_length(self):
        """Test with maximum constraint length (1000)."""
        s = "a" * 500 + "b" + "a" * 500
        result = longestPalindrome(s)
        assert result == s
        assert len(result) == 1001

    def test_palindrome_with_special_pattern(self):
        """Test palindrome with alternating pattern."""
        s = "ababababa"
        result = longestPalindrome(s)
        assert result == result[::-1]
        assert len(result) >= 5

    def test_single_char_repeated_odd(self):
        """Test single character repeated odd number of times."""
        result = longestPalindrome("aaaaa")
        assert result == "aaaaa"

    def test_single_char_repeated_even(self):
        """Test single character repeated even number of times."""
        result = longestPalindrome("aaaa")
        assert result == "aaaa"

    def test_complex_nested_structure(self):
        """Test complex nested palindrome structure."""
        s = "abacabaxyz"
        result = longestPalindrome(s)
        assert result == result[::-1]
        assert result in s
        assert len(result) >= 7