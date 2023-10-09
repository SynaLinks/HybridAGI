import unittest
from hybrid_agi import InterpreterOutputParser

class TestInterpreterOutputParser(unittest.TestCase):
    def setUp(self):
        self.parser = InterpreterOutputParser()

    def test_parse_valid_output(self):
        output = \
"""example.txt
```python
print('Hello, World!')
```"""
        new_output = self.parser.parse(output)
        self.assertEqual(
            new_output,
            output
        )

    def test_parse_invalid_output_with_action(self):
        output = \
"""example.txt
```python
print('Hello, World!')
```
Action Purpose: Say hello to the User
Action: AskUser"""
        valid_output = \
"""example.txt
```python
print('Hello, World!')
```"""
        new_output = self.parser.parse(output)
        self.assertEqual(
            new_output,
            valid_output
        )

    def test_parse_invalid_output_with_decision(self):
        output = \
"""example.txt
```python
print('Hello, World!')
```
Decision Purpose: Check if there is a question to ask
Decision: A question to ask?"""
        valid_output = \
"""example.txt
```python
print('Hello, World!')
```"""
        new_output = self.parser.parse(output)
        self.assertEqual(
            new_output,
            valid_output
        )