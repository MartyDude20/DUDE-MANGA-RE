# Playwright Service Tests

This directory contains all test files for the playwright_service.

## Quick Start

### Run Important Tests
```bash
cd tests
python run_all_tests.py
```

### Run All Tests
```bash
cd tests
python run_all_tests.py --all
```

### Run Individual Tests
```bash
cd tests
python test_simple_cache.py
python test_simple_cache_working.py
python test_performance.py
```

## Test Files

### Core Cache Tests
- **`test_simple_cache.py`** - Tests the basic TTL cache functionality
- **`test_simple_cache_working.py`** - HTTP-based tests for the cache system
- **`test_performance.py`** - Performance benchmarks for the cache system

### Source Tests
- **`source_health_check.py`** - Tests all manga sources for availability
- **`test_asurascans_search.py`** - Tests AsuraScans search functionality
- **`test_specific_asurascans.py`** - Specific AsuraScans tests
- **`simple_asurascans_test.py`** - Simple AsuraScans functionality tests

### Load Tests
- **`frontend_load_test.py`** - Simulates frontend load testing
- **`quick_performance_test.py`** - Quick performance validation

### Legacy Tests (Old Preloader System)
- **`test_preloader.py`** - Tests for the old complex preloader system
- **`test_user_cache.py`** - Tests for user-specific caching

### Authentication Tests
- **`test_auth.py`** - Authentication system tests
- **`test_register.py`** - User registration tests
- **`test_backend.py`** - Basic backend functionality tests

## Test Categories

### ✅ Current System Tests
These tests are relevant to the current simple TTL cache system:
- `test_simple_cache.py`
- `test_simple_cache_working.py`
- `test_performance.py`
- `source_health_check.py`

### ⚠️ Legacy Tests
These tests are for the old complex preloader system and may not work with the current system:
- `test_preloader.py`
- `test_user_cache.py`
- `frontend_load_test.py`
- `quick_performance_test.py`

### 🔧 Utility Tests
These are utility and maintenance tests:
- `test_auth.py`
- `test_register.py`
- `test_backend.py`
- `test_asurascans_search.py`

## Running Tests from Different Locations

### From playwright_service directory:
```bash
python tests/run_all_tests.py
```

### From tests directory:
```bash
python run_all_tests.py
```

### From project root:
```bash
python playwright_service/tests/run_all_tests.py
```

## Test Results

Test results are saved in JSON format for performance tests:
- `performance_test_results_YYYYMMDD_HHMMSS.json`

## Notes

- All tests include proper import path handling for running from different locations
- The test runner automatically detects and runs tests with `main()` functions
- Performance tests measure cache hit rates and search speeds
- Source health checks verify all manga sources are working correctly 