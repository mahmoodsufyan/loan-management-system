import unittest
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def suite():
    loader = unittest.TestLoader()
    s = unittest.TestSuite()
    s.addTests(loader.discover(os.path.dirname(__file__), pattern="test_*.py"))
    return s

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    sys.exit(not result.wasSuccessful())

