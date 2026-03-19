import pytest
import time
from solution import *


class TestRomanToInt:
    """Test suite for Roman numeral to integer conversion."""
    
    # Basic correctness tests from problem examples
    def test_example_1_iii(self):
        """Test Example 1: III = 3"""
        assert romanToInt("III") == 3
    
    def test_example_2_lviii(self):
        """Test Example 2: LVIII = 58"""
        assert romanToInt("LVIII") == 58
    
    def test_example_3_mcmxciv(self):
        """Test Example 3: MCMXCIV = 1994"""
        assert romanToInt("MCMXCIV") == 1994
    
    # Single character tests
    def test_single_i(self):
        """Test single character I = 1"""
        assert romanToInt("I") == 1
    
    def test_single_v(self):
        """Test single character V = 5"""
        assert romanToInt("V") == 5
    
    def test_single_x(self):
        """Test single character X = 10"""
        assert romanToInt("X") == 10
    
    def test_single_l(self):
        """Test single character L = 50"""
        assert romanToInt("L") == 50
    
    def test_single_c(self):
        """Test single character C = 100"""
        assert romanToInt("C") == 100
    
    def test_single_d(self):
        """Test single character D = 500"""
        assert romanToInt("D") == 500
    
    def test_single_m(self):
        """Test single character M = 1000"""
        assert romanToInt("M") == 1000
    
    # Subtraction cases
    def test_subtraction_iv(self):
        """Test subtraction case IV = 4"""
        assert romanToInt("IV") == 4
    
    def test_subtraction_ix(self):
        """Test subtraction case IX = 9"""
        assert romanToInt("IX") == 9
    
    def test_subtraction_xl(self):
        """Test subtraction case XL = 40"""
        assert romanToInt("XL") == 40
    
    def test_subtraction_xc(self):
        """Test subtraction case XC = 90"""
        assert romanToInt("XC") == 90
    
    def test_subtraction_cd(self):
        """Test subtraction case CD = 400"""
        assert romanToInt("CD") == 400
    
    def test_subtraction_cm(self):
        """Test subtraction case CM = 900"""
        assert romanToInt("CM") == 900
    
    # Multiple subtraction cases
    def test_multiple_subtractions(self):
        """Test multiple subtraction cases in one numeral"""
        assert romanToInt("XCIX") == 99  # XC + IX
        assert romanToInt("CDXL") == 440  # CD + XL
        assert romanToInt("CMXC") == 990  # CM + XC
    
    # Additive cases (no subtraction)
    def test_additive_ii(self):
        """Test additive case II = 2"""
        assert romanToInt("II") == 2
    
    def test_additive_vi(self):
        """Test additive case VI = 6"""
        assert romanToInt("VI") == 6
    
    def test_additive_xi(self):
        """Test additive case XI = 11"""
        assert romanToInt("XI") == 11
    
    def test_additive_xxvii(self):
        """Test additive case XXVII = 27"""
        assert romanToInt("XXVII") == 27
    
    def test_additive_lxvi(self):
        """Test additive case LXVI = 66"""
        assert romanToInt("LXVI") == 66
    
    # Edge cases with maximum values
    def test_maximum_value_3999(self):
        """Test maximum valid value MMMCMXCIX = 3999"""
        assert romanToInt("MMMCMXCIX") == 3999
    
    def test_3000(self):
        """Test MMM = 3000"""
        assert romanToInt("MMM") == 3000
    
    def test_2000(self):
        """Test MM = 2000"""
        assert romanToInt("MM") == 2000
    
    def test_1000(self):
        """Test M = 1000"""
        assert romanToInt("M") == 1000
    
    # Complex mixed cases
    def test_complex_1984(self):
        """Test MCMLXXXIV = 1984"""
        assert romanToInt("MCMLXXXIV") == 1984
    
    def test_complex_1666(self):
        """Test MDCLXVI = 1666"""
        assert romanToInt("MDCLXVI") == 1666
    
    def test_complex_444(self):
        """Test CDXLIV = 444"""
        assert romanToInt("CDXLIV") == 444
    
    def test_complex_888(self):
        """Test DCCCLXXXVIII = 888"""
        assert romanToInt("DCCCLXXXVIII") == 888
    
    def test_complex_2023(self):
        """Test MMXXIII = 2023"""
        assert romanToInt("MMXXIII") == 2023
    
    # Boundary tests
    def test_minimum_value_1(self):
        """Test minimum valid value I = 1"""
        assert romanToInt("I") == 1
    
    def test_value_2(self):
        """Test II = 2"""
        assert romanToInt("II") == 2
    
    def test_value_5(self):
        """Test V = 5"""
        assert romanToInt("V") == 5
    
    def test_value_10(self):
        """Test X = 10"""
        assert romanToInt("X") == 10
    
    # Repeated characters
    def test_repeated_i_three_times(self):
        """Test III = 3 (repeated I)"""
        assert romanToInt("III") == 3
    
    def test_repeated_x_three_times(self):
        """Test XXX = 30 (repeated X)"""
        assert romanToInt("XXX") == 30
    
    def test_repeated_c_three_times(self):
        """Test CCC = 300 (repeated C)"""
        assert romanToInt("CCC") == 300
    
    def test_repeated_m_three_times(self):
        """Test MMM = 3000 (repeated M)"""
        assert romanToInt("MMM") == 3000
    
    # All subtraction pairs together
    def test_all_subtraction_pairs(self):
        """Test all six subtraction cases"""
        assert romanToInt("IV") == 4
        assert romanToInt("IX") == 9
        assert romanToInt("XL") == 40
        assert romanToInt("XC") == 90
        assert romanToInt("CD") == 400
        assert romanToInt("CM") == 900
    
    # Efficiency test
    def test_efficiency_large_input(self):
        """Test that function completes efficiently for maximum length input.
        
        The constraint is 1 <= s.length <= 15, so we test with a 15-character
        maximum valid roman numeral. The algorithm should be O(n) where n is
        the length of the string, so it should complete in microseconds.
        """
        # Create a 15-character roman numeral (maximum constraint)
        large_input = "MMMCMXCIX" + "MMMCMXCIX"[:6]  # MMMCMXCIXMMMCMX (15 chars)
        
        start_time = time.time()
        result = romanToInt(large_input)
        elapsed = time.time() - start_time
        
        # Should complete in well under 1 second (generous for O(n) algorithm)
        assert elapsed < 1.0, f"Function took {elapsed}s, expected < 1.0s"
        # Verify result is reasonable
        assert isinstance(result, int)
        assert result > 0
    
    def test_efficiency_many_repeated_calls(self):
        """Test that function handles many calls efficiently.
        
        This ensures the algorithm is linear and not quadratic.
        """
        test_cases = [
            "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
            "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
            "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC", "C", "CC", "CCC",
            "CD", "D", "DC", "DCC", "DCCC", "CM", "M", "MM", "MMM",
            "MCMXCIV", "MMMCMXCIX", "LVIII", "XXVII", "MDCLXVI"
        ]
        
        start_time = time.time()
        for test_case in test_cases:
            romanToInt(test_case)
        elapsed = time.time() - start_time
        
        # 45 calls should complete in well under 1 second
        assert elapsed < 1.0, f"Function took {elapsed}s for 45 calls, expected < 1.0s"
    
    # Type validation
    def test_return_type_is_int(self):
        """Test that function returns an integer"""
        result = romanToInt("V")
        assert isinstance(result, int)
    
    def test_return_type_for_complex_input(self):
        """Test that function returns an integer for complex input"""
        result = romanToInt("MCMXCIV")
        assert isinstance(result, int)


# Additional standalone test functions for parametrized testing
@pytest.mark.parametrize("roman,expected", [
    ("I", 1),
    ("II", 2),
    ("III", 3),
    ("IV", 4),
    ("V", 5),
    ("VI", 6),
    ("VII", 7),
    ("VIII", 8),
    ("IX", 9),
    ("X", 10),
    ("XI", 11),
    ("XII", 12),
    ("XIII", 13),
    ("XIV", 14),
    ("XV", 15),
    ("XVI", 16),
    ("XVII", 17),
    ("XVIII", 18),
    ("XIX", 19),
    ("XX", 20),
    ("XXX", 30),
    ("XL", 40),
    ("L", 50),
    ("LX", 60),
    ("LXX", 70),
    ("LXXX", 80),
    ("XC", 90),
    ("C", 100),
    ("CC", 200),
    ("CCC", 300),
    ("CD", 400),
    ("D", 500),
    ("DC", 600),
    ("DCC", 700),
    ("DCCC", 800),
    ("CM", 900),
    ("M", 1000),
    ("MM", 2000),
    ("MMM", 3000),
    ("LVIII", 58),
    ("MCMXCIV", 1994),
    ("XXVII", 27),
    ("MDCLXVI", 1666),
    ("MMMCMXCIX", 3999),
    ("MCMLXXXIV", 1984),
    ("CDXLIV", 444),
    ("DCCCLXXXVIII", 888),
    ("MMXXIII", 2023),
    ("XCIX", 99),
    ("CDXL", 440),
    ("CMXC", 990),
])
def test_roman_to_int_parametrized(roman, expected):
    """Parametrized test for various roman numeral conversions"""
    assert romanToInt(roman) == expected