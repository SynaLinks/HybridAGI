import unittest
import coverage

source_dirs = ['hybridagi']

cov = coverage.Coverage(source=source_dirs)
cov.start()

test_loader = unittest.TestLoader()
test_suite = test_loader.discover('tests')

test_runner = unittest.TextTestRunner()
test_result = test_runner.run(test_suite)

cov.stop()
cov.report()
cov.save()