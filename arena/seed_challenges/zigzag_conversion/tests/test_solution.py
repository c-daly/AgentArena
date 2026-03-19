import pytest
import time
from solution import *


class TestZigzagConvert:
    """Test suite for the zigzag string conversion problem."""

    # ==================== Basic Correctness Tests ====================
    
    def test_example_1(self):
        """Test Example 1: s = "PAYPALISHIRING", numRows = 3"""
        s = "PAYPALISHIRING"
        numRows = 3
        expected = "PAHNAPLSIIGYIR"
        assert convert(s, numRows) == expected
    
    def test_example_2(self):
        """Test Example 2: s = "PAYPALISHIRING", numRows = 4"""
        s = "PAYPALISHIRING"
        numRows = 4
        expected = "PINALSIGYAHRPI"
        assert convert(s, numRows) == expected
    
    def test_example_3(self):
        """Test Example 3: s = "A", numRows = 1"""
        s = "A"
        numRows = 1
        expected = "A"
        assert convert(s, numRows) == expected
    
    # ==================== Edge Cases ====================
    
    def test_single_character(self):
        """Test with a single character."""
        assert convert("A", 1) == "A"
        assert convert("A", 2) == "A"
        assert convert("A", 5) == "A"
    
    def test_two_characters_one_row(self):
        """Test with two characters and one row."""
        assert convert("AB", 1) == "AB"
    
    def test_two_characters_two_rows(self):
        """Test with two characters and two rows."""
        assert convert("AB", 2) == "AB"
    
    def test_two_characters_three_rows(self):
        """Test with two characters and three rows."""
        assert convert("AB", 3) == "AB"
    
    def test_string_length_equals_numrows(self):
        """Test when string length equals number of rows."""
        assert convert("ABCD", 4) == "ABCD"
    
    def test_numrows_greater_than_length(self):
        """Test when numRows is greater than string length."""
        assert convert("ABC", 10) == "ABC"
    
    def test_two_rows(self):
        """Test with 2 rows."""
        # A B C D E F
        # In 2 rows: A C E / B D F
        s = "ABCDEF"
        expected = "ACEBDF"
        assert convert(s, 2) == expected
    
    def test_three_rows_simple(self):
        """Test with 3 rows on a simple string."""
        # A B C D E F G H I
        # Row 0: A   C   E   G   I
        # Row 1: B D B D F H
        # Row 2: C   E   G
        s = "ABCDEFGHI"
        result = convert(s, 3)
        # Pattern: A(0) B(1) C(2) D(1) E(0) F(1) G(2) H(1) I(0)
        # Row 0: A, E, I
        # Row 1: B, D, F, H
        # Row 2: C, G
        expected = "AEIBDFHCG"
        assert result == expected
    
    def test_four_rows(self):
        """Test with 4 rows."""
        s = "ABCDEFGHIJKLMNOP"
        result = convert(s, 4)
        # Pattern repeats every 6 chars (2*(4-1))
        # Row 0: A(0), G(6), M(12)
        # Row 1: B(1), F(5), H(7), L(11), N(13)
        # Row 2: C(2), E(4), I(8), K(10), O(14)
        # Row 3: D(3), J(9), P(15)
        expected = "AGMBFHLNCEIKODJP"
        assert result == expected
    
    def test_lowercase_and_uppercase(self):
        """Test with mixed case letters."""
        s = "PayPalIsHiring"
        numRows = 3
        result = convert(s, numRows)
        # Should handle case correctly
        assert isinstance(result, str)
        assert len(result) == len(s)
    
    def test_special_characters(self):
        """Test with special characters (comma and period)."""
        s = "A,B.C,D"
        numRows = 2
        result = convert(s, numRows)
        assert isinstance(result, str)
        assert len(result) == len(s)
        assert "," in result
        assert "." in result
    
    def test_all_same_character(self):
        """Test with all same characters."""
        s = "AAAAAAA"
        numRows = 3
        result = convert(s, numRows)
        assert result == "AAAAAAA"
        assert len(result) == len(s)
    
    # ==================== Pattern Verification Tests ====================
    
    def test_output_length_preserved(self):
        """Test that output length equals input length."""
        test_cases = [
            ("PAYPALISHIRING", 3),
            ("PAYPALISHIRING", 4),
            ("ABCDEFGHIJKLMNOP", 5),
            ("A", 1),
            ("AB", 2),
        ]
        for s, numRows in test_cases:
            result = convert(s, numRows)
            assert len(result) == len(s), f"Length mismatch for {s} with {numRows} rows"
    
    def test_output_contains_all_characters(self):
        """Test that output contains all characters from input."""
        test_cases = [
            ("PAYPALISHIRING", 3),
            ("PAYPALISHIRING", 4),
            ("ABCDEFGHIJKLMNOP", 5),
        ]
        for s, numRows in test_cases:
            result = convert(s, numRows)
            assert sorted(result) == sorted(s), f"Character mismatch for {s} with {numRows} rows"
    
    # ==================== Efficiency/Performance Tests ====================
    
    def test_large_input_performance(self):
        """Test performance with a large input string."""
        # Create a large string
        s = "A" * 1000
        numRows = 10
        
        start_time = time.time()
        result = convert(s, numRows)
        elapsed_time = time.time() - start_time
        
        # Should complete in well under 1 second for O(n) or O(n log n) solution
        # Brute force O(n²) would be much slower
        assert elapsed_time < 1.0, f"Performance test failed: {elapsed_time}s"
        assert len(result) == len(s)
    
    def test_very_large_input_performance(self):
        """Test performance with a very large input string."""
        # Create a very large string
        s = "".join(chr(65 + (i % 26)) for i in range(1000))
        numRows = 50
        
        start_time = time.time()
        result = convert(s, numRows)
        elapsed_time = time.time() - start_time
        
        # Should complete in well under 2 seconds
        assert elapsed_time < 2.0, f"Performance test failed: {elapsed_time}s"
        assert len(result) == len(s)
        assert sorted(result) == sorted(s)
    
    def test_many_rows_performance(self):
        """Test performance with many rows."""
        s = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 30  # 780 characters
        numRows = 100
        
        start_time = time.time()
        result = convert(s, numRows)
        elapsed_time = time.time() - start_time
        
        # Should complete quickly even with many rows
        assert elapsed_time < 1.0, f"Performance test failed: {elapsed_time}s"
        assert len(result) == len(s)
    
    def test_extreme_case_one_row(self):
        """Test performance with numRows = 1 (should be trivial)."""
        s = "A" * 1000
        numRows = 1
        
        start_time = time.time()
        result = convert(s, numRows)
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 0.1
        assert result == s
    
    def test_extreme_case_many_rows(self):
        """Test performance when numRows > string length."""
        s = "ABCDEFGHIJ"
        numRows = 1000
        
        start_time = time.time()
        result = convert(s, numRows)
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 0.1
        assert result == s
    
    # ==================== Boundary Tests ====================
    
    def test_constraint_min_length(self):
        """Test with minimum string length (1)."""
        result = convert("A", 1)
        assert result == "A"
    
    def test_constraint_max_length(self):
        """Test with maximum string length (1000)."""
        s = "A" * 1000
        result = convert(s, 1)
        assert result == s
        assert len(result) == 1000
    
    def test_constraint_min_rows(self):
        """Test with minimum numRows (1)."""
        s = "PAYPALISHIRING"
        result = convert(s, 1)
        assert result == s
    
    def test_constraint_max_rows(self):
        """Test with maximum numRows (1000)."""
        s = "PAYPALISHIRING"
        result = convert(s, 1000)
        assert result == s
    
    # ==================== Additional Verification Tests ====================
    
    def test_zigzag_pattern_verification_3_rows(self):
        """Manually verify the zigzag pattern for 3 rows."""
        s = "PAYPALISHIRING"
        # P(0) A(1) Y(2) P(3) A(4) L(5) I(6) S(7) H(8) I(9) R(10) I(11) N(12) G(13)
        # Row 0: P(0), A(4), H(8), N(12)
        # Row 1: A(1), Y(2), P(3), L(5), I(6), S(7), I(9), R(10), I(11), G(13)
        # Row 2: Y(2), I(6), R(10)
        # Wait, let me recalculate the pattern
        # Cycle length = 2*(3-1) = 4
        # Position 0: row 0
        # Position 1: row 1
        # Position 2: row 2
        # Position 3: row 1
        # Position 4: row 0
        # Position 5: row 1
        # Position 6: row 2
        # Position 7: row 1
        # Position 8: row 0
        # Position 9: row 1
        # Position 10: row 2
        # Position 11: row 1
        # Position 12: row 0
        # Position 13: row 1
        # Row 0: P(0), A(4), H(8), N(12)
        # Row 1: A(1), Y(2), P(3), L(5), I(6), S(7), I(9), R(10), I(11), G(13)
        # Row 2: Y(2), I(6), R(10)
        # Hmm, Y appears twice. Let me reconsider...
        # Actually the cycle is: down 3, up 2, down 3, up 2...
        # Positions: 0(down), 1(down), 2(down), 3(up), 4(up), 5(down), 6(down), 7(down), 8(up), 9(up), 10(down)...
        # Let me just verify the known answer
        result = convert(s, 3)
        assert result == "PAHNAPLSIIGYIR"
    
    def test_zigzag_pattern_verification_4_rows(self):
        """Manually verify the zigzag pattern for 4 rows."""
        s = "PAYPALISHIRING"
        result = convert(s, 4)
        assert result == "PINALSIGYAHRPI"
    
    def test_idempotent_single_row(self):
        """Test that single row conversion is idempotent."""
        s = "PAYPALISHIRING"
        result = convert(s, 1)
        assert result == s
    
    def test_different_numrows_same_string(self):
        """Test the same string with different numRows produces different results."""
        s = "PAYPALISHIRING"
        result_2 = convert(s, 2)
        result_3 = convert(s, 3)
        result_4 = convert(s, 4)
        
        # All should have same length but different order
        assert len(result_2) == len(result_3) == len(result_4) == len(s)
        # They should not all be equal (unless by coincidence)
        assert not (result_2 == result_3 == result_4)