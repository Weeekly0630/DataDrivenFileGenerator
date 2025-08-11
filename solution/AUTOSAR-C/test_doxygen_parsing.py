#!/usr/bin/env python3
"""
Test script for enhanced Doxygen parsing functionality.
"""

import sys
import os

# Add the modules directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'clang', 'modules'))

from c_node_printer import parse_doxygen_comment, parse_doxygen_comment_simple, DoxygenComment

def test_basic_doxygen():
    """Test basic Doxygen comment parsing."""
    comment = """
    /**
     * @brief This is a brief description.
     * @param[in] param1 First parameter description
     * @param[out] param2 Second parameter description  
     * @return Returns a status code
     * @deprecated This function is deprecated
     * @note This is a note
     * @warning This is a warning
     */
    """
    
    print("=== Test Basic Doxygen Comment ===")
    print(f"Input: {comment}")
    
    doxy = parse_doxygen_comment(comment)
    print(f"\nParsed brief: {doxy.brief}")
    print(f"Parsed detailed: {doxy.detailed}")
    print(f"Parsed params: {doxy.params}")
    print(f"Parsed returns: {doxy.returns}")
    print(f"Parsed deprecated: {doxy.deprecated}")
    print(f"Parsed note: {doxy.note}")
    print(f"Parsed warning: {doxy.warning}")
    
    print(f"\nFull string representation: {doxy}")
    print(f"Summary: {doxy.get_summary()}")
    print(f"Has content: {doxy.has_content()}")
    
    print(f"\nMarkdown format:\n{doxy.to_markdown()}")
    
    simple = parse_doxygen_comment_simple(comment)
    print(f"\nSimple parsing: {simple}")


def test_complex_comment():
    """Test complex comment with multiple sections."""
    comment = """
    /**
     * Calculate the square root of a number.
     * 
     * This function calculates the square root using Newton's method
     * for better precision than the standard library implementation.
     * 
     * @param[in] value The input value (must be non-negative)
     * @param[in] precision The desired precision (default: 1e-6)
     * @return The square root of the input value
     * @throws std::invalid_argument If value is negative
     * @throws std::runtime_error If convergence fails
     * 
     * @since Version 2.0
     * @author John Doe
     * @date 2024-01-15
     * 
     * @example
     * double result = sqrt_newton(16.0);
     * // result will be 4.0
     * 
     * @see std::sqrt
     * @todo Add support for complex numbers
     * @bug Known issue with very large numbers
     */
    """
    
    print("\n\n=== Test Complex Doxygen Comment ===")
    
    doxy = parse_doxygen_comment(comment)
    print(f"Brief: {doxy.brief}")
    print(f"Detailed: {doxy.detailed}")
    print(f"Parameters: {doxy.params}")
    print(f"Returns: {doxy.returns}")
    print(f"Throws: {doxy.throws}")
    print(f"Since: {doxy.since}")
    print(f"Author: {doxy.author}")
    print(f"Date: {doxy.date}")
    print(f"Example: {doxy.example}")
    print(f"See also: {doxy.see_also}")
    print(f"TODO: {doxy.todo}")
    print(f"Bug: {doxy.bug}")
    
    print(f"\nMarkdown format:\n{doxy.to_markdown()}")


def test_simple_comments():
    """Test simple comments without Doxygen tags."""
    comments = [
        "Simple comment without tags",
        "// C++ style comment",
        "/* Multi-line comment\n   with multiple lines */",
        "",
        None
    ]
    
    print("\n\n=== Test Simple Comments ===")
    
    for i, comment in enumerate(comments):
        print(f"\nTest {i+1}: {repr(comment)}")
        doxy = parse_doxygen_comment(comment)
        simple = parse_doxygen_comment_simple(comment)
        print(f"  Parsed: {doxy}")
        print(f"  Simple: {simple}")
        print(f"  Has content: {doxy.has_content()}")


def test_malformed_comments():
    """Test malformed or edge case comments."""
    comments = [
        "@brief Brief without content",
        "@param param_without_description",
        "@return",
        "@@invalid @tag",
        "\\brief Using backslash syntax",
        "\\param[in] name Description using backslash"
    ]
    
    print("\n\n=== Test Malformed/Edge Case Comments ===")
    
    for i, comment in enumerate(comments):
        print(f"\nTest {i+1}: {repr(comment)}")
        try:
            doxy = parse_doxygen_comment(comment)
            print(f"  Parsed successfully: {doxy}")
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    test_basic_doxygen()
    test_complex_comment()
    test_simple_comments()
    test_malformed_comments()
    
    print("\n\n=== All tests completed! ===")
