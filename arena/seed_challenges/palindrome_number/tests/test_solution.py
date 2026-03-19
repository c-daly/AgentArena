import pytest
import time
from solution import *


class TestIsPalindrome:
    """Test suite for integer palindrome checker"""

    # Basic correctness tests from examples
    def test_example_1_positive_palindrome(self):
        """Test case from Example 1: 121 is a palindrome"""
        assert isPalindrome(121) is True

    def test_example_2_negative_number(self):
        """Test case from Example 2: -121 is not a palindrome"""
        assert isPalindrome(-121) is False

    def test_example_3_trailing_zero(self):
        """Test case from Example 3: 10 is not a palindrome"""
        assert isPalindrome(10) is False

    # Edge cases with single digits
    def test_single_digit_zero(self):
        """Single digit 0 is a palindrome"""
        assert isPalindrome(0) is True

    def test_single_digit_positive(self):
        """Single digit positive numbers are palindromes"""
        assert isPalindrome(5) is True
        assert isPalindrome(9) is True

    def test_single_digit_negative(self):
        """Single digit negative numbers are not palindromes"""
        assert isPalindrome(-5) is False
        assert isPalindrome(-9) is False

    # Two digit numbers
    def test_two_digit_palindrome(self):
        """Two digit palindromes"""
        assert isPalindrome(11) is True
        assert isPalindrome(22) is True
        assert isPalindrome(99) is True

    def test_two_digit_non_palindrome(self):
        """Two digit non-palindromes"""
        assert isPalindrome(12) is False
        assert isPalindrome(23) is False
        assert isPalindrome(90) is False

    # Three digit numbers
    def test_three_digit_palindrome(self):
        """Three digit palindromes"""
        assert isPalindrome(101) is True
        assert isPalindrome(111) is True
        assert isPalindrome(191) is True
        assert isPalindrome(999) is True

    def test_three_digit_non_palindrome(self):
        """Three digit non-palindromes"""
        assert isPalindrome(123) is False
        assert isPalindrome(100) is False
        assert isPalindrome(102) is False

    # Larger palindromes
    def test_four_digit_palindrome(self):
        """Four digit palindromes"""
        assert isPalindrome(1001) is True
        assert isPalindrome(1221) is True
        assert isPalindrome(9999) is True

    def test_four_digit_non_palindrome(self):
        """Four digit non-palindromes"""
        assert isPalindrome(1000) is False
        assert isPalindrome(1234) is False
        assert isPalindrome(1230) is False

    def test_five_digit_palindrome(self):
        """Five digit palindromes"""
        assert isPalindrome(10101) is True
        assert isPalindrome(12321) is True
        assert isPalindrome(99999) is True

    def test_five_digit_non_palindrome(self):
        """Five digit non-palindromes"""
        assert isPalindrome(10000) is False
        assert isPalindrome(12345) is False

    # Negative numbers (all should be False)
    def test_negative_palindromes(self):
        """Negative numbers are never palindromes due to minus sign"""
        assert isPalindrome(-1) is False
        assert isPalindrome(-11) is False
        assert isPalindrome(-121) is False
        assert isPalindrome(-1001) is False

    # Boundary values
    def test_max_32bit_int(self):
        """Test near max 32-bit signed integer"""
        assert isPalindrome(2147483647) is False

    def test_min_32bit_int(self):
        """Test near min 32-bit signed integer"""
        assert isPalindrome(-2147483648) is False

    def test_large_palindrome(self):
        """Test large palindrome numbers"""
        assert isPalindrome(1000000001) is True
        assert isPalindrome(123454321) is True
        assert isPalindrome(9876789) is True

    def test_large_non_palindrome(self):
        """Test large non-palindrome numbers"""
        assert isPalindrome(1000000002) is False
        assert isPalindrome(123456789) is False

    # Numbers with trailing zeros
    def test_numbers_with_trailing_zeros(self):
        """Numbers ending in 0 cannot be palindromes (except 0)"""
        assert isPalindrome(20) is False
        assert isPalindrome(100) is False
        assert isPalindrome(1000) is False
        assert isPalindrome(120) is False

    # Performance test - ensure O(log n) or O(n) solution, not O(n²)
    def test_performance_large_palindrome(self):
        """Performance test: should complete quickly for large numbers"""
        # Create a large palindrome number
        large_palindrome = 12345678987654321
        
        start_time = time.time()
        result = isPalindrome(large_palindrome)
        elapsed = time.time() - start_time
        
        assert result is True
        # Should complete in well under 1 second for efficient algorithm
        assert elapsed < 1.0, f"Function took {elapsed}s, expected < 1.0s"

    def test_performance_large_non_palindrome(self):
        """Performance test: should complete quickly for large non-palindromes"""
        large_non_palindrome = 12345678987654322
        
        start_time = time.time()
        result = isPalindrome(large_non_palindrome)
        elapsed = time.time() - start_time
        
        assert result is False
        assert elapsed < 1.0, f"Function took {elapsed}s, expected < 1.0s"

    def test_performance_many_checks(self):
        """Performance test: multiple checks should be fast"""
        test_numbers = [
            121, -121, 10, 0, 1, 11, 12, 101, 1001, 
            12321, 123321, 1234321, 12345654321
        ]
        
        start_time = time.time()
        for num in test_numbers:
            isPalindrome(num)
        elapsed = time.time() - start_time
        
        # Should handle many checks very quickly
        assert elapsed < 0.5, f"Function took {elapsed}s for {len(test_numbers)} checks"

    # Additional edge cases
    def test_repeated_digits(self):
        """Test numbers with all same digits"""
        assert isPalindrome(1) is True
        assert isPalindrome(11) is True
        assert isPalindrome(111) is True
        assert isPalindrome(1111) is True
        assert isPalindrome(11111) is True

    def test_alternating_pattern(self):
        """Test numbers with alternating patterns"""
        assert isPalindrome(1212121) is True
        assert isPalindrome(121212) is False
        assert isPalindrome(12121) is True

    def test_zero_in_middle(self):
        """Test palindromes with zero in the middle"""
        assert isPalindrome(101) is True
        assert isPalindrome(1001) is True
        assert isPalindrome(10001) is True
        assert isPalindrome(100001) is True