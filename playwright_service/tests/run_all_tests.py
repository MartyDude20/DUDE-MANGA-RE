#!/usr/bin/env python3
"""
Test runner for all playwright_service tests
"""

import sys
import os
import importlib
import time
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # playwright_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # project root

def get_test_modules():
    """Get all test modules in the tests directory"""
    test_modules = []
    
    # Get all .py files in the current directory
    for filename in os.listdir('.'):
        if filename.endswith('.py') and filename.startswith('test_') and filename != 'run_all_tests.py':
            module_name = filename[:-3]  # Remove .py extension
            test_modules.append(module_name)
    
    return test_modules

def run_test_module(module_name):
    """Run a single test module"""
    print(f"\n{'='*60}")
    print(f"Running: {module_name}")
    print(f"{'='*60}")
    
    try:
        # Import and run the module
        module = importlib.import_module(module_name)
        
        # Check if module has a main function
        if hasattr(module, 'main'):
            start_time = time.time()
            module.main()
            end_time = time.time()
            print(f"✅ {module_name} completed in {end_time - start_time:.2f}s")
            return True
        else:
            print(f"⚠️  {module_name} has no main() function")
            return False
            
    except Exception as e:
        print(f"❌ {module_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_specific_tests():
    """Run specific important tests"""
    important_tests = [
        'test_simple_cache',
        'test_simple_cache_working',
        'test_performance',
        'source_health_check'
    ]
    
    print("🚀 Running Important Tests")
    print("=" * 60)
    
    results = {}
    for test_name in important_tests:
        if os.path.exists(f"{test_name}.py"):
            results[test_name] = run_test_module(test_name)
        else:
            print(f"⚠️  {test_name}.py not found")
            results[test_name] = False
    
    return results

def run_all_tests():
    """Run all test modules"""
    print("🚀 Running All Tests")
    print("=" * 60)
    
    test_modules = get_test_modules()
    print(f"Found {len(test_modules)} test modules:")
    for module in test_modules:
        print(f"  - {module}")
    
    results = {}
    for module_name in test_modules:
        results[module_name] = run_test_module(module_name)
    
    return results

def main():
    """Main test runner"""
    print("🧪 Playwright Service Test Runner")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if we should run all tests or just important ones
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        results = run_all_tests()
    else:
        results = run_specific_tests()
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 