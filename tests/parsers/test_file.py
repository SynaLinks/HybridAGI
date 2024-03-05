import unittest
from hybridagi import FileOutputParser

class TestFileOutputParser(unittest.TestCase):
    def setUp(self):
        self.parser = FileOutputParser()

    def test_parse_valid_output(self):
        output = "example.txt\n```python\nprint('Hello, World!')\n```"
        filenames, contents, languages = self.parser.parse(output)
        self.assertEqual(filenames[0], "example.txt")
        self.assertEqual(languages[0], "python")
        self.assertEqual(contents[0], "print('Hello, World!')")

    def test_parse_output_with_leading_and_trailing_whitespace(self):
        output = "\nexample.txt\n```python\nprint('Hello, World!')\n```\n"
        filenames, contents, languages = self.parser.parse(output)
        self.assertEqual(filenames[0], "example.txt")
        self.assertEqual(languages[0], "python")
        self.assertEqual(contents[0], "print('Hello, World!')")

    def test_parse_output_with_multiple_newlines_between_tokens(self):
        output = "example.txt\n```python\n\nprint('Hello, World!')\n\n```"
        filenames, contents, languages = self.parser.parse(output)
        self.assertEqual(filenames[0], "example.txt")
        self.assertEqual(languages[0], "python")
        self.assertEqual(contents[0], "print('Hello, World!')")

    def test_parse_output_with_multiple_ending_backticks(self):
        output = "example.txt\n```python\n\nprint('Hello, World!')\n\n```\n```"
        filenames, contents, languages = self.parser.parse(output)
        self.assertEqual(filenames[0], "example.txt")
        self.assertEqual(languages[0], "python")
        self.assertEqual(contents[0], "print('Hello, World!')")

    def test_parse_output_with_multiple_files(self):
        output = \
"""
example1.txt
```python
print('file 1')
```
some text

example2.txt
```python
print('file 2')
```
"""
        filenames, contents, languages = self.parser.parse(output)
        self.assertEqual(filenames[0], "example1.txt")
        self.assertEqual(languages[0], "python")
        self.assertEqual(contents[0], "print('file 1')")
        self.assertEqual(filenames[1], "example2.txt")
        self.assertEqual(languages[1], "python")
        self.assertEqual(contents[1], "print('file 2')")

    def test_parse_output_without_ending_backticks(self):
        output = "example.txt\n```python\n\nprint('Hello, World!')"
        with self.assertRaises(ValueError):
            self.parser.parse(output)

    def test_parse_output_with_invalid_format(self):
        # Missing backticks around LANG
        output = "example.txt\npython\nprint('Hello, World!')\n```"
        with self.assertRaises(ValueError):
            self.parser.parse(output)

    def test_get_format_instructions(self):
        instructions = self.parser.get_format_instructions()
        expected_instructions = \
"""
The Input should follow the following format:

FILENAME
```LANG
CONTENT
```

Where the following tokens must be replaced such that:
FILENAME is the lowercase file name including the file extension.
LANG is the markup code block language for the content's language (use plaintext for txt files)
and CONTENT its content. Make sure to follow the above format.
"""
        self.assertEqual(instructions, expected_instructions)

if __name__ == '__main__':
    unittest.main()
