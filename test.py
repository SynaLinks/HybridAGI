import unittest
import coverage

cov = coverage.Coverage()
cov.start()

test_loader = unittest.TestLoader()
test_suite = test_loader.discover('tests')

test_runner = unittest.TextTestRunner()
test_result = test_runner.run(test_suite)

cov.stop()
cov.report()
cov.html_report(directory='htmlcov')
cov.save()