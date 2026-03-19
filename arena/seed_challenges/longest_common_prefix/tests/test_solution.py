import pytest
import time
from solution import *


class TestLongestCommonPrefix:
    """Test suite for longest common prefix function."""
    
    # Basic correctness tests from examples
    def test_example_1_flower_flow_flight(self):
        """Test with example 1: flower, flow, flight -> fl"""
        strs = ["flower", "flow", "flight"]
        assert longestCommonPrefix(strs) == "fl"
    
    def test_example_2_dog_racecar_car(self):
        """Test with example 2: dog, racecar, car -> empty string"""
        strs = ["dog", "racecar", "car"]
        assert longestCommonPrefix(strs) == ""
    
    # Edge cases - single element
    def test_single_string(self):
        """Test with single string - entire string is the prefix"""
        assert longestCommonPrefix(["hello"]) == "hello"
    
    def test_single_empty_string(self):
        """Test with single empty string"""
        assert longestCommonPrefix([""]) == ""
    
    # Edge cases - multiple identical strings
    def test_identical_strings(self):
        """Test with identical strings"""
        assert longestCommonPrefix(["abc", "abc", "abc"]) == "abc"
    
    # Edge cases - no common prefix
    def test_no_common_prefix_different_first_chars(self):
        """Test strings with different first characters"""
        assert longestCommonPrefix(["a", "b", "c"]) == ""
    
    def test_no_common_prefix_one_char_different(self):
        """Test strings that differ at first character"""
        assert longestCommonPrefix(["abc", "def", "ghi"]) == ""
    
    # Edge cases - one string is prefix of others
    def test_one_string_is_prefix_of_others(self):
        """Test when one string is a prefix of all others"""
        assert longestCommonPrefix(["a", "ab", "abc"]) == "a"
    
    def test_longer_prefix_is_prefix_of_others(self):
        """Test when longer string is prefix"""
        assert longestCommonPrefix(["abc", "abcd", "abcde"]) == "abc"
    
    # Edge cases - empty strings in array
    def test_empty_string_in_array(self):
        """Test with empty string in array - should return empty"""
        assert longestCommonPrefix(["abc", "", "abc"]) == ""
    
    def test_all_empty_strings(self):
        """Test with all empty strings"""
        assert longestCommonPrefix(["", "", ""]) == ""
    
    # Edge cases - two strings
    def test_two_strings_with_common_prefix(self):
        """Test with two strings having common prefix"""
        assert longestCommonPrefix(["hello", "help"]) == "hel"
    
    def test_two_strings_no_common_prefix(self):
        """Test with two strings having no common prefix"""
        assert longestCommonPrefix(["hello", "world"]) == ""
    
    def test_two_identical_strings(self):
        """Test with two identical strings"""
        assert longestCommonPrefix(["test", "test"]) == "test"
    
    # Edge cases - single character strings
    def test_single_character_strings_same(self):
        """Test with single character strings that are same"""
        assert longestCommonPrefix(["a", "a", "a"]) == "a"
    
    def test_single_character_strings_different(self):
        """Test with single character strings that are different"""
        assert longestCommonPrefix(["a", "b", "c"]) == ""
    
    # More complex cases
    def test_long_common_prefix(self):
        """Test with long common prefix"""
        strs = ["interspecies", "interstellar", "interstate"]
        assert longestCommonPrefix(strs) == "inters"
    
    def test_prefix_at_end_of_shorter_string(self):
        """Test when common prefix is entire shorter string"""
        assert longestCommonPrefix(["ab", "a"]) == "a"
    
    def test_multiple_strings_with_partial_match(self):
        """Test with multiple strings and partial match"""
        strs = ["prefix", "preface", "prepare"]
        assert longestCommonPrefix(strs) == "pre"
    
    def test_case_sensitive(self):
        """Test that comparison is case sensitive"""
        assert longestCommonPrefix(["Hello", "hello"]) == ""
    
    # Performance test
    def test_performance_large_input(self):
        """Test performance with large input - should complete in reasonable time"""
        # Create 200 strings of length 200 with common prefix
        common_prefix = "a" * 100
        strs = [common_prefix + "b" * (100 - i % 50) for i in range(200)]
        
        start_time = time.time()
        result = longestCommonPrefix(strs)
        elapsed = time.time() - start_time
        
        # Should complete in under 1 second for reasonable algorithms
        # Brute force O(n²) would be much slower
        assert elapsed < 1.0
        assert result == common_prefix
    
    def test_performance_many_strings_short_prefix(self):
        """Test performance with many strings and short common prefix"""
        # 200 strings with only 1 character common prefix
        strs = ["a" + chr(97 + (i % 26)) * 199 for i in range(200)]
        
        start_time = time.time()
        result = longestCommonPrefix(strs)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0
        assert result == "a"
    
    def test_performance_long_strings_no_common_prefix(self):
        """Test performance with long strings but no common prefix"""
        # Create strings that differ at first character
        strs = [chr(97 + (i % 26)) + "x" * 199 for i in range(200)]
        
        start_time = time.time()
        result = longestCommonPrefix(strs)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0
        assert result == ""
    
    # Boundary tests
    def test_max_length_strings(self):
        """Test with maximum length strings (200 chars)"""
        s = "a" * 200
        strs = [s, s, s]
        assert longestCommonPrefix(strs) == s
    
    def test_max_count_strings(self):
        """Test with maximum count of strings (200)"""
        strs = ["prefix" + str(i) for i in range(200)]
        # All start with "prefix"
        assert longestCommonPrefix(strs) == "prefix"
    
    def test_whitespace_not_present(self):
        """Verify that strings only contain lowercase letters"""
        # According to constraints, strings consist of only lowercase English letters
        strs = ["abc", "abd", "abe"]
        result = longestCommonPrefix(strs)
        assert result == "ab"
        # Verify result is lowercase
        assert result.islower() or result == ""
    
    # Additional edge cases
    def test_very_similar_strings(self):
        """Test with very similar strings"""
        strs = ["aaaa", "aaab", "aaac"]
        assert longestCommonPrefix(strs) == "aaa"
    
    def test_repeated_characters(self):
        """Test with repeated characters"""
        strs = ["aaaa", "aaaa", "aaaa"]
        assert longestCommonPrefix(strs) == "aaaa"
    
    def test_alternating_pattern(self):
        """Test with alternating pattern strings"""
        strs = ["ababab", "ababac", "ababba"]
        assert longestCommonPrefix(strs) == "abab"