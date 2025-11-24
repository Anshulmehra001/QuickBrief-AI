#!/usr/bin/env python3
"""
Test runner for QuickBrief AI - runs all test suites.
"""

import sys
import subprocess
import os

def run_test_file(test_file, description):
    """Run a test file and return success status."""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file}: {str(e)}")
        return False

def main():
    """Run all test suites."""
    print("QuickBrief AI - Complete Test Suite")
    print("=" * 60)
    
    # List of test files to run
    test_files = [
        ("test_workflow.py", "Basic Workflow Tests"),
        ("test_real_workflow.py", "Realistic Workflow Tests"),
        ("test_error_scenarios.py", "Error Handling Tests"),
        ("test_core_functions.py", "Automated Core Function Tests")
    ]
    
    results = []
    
    for test_file, description in test_files:
        if os.path.exists(test_file):
            success = run_test_file(test_file, description)
            results.append((description, success))
        else:
            print(f"\nWarning: Test file {test_file} not found, skipping...")
            results.append((description, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    all_passed = True
    for description, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{description:<40} {status}")
        if not success:
            all_passed = False
    
    print(f"{'='*60}")
    if all_passed:
        print("✓ ALL TEST SUITES PASSED!")
    else:
        print("✗ SOME TEST SUITES FAILED!")
    print(f"{'='*60}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)