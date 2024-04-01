import unittest
from hybridagi import PathOutputParser

def test_parse_valid_path():
    parser = PathOutputParser()
    path = '/path/to/some/directory/'
    parsed_path = parser.parse(path)
    assert parsed_path == '/path/to/some/directory'

def test_parse_path_with_leading_and_trailing_whitespace():
    parser = PathOutputParser()
    path = '   /path/to/some/directory/   '
    parsed_path = parser.parse(path)
    assert parsed_path == '/path/to/some/directory'

def test_parse_path_with_double_quotes():
    parser = PathOutputParser()
    path = '"/path/to/some/directory/"'
    parsed_path = parser.parse(path)
    assert parsed_path == '/path/to/some/directory'

def test_parse_single_character_path():
    parser = PathOutputParser()
    path = '/x/'
    parsed_path = parser.parse(path)
    assert parsed_path == '/x'

def test_parse_empty_path():
    parser = PathOutputParser()
    path = ''
    parsed_path = parser.parse(path)
    assert parsed_path == ''

def test_fix_path_removes_trailing_slash():
    parser = PathOutputParser()
    path = '/some/path/'
    fixed_path = parser.parse(path)
    assert fixed_path == '/some/path'

def test_fix_path_does_not_remove_trailing_slash_for_single_character_path():
    parser = PathOutputParser()
    path = '/x/'
    fixed_path = parser.parse(path)
    assert fixed_path == '/x'