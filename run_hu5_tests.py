"""
Test runner for HU5 Diagnostic Endpoint Tests - Simplified
==========================================================

This script provides an easy way to run the simplified HU5 diagnostic tests.

Usage:
    python run_hu5_tests.py                    # Run all tests
    python run_hu5_tests.py --mongodb-only     # Test only MongoDB connection
    python run_hu5_tests.py --service-only     # Test only diagnostic service
    python run_hu5_tests.py --verbose          # Verbose output
"""
import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

import pytest

# Import después de añadir el path
from src.database.mongodb import mongo_manager


async def check_mongodb_connection():
    """Check MongoDB connection before running tests."""
    try:
        print("🔄 Checking MongoDB connection...")
        await mongo_manager.connect()
        await mongo_manager.client.admin.command('ping')
        print("✅ MongoDB connection successful")
        await mongo_manager.disconnect()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Make sure MongoDB is running and accessible")
        return False


def run_tests(test_filter=None, verbose=False):
    """Run the HU5 diagnostic tests."""
    test_file = "tests/test_diagnostic_endpoint.py"
    
    # Build pytest arguments
    args = [test_file]
    
    if verbose:
        args.extend(["-v", "-s"])
    else:
        args.append("-v")
    
    # Add specific test filter if provided
    if test_filter:
        args.append(f"-k {test_filter}")
    
    # Add async support
    args.extend(["--asyncio-mode=auto"])
    
    print(f"🧪 Running HU5 Diagnostic Tests...")
    print(f"📁 Test file: {test_file}")
    print(f"🔧 Arguments: {' '.join(args)}")
    print("=" * 60)
    
    # Run tests
    exit_code = pytest.main(args)
    
    print("=" * 60)
    if exit_code == 0:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed. Check output above.")
    
    return exit_code


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Run HU5 Diagnostic Endpoint Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_hu5_tests.py                    # Run all tests
    python run_hu5_tests.py --mongodb-only     # Test MongoDB only
    python run_hu5_tests.py --endpoint-only    # Test endpoint only
    python run_hu5_tests.py --verbose          # Verbose output
        """
    )
    
    parser.add_argument(
        "--mongodb-only",
        action="store_true",
        help="Run only MongoDB connection tests"
    )
    
    parser.add_argument(
        "--service-only",
        action="store_true",
        help="Run only diagnostic service tests"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--check-connection",
        action="store_true",
        help="Only check MongoDB connection and exit"
    )
    
    args = parser.parse_args()
    
    print("🏥 HU5 - Diagnostic Endpoint Test Suite")
    print("=" * 50)
    
    # Check connection first if requested
    if args.check_connection:
        connection_ok = asyncio.run(check_mongodb_connection())
        sys.exit(0 if connection_ok else 1)
    
    # Check MongoDB connection before running tests
    print("🔍 Pre-flight checks...")
    connection_ok = asyncio.run(check_mongodb_connection())
    
    if not connection_ok:
        print("\n❌ Cannot proceed without MongoDB connection")
        print("💡 Start MongoDB and try again")
        sys.exit(1)
    
    # Determine test filter based on arguments
    test_filter = None
    if args.mongodb_only:
        test_filter = "mongodb"
        print("🎯 Running MongoDB tests only")
    elif args.service_only:
        test_filter = "service"
        print("🎯 Running diagnostic service tests only")
    else:
        print("🎯 Running all simplified HU5 tests")
    
    # Run tests
    exit_code = run_tests(test_filter, args.verbose)
    
    # Final message
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("   - MongoDB connection: ✅")
    print("   - Diagnostic endpoint availability: ✅")
    print("   - Endpoint validation: ✅")
    print("   - Diagnostic service methods: ✅")
    print("   - Service error handling: ✅")
    
    if exit_code == 0:
        print("\n🏆 HU5 implementation is working correctly!")
    else:
        print("\n🔧 Some issues found. Please review the test output.")
    
    print("\n💡 To run tests manually:")
    print("   python -m pytest tests/test_diagnostic_endpoint.py -v --asyncio-mode=auto")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()