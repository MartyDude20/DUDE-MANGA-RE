#!/usr/bin/env python3

try:
    print("Testing imports...")
    from flask import Flask
    print("✓ Flask imported")
    
    from cache_manager import CacheManager
    print("✓ CacheManager imported")
    
    cm = CacheManager()
    print("✓ CacheManager instantiated")
    
    print("✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc() 