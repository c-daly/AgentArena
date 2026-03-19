import pytest
import time
from solution import *


class TestRegexMatching:
    """Test suite for regular expression matching with '.' and '*'"""

    # ===== Basic Correctness Tests =====
    def test_example_1_no_match(self):
        """Example 1: "aa" does not match "a" """
        assert isMatch("aa", "a") == False

    def test_example_2_star_match(self):
        """Example 2: "aa" matches "a*" """
        assert isMatch("aa", "a*") == True

    def test_example_3_dot_star_match(self):
        """Example 3: "ab" matches ".*" """
        assert isMatch("ab", ".*") == True

    # ===== Single Character Tests =====
    def test_single_char_exact_match(self):
        """Single character exact match"""
        assert isMatch("a", "a") == True

    def test_single_char_no_match(self):
        """Single character no match"""
        assert isMatch("a", "b") == False

    def test_single_char_dot(self):
        """Single character with dot"""
        assert isMatch("a", ".") == True
        assert isMatch("z", ".") == True

    # ===== Dot Matching Tests =====
    def test_dot_matches_any_single_char(self):
        """Dot matches any single character"""
        assert isMatch("a", ".") == True
        assert isMatch("b", ".") == True
        assert isMatch("z", ".") == True

    def test_multiple_dots(self):
        """Multiple dots match multiple characters"""
        assert isMatch("abc", "...") == True
        assert isMatch("ab", "...") == False
        assert isMatch("abcd", "...") == False

    def test_dot_with_literal_chars(self):
        """Dot mixed with literal characters"""
        assert isMatch("ab", "a.") == True
        assert isMatch("ac", "a.") == True
        assert isMatch("a", "a.") == False
        assert isMatch("abc", "a.c") == True
        assert isMatch("adc", "a.c") == True
        assert isMatch("ac", "a.c") == False

    # ===== Star Matching Tests =====
    def test_star_zero_occurrences(self):
        """Star matches zero occurrences"""
        assert isMatch("b", "a*b") == True
        assert isMatch("aab", "a*ab") == True
        assert isMatch("c", "a*c") == True

    def test_star_one_occurrence(self):
        """Star matches one occurrence"""
        assert isMatch("a", "a*") == True
        assert isMatch("ab", "a*b") == True

    def test_star_multiple_occurrences(self):
        """Star matches multiple occurrences"""
        assert isMatch("aa", "a*") == True
        assert isMatch("aaa", "a*") == True
        assert isMatch("aaaa", "a*") == True
        assert isMatch("aaab", "a*b") == True

    def test_star_with_dot(self):
        """Star with dot pattern"""
        assert isMatch("ab", ".*") == True
        assert isMatch("abc", ".*") == True
        assert isMatch("", ".*") == True
        assert isMatch("a", ".*") == True
        assert isMatch("aab", ".*") == True

    def test_star_no_match(self):
        """Star patterns that don't match"""
        assert isMatch("aa", "a") == False
        assert isMatch("ba", "a*") == False
        assert isMatch("baa", "a*") == False

    # ===== Complex Pattern Tests =====
    def test_multiple_star_patterns(self):
        """Multiple star patterns in sequence"""
        assert isMatch("a", "a*") == True
        assert isMatch("aa", "a*a*") == True
        assert isMatch("aaa", "a*a*a*") == True
        assert isMatch("ab", "a*b*") == True
        assert isMatch("aabb", "a*b*") == True

    def test_alternating_chars_and_stars(self):
        """Alternating characters and stars"""
        assert isMatch("mississippi", "mis*is*p*.") == True
        assert isMatch("ab", ".*") == True
        assert isMatch("aab", "c*a*b") == True

    def test_complex_pattern_1(self):
        """Complex pattern: a*b*c*"""
        assert isMatch("", "a*b*c*") == True
        assert isMatch("a", "a*b*c*") == True
        assert isMatch("ab", "a*b*c*") == True
        assert isMatch("abc", "a*b*c*") == True
        assert isMatch("aabbcc", "a*b*c*") == True

    def test_complex_pattern_2(self):
        """Complex pattern with dots and stars"""
        assert isMatch("aab", "c*a*b") == True
        assert isMatch("ab", ".*") == True
        assert isMatch("aab", "a*a*b") == True

    def test_complex_pattern_3(self):
        """Pattern with leading star characters"""
        assert isMatch("aa", "a*") == True
        assert isMatch("aaa", "a*") == True
        assert isMatch("aaaa", "a*") == True

    # ===== Edge Cases =====
    def test_empty_string_empty_pattern(self):
        """Empty string and empty pattern"""
        # Based on constraints, both should be at least 1 character
        # But testing edge case behavior
        pass

    def test_empty_string_with_star_pattern(self):
        """Empty string with star pattern"""
        assert isMatch("", "a*") == True
        assert isMatch("", "a*b*") == True
        assert isMatch("", ".*") == True

    def test_single_star_pattern(self):
        """Single star patterns"""
        assert isMatch("a", "a*") == True
        assert isMatch("aa", "a*") == True
        assert isMatch("aaa", "a*") == True

    def test_pattern_longer_than_string(self):
        """Pattern longer than string without stars"""
        assert isMatch("a", "ab") == False
        assert isMatch("a", "abc") == False

    def test_string_longer_than_pattern(self):
        """String longer than pattern"""
        assert isMatch("aaa", "a") == False
        assert isMatch("aaa", "aa") == False

    def test_repeated_different_chars(self):
        """Repeated different characters"""
        assert isMatch("aabb", "a*b*") == True
        assert isMatch("aabbb", "a*b*") == True
        assert isMatch("aaabbb", "a*b*") == True

    def test_no_match_cases(self):
        """Cases that should not match"""
        assert isMatch("aa", "a") == False
        assert isMatch("aa", "a?") == False  # No ? support, but test literal
        assert isMatch("ab", "a") == False
        assert isMatch("ba", "a*") == False

    def test_dot_star_comprehensive(self):
        """Comprehensive dot-star tests"""
        assert isMatch("", ".*") == True
        assert isMatch("a", ".*") == True
        assert isMatch("ab", ".*") == True
        assert isMatch("abc", ".*") == True
        assert isMatch("abcdefghij", ".*") == True

    def test_pattern_with_specific_chars_and_stars(self):
        """Pattern with specific characters and stars"""
        assert isMatch("aaaa", "a*a*a*a*") == True
        assert isMatch("abcabczzzde", ".*abc???de*") == False  # No ? support
        assert isMatch("ab", "a*b*") == True
        assert isMatch("aab", "a*b*") == True

    def test_star_after_dot(self):
        """Star after dot pattern"""
        assert isMatch("aab", ".*b") == True
        assert isMatch("aab", "a.*b") == True
        assert isMatch("ab", "a.*b") == True
        assert isMatch("aabb", "a.*b") == True

    def test_multiple_different_star_patterns(self):
        """Multiple different star patterns"""
        assert isMatch("aabbcc", "a*b*c*") == True
        assert isMatch("abc", "a*b*c*") == True
        assert isMatch("ac", "a*b*c*") == True
        assert isMatch("c", "a*b*c*") == True

    def test_greedy_vs_non_greedy(self):
        """Test cases that might trip up greedy matching"""
        assert isMatch("aaa", "a*a") == True
        assert isMatch("aaa", "a*aa") == True
        assert isMatch("aaaa", "a*a*a") == True

    def test_pattern_with_trailing_star(self):
        """Pattern ending with star"""
        assert isMatch("a", "a*") == True
        assert isMatch("aa", "a*") == True
        assert isMatch("aaa", "a*") == True
        assert isMatch("aaaa", "a*") == True
        assert isMatch("aaaaa", "a*") == True

    def test_pattern_with_leading_star_char(self):
        """Pattern with star character early"""
        assert isMatch("aab", "a*ab") == True
        assert isMatch("ab", "a*b") == True
        assert isMatch("b", "a*b") == True

    def test_mixed_dot_and_char_with_star(self):
        """Mixed dot, character, and star"""
        assert isMatch("aa", "a.") == True
        assert isMatch("ab", "a.") == True
        assert isMatch("aaa", "a.*") == True
        assert isMatch("abc", "a.*c") == True

    def test_no_match_with_star(self):
        """Star patterns that should not match"""
        assert isMatch("ba", "a*") == False
        assert isMatch("ca", "a*") == False
        assert isMatch("baa", "a*") == False

    # ===== Performance/Efficiency Tests =====
    def test_performance_medium_input(self):
        """Performance test with medium-sized inputs"""
        # Create a pattern like "a*b*c*d*e*..." and matching string
        s = "a" * 5 + "b" * 5 + "c" * 5 + "d" * 5
        p = "a*b*c*d*"
        
        start = time.time()
        result = isMatch(s, p)
        elapsed = time.time() - start
        
        assert result == True
        assert elapsed < 1.0, f"Performance test failed: took {elapsed}s"

    def test_performance_complex_pattern(self):
        """Performance test with complex pattern"""
        # Pattern with many alternatives
        s = "aaaaaaaaaaaaaaaaaab"
        p = "a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*b"
        
        start = time.time()
        result = isMatch(s, p)
        elapsed = time.time() - start
        
        assert result == True
        assert elapsed < 1.0, f"Performance test failed: took {elapsed}s"

    def test_performance_worst_case_pattern(self):
        """Performance test for potential worst case"""
        # This tests that the solution doesn't use exponential backtracking
        s = "a" * 20
        p = "a*" * 10
        
        start = time.time()
        result = isMatch(s, p)
        elapsed = time.time() - start
        
        assert result == True
        assert elapsed < 1.0, f"Performance test failed: took {elapsed}s"

    def test_performance_no_match_case(self):
        """Performance test for non-matching case"""
        s = "a" * 20
        p = "b*"
        
        start = time.time()
        result = isMatch(s, p)
        elapsed = time.time() - start
        
        assert result == False
        assert elapsed < 1.0, f"Performance test failed: took {elapsed}s"

    def test_performance_dot_star_large(self):
        """Performance test with .* pattern"""
        s = "a" * 20
        p = ".*"
        
        start = time.time()
        result = isMatch(s, p)
        elapsed = time.time() - start
        
        assert result == True
        assert elapsed < 1.0, f"Performance test failed: took {elapsed}s"

    # ===== Additional Edge Cases =====
    def test_all_same_char_pattern(self):
        """All same character in pattern"""
        assert isMatch("aaaa", "a*") == True
        assert isMatch("aaaa", "a*a*") == True
        assert isMatch("aaaa", "a*a*a*") == True

    def test_pattern_with_zero_star_matches(self):
        """Pattern where star matches zero times"""
        assert isMatch("b", "a*b") == True
        assert isMatch("bb", "a*b*") == True
        assert isMatch("c", "a*b*c") == True

    def test_alternating_pattern(self):
        """Alternating character pattern"""
        assert isMatch("ababab", "a*b*") == False
        assert isMatch("ab", "a*b*") == True
        assert isMatch("aabb", "a*b*") == True

    def test_dot_matches_single_char_only(self):
        """Verify dot matches exactly one character"""
        assert isMatch("a", ".") == True
        assert isMatch("ab", ".") == False
        assert isMatch("ab", "..") == True
        assert isMatch("abc", "..") == False

    def test_complex_real_world_pattern(self):
        """Complex real-world-like patterns"""
        assert isMatch("mississippi", "mis*is*p*.") == True
        assert isMatch("aa", "a") == False
        assert isMatch("aa", "a*") == True
        assert isMatch("ab", ".*") == True
        assert isMatch("aab", "c*a*b") == True