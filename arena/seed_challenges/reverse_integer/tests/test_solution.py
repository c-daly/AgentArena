import pytest
import time
from solution import *


class TestReverseInteger:
    """Test suite for the reverse integer problem."""
    
    # Basic correctness tests from examples
    def test_example_1_positive(self):
        """Test reversing positive integer 123 -> 321"""
        assert reverse(123) == 321
    
    def test_example_2_negative(self):
        """Test reversing negative integer -123 -> -321"""
        assert reverse(-123) == -321
    
    def test_example_3_trailing_zeros(self):
        """Test reversing integer with trailing zeros 120 -> 21"""
        assert reverse(120) == 21
    
    # Edge cases with single digits
    def test_single_digit_positive(self):
        """Test single digit positive number"""
        assert reverse(5) == 5
    
    def test_single_digit_negative(self):
        """Test single digit negative number"""
        assert reverse(-5) == -5
    
    def test_zero(self):
        """Test zero"""
        assert reverse(0) == 0
    
    # Edge cases with multiple trailing zeros
    def test_multiple_trailing_zeros(self):
        """Test number with multiple trailing zeros"""
        assert reverse(1200) == 21
    
    def test_all_zeros_except_first(self):
        """Test number like 1000"""
        assert reverse(1000) == 1
    
    def test_negative_trailing_zeros(self):
        """Test negative number with trailing zeros"""
        assert reverse(-120) == -21
    
    # 32-bit integer boundary tests
    def test_max_32bit_integer(self):
        """Test maximum 32-bit signed integer 2^31 - 1 = 2147483647"""
        # Reversing 2147483647 gives 7463847412 which exceeds 2^31-1
        assert reverse(2147483647) == 0
    
    def test_min_32bit_integer(self):
        """Test minimum 32-bit signed integer -2^31 = -2147483648"""
        # Reversing -2147483648 gives -8463847412 which exceeds -2^31
        assert reverse(-2147483648) == 0
    
    def test_within_bounds_large_positive(self):
        """Test large positive number that stays within bounds"""
        # 1534236469 reversed is 9646324351 which exceeds bounds
        assert reverse(1534236469) == 0
    
    def test_within_bounds_large_negative(self):
        """Test large negative number that stays within bounds"""
        # -2147483648 reversed exceeds bounds
        assert reverse(-2147483648) == 0
    
    def test_large_positive_in_bounds(self):
        """Test large positive number that fits in bounds"""
        # 1000000003 -> 3000000001 which exceeds bounds
        assert reverse(1000000003) == 0
    
    def test_large_positive_safe(self):
        """Test large positive number that safely reverses"""
        # 1534236460 -> 0646324351 = 646324351
        result = reverse(1534236460)
        assert result == 646324351
    
    def test_large_negative_safe(self):
        """Test large negative number that safely reverses"""
        # -1534236460 -> -646324351
        result = reverse(-1534236460)
        assert result == -646324351
    
    # Additional correctness tests
    def test_two_digit_number(self):
        """Test two digit number"""
        assert reverse(12) == 21
    
    def test_two_digit_negative(self):
        """Test two digit negative number"""
        assert reverse(-12) == -21
    
    def test_palindrome_number(self):
        """Test palindromic number"""
        assert reverse(121) == 121
    
    def test_palindrome_negative(self):
        """Test negative palindromic number"""
        assert reverse(-121) == -121
    
    def test_number_ending_in_zero(self):
        """Test number ending in zero"""
        assert reverse(100) == 1
    
    def test_negative_ending_in_zero(self):
        """Test negative number ending in zero"""
        assert reverse(-100) == -1
    
    def test_medium_positive(self):
        """Test medium positive number"""
        assert reverse(12345) == 54321
    
    def test_medium_negative(self):
        """Test medium negative number"""
        assert reverse(-12345) == -54321
    
    def test_number_with_internal_zeros(self):
        """Test number with zeros in the middle"""
        assert reverse(1020) == 2010
    
    def test_negative_with_internal_zeros(self):
        """Test negative number with zeros in the middle"""
        assert reverse(-1020) == -2010
    
    # Efficiency test
    def test_efficiency_large_input(self):
        """Test that the function completes efficiently for large numbers"""
        start_time = time.time()
        
        # Test with multiple large numbers
        for _ in range(10000):
            reverse(1534236460)
            reverse(-1534236460)
            reverse(2147483647)
            reverse(-2147483648)
        
        elapsed_time = time.time() - start_time
        
        # Should complete in well under 1 second for 40000 operations
        # A correct O(log n) solution should be much faster
        assert elapsed_time < 1.0, f"Function took {elapsed_time}s, expected < 1.0s"
    
    def test_efficiency_boundary_cases(self):
        """Test efficiency with boundary case numbers"""
        start_time = time.time()
        
        # Test with numbers near boundaries
        test_numbers = [
            2147483647, -2147483648, 1534236469, -1534236469,
            1000000000, -1000000000, 999999999, -999999999
        ]
        
        for _ in range(1000):
            for num in test_numbers:
                reverse(num)
        
        elapsed_time = time.time() - start_time
        
        # 8000 operations should complete quickly
        assert elapsed_time < 0.5, f"Function took {elapsed_time}s, expected < 0.5s"
    
    # Type and constraint validation
    def test_constraint_lower_bound(self):
        """Test with minimum constraint value"""
        result = reverse(-2147483648)
        assert isinstance(result, int)
        assert -2147483648 <= result <= 2147483647 or result == 0
    
    def test_constraint_upper_bound(self):
        """Test with maximum constraint value"""
        result = reverse(2147483647)
        assert isinstance(result, int)
        assert -2147483648 <= result <= 2147483647 or result == 0
    
    def test_return_type_is_integer(self):
        """Verify return type is always integer"""
        assert isinstance(reverse(123), int)
        assert isinstance(reverse(-123), int)
        assert isinstance(reverse(0), int)
        assert isinstance(reverse(2147483647), int)