import unittest
from hybridagi import PathOutputParser

class TestPathOutputParser(unittest.TestCase):
    def setUp(self):
        self.parser = PathOutputParser()

    def test_parse_valid_path(self):
        path = '/path/to/some/directory/'
        parsed_path = self.parser.parse(path)
        self.assertEqual(parsed_path, '/path/to/some/directory')

    def test_parse_path_with_leading_and_trailing_whitespace(self):
        path = '   /path/to/some/directory/   '
        parsed_path = self.parser.parse(path)
        self.assertEqual(parsed_path, '/path/to/some/directory')

    def test_parse_path_with_double_quotes(self):
        path = '"/path/to/some/directory/"'
        parsed_path = self.parser.parse(path)
        self.assertEqual(parsed_path, '/path/to/some/directory')

    def test_parse_single_character_path(self):
        path = '/x/'
        parsed_path = self.parser.parse(path)
        self.assertEqual(parsed_path, '/x')

    def test_parse_empty_path(self):
        path = ''
        parsed_path = self.parser.parse(path)
        self.assertEqual(parsed_path, '')

    def test_fix_path_removes_trailing_slash(self):
        path = '/some/path/'
        fixed_path = self.parser.fix_path(path)
        self.assertEqual(fixed_path, '/some/path')

    def test_fix_path_does_not_remove_trailing_slash_for_single_character_path(self):
        path = '/x/'
        fixed_path = self.parser.fix_path(path)
        self.assertEqual(fixed_path, '/x')

if __name__ == '__main__':
    unittest.main()