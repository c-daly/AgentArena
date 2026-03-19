import pytest
import time
from solution import *


class TestIsValid:
    """Test suite for valid parentheses problem"""
    
    # Basic correctness tests from examples
    def test_example_1_simple_pair(self):
        """Test simple valid pair: ()"""
        assert isValid("()") == True
    
    def test_example_2_multiple_pairs(self):
        """Test multiple valid pairs: ()[]{}"""
        assert isValid("()[]{}") == True
    
    def test_example_3_mismatched_brackets(self):
        """Test mismatched brackets: (]"""
        assert isValid("(]") == False
    
    def test_example_4_nested_brackets(self):
        """Test nested valid brackets: ([])"""
        assert isValid("([])") == True
    
    def test_example_5_wrong_order(self):
        """Test wrong closing order: ([)]"""
        assert isValid("([)]") == False
    
    # Edge cases
    def test_single_open_bracket(self):
        """Test single opening bracket"""
        assert isValid("(") == False
    
    def test_single_close_bracket(self):
        """Test single closing bracket"""
        assert isValid(")") == False
    
    def test_only_open_brackets(self):
        """Test only opening brackets"""
        assert isValid("(((") == False
    
    def test_only_close_brackets(self):
        """Test only closing brackets"""
        assert isValid(")))") == False
    
    def test_close_before_open(self):
        """Test closing bracket before opening"""
        assert isValid(")()()") == False
    
    def test_extra_close_bracket(self):
        """Test extra closing bracket at end"""
        assert isValid("()())") == False
    
    def test_extra_open_bracket(self):
        """Test extra opening bracket at end"""
        assert isValid("(())") == True
    
    # Different bracket types
    def test_square_brackets_only(self):
        """Test only square brackets"""
        assert isValid("[]") == True
    
    def test_curly_brackets_only(self):
        """Test only curly brackets"""
        assert isValid("{}") == True
    
    def test_all_bracket_types(self):
        """Test all three bracket types mixed"""
        assert isValid("({[]})") == True
    
    def test_all_bracket_types_invalid(self):
        """Test all three bracket types in wrong order"""
        assert isValid("({[}])") == False
    
    # Nested structures
    def test_deeply_nested_valid(self):
        """Test deeply nested valid brackets"""
        assert isValid("(((())))") == True
    
    def test_deeply_nested_invalid(self):
        """Test deeply nested invalid brackets"""
        assert isValid("(((()))))")  == False
    
    def test_complex_nested_valid(self):
        """Test complex nested structure"""
        assert isValid("[{()()}]") == True
    
    def test_complex_nested_invalid(self):
        """Test complex nested structure invalid"""
        assert isValid("[{(})]") == False
    
    def test_alternating_types(self):
        """Test alternating bracket types"""
        assert isValid("()[]{}()[]{}") == True
    
    def test_alternating_types_invalid(self):
        """Test alternating bracket types invalid"""
        assert isValid("()[]{(") == False
    
    # Specific mismatch cases
    def test_round_closed_by_square(self):
        """Test round bracket closed by square"""
        assert isValid("(]") == False
    
    def test_round_closed_by_curly(self):
        """Test round bracket closed by curly"""
        assert isValid("(}") == False
    
    def test_square_closed_by_round(self):
        """Test square bracket closed by round"""
        assert isValid("[)") == False
    
    def test_square_closed_by_curly(self):
        """Test square bracket closed by curly"""
        assert isValid("[}") == False
    
    def test_curly_closed_by_round(self):
        """Test curly bracket closed by round"""
        assert isValid("{)") == False
    
    def test_curly_closed_by_square(self):
        """Test curly bracket closed by square"""
        assert isValid("{]") == False
    
    # Minimum valid cases
    def test_minimum_valid_round(self):
        """Test minimum valid round brackets"""
        assert isValid("()") == True
    
    def test_minimum_valid_square(self):
        """Test minimum valid square brackets"""
        assert isValid("[]") == True
    
    def test_minimum_valid_curly(self):
        """Test minimum valid curly brackets"""
        assert isValid("{}") == True
    
    # Performance test - large input
    def test_performance_large_valid_input(self):
        """Test performance with large valid input"""
        # Create a large valid string with 5000 pairs of brackets
        large_input = "()" * 5000
        
        start_time = time.time()
        result = isValid(large_input)
        elapsed_time = time.time() - start_time
        
        assert result == True
        # Should complete in well under 1 second for O(n) solution
        # Generous threshold to allow for system variations
        assert elapsed_time < 1.0, f"Performance test failed: {elapsed_time}s"
    
    def test_performance_large_invalid_input(self):
        """Test performance with large invalid input"""
        # Create a large invalid string (all open brackets)
        large_input = "(" * 5000
        
        start_time = time.time()
        result = isValid(large_input)
        elapsed_time = time.time() - start_time
        
        assert result == False
        # Should complete in well under 1 second for O(n) solution
        assert elapsed_time < 1.0, f"Performance test failed: {elapsed_time}s"
    
    def test_performance_large_complex_input(self):
        """Test performance with large complex nested input"""
        # Create a large complex valid string
        large_input = "([{}])" * 1000
        
        start_time = time.time()
        result = isValid(large_input)
        elapsed_time = time.time() - start_time
        
        assert result == True
        # Should complete in well under 1 second for O(n) solution
        assert elapsed_time < 1.0, f"Performance test failed: {elapsed_time}s"
    
    def test_performance_large_invalid_complex_input(self):
        """Test performance with large complex invalid input"""
        # Create a large complex invalid string
        large_input = "([{])" * 1000
        
        start_time = time.time()
        result = isValid(large_input)
        elapsed_time = time.time() - start_time
        
        assert result == False
        # Should complete in well under 1 second for O(n) solution
        assert elapsed_time < 1.0, f"Performance test failed: {elapsed_time}s"
    
    # Maximum constraint test
    def test_max_length_constraint(self):
        """Test with maximum length constraint (10^4)"""
        # Create string with exactly 10000 characters (5000 pairs)
        large_input = "()" * 5000
        assert len(large_input) == 10000
        
        start_time = time.time()
        result = isValid(large_input)
        elapsed_time = time.time() - start_time
        
        assert result == True
        assert elapsed_time < 1.0


# Parametrized tests for comprehensive coverage
class TestIsValidParametrized:
    """Parametrized tests for comprehensive coverage"""
    
    @pytest.mark.parametrize("input_str,expected", [
        ("()", True),
        ("()[]{}", True),
        ("(]", False),
        ("([()])", True),
        ("([)]", False),
        ("{[]}", True),
        ("", False),  # Empty string - constraint says 1 <= length
        ("(", False),
        (")", False),
        ("((", False),
        ("))", False),
        ("(())", True),
        ("[[]", False),
        ("[[]]", True),
        ("{{}}", True),
        ("({[]})", True),
        ("({[}])", False),
    ])
    def test_various_cases(self, input_str, expected):
        """Test various bracket combinations"""
        if input_str == "":
            # Skip empty string as constraint requires length >= 1
            pytest.skip("Empty string not in constraint range")
        assert isValid(input_str) == expected