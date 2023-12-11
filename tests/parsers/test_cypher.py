import unittest
from hybridagi import CypherOutputParser

class TestCypherOutputParser(unittest.TestCase):
    def setUp(self):
        self.parser = CypherOutputParser()

    def test_parse_valid_query(self):
        query = "MATCH (n) RETURN n;"
        parsed_query = self.parser.parse(query)
        self.assertEqual(parsed_query, "MATCH (n) RETURN n")

    def test_parse_query_with_leading_and_trailing_whitespace(self):
        query = "  MATCH (n) RETURN n;  "
        parsed_query = self.parser.parse(query)
        self.assertEqual(parsed_query, "MATCH (n) RETURN n")

    def test_parse_query_with_trailing_punctuation_marks(self):
        query = 'MATCH (n) RETURN n;"'
        parsed_query = self.parser.parse(query)
        self.assertEqual(parsed_query, 'MATCH (n) RETURN n')

    def test_parse_empty_query(self):
        query = ""
        with self.assertRaises(ValueError):
            self.parser.parse(query)

    def test_parse_non_string_query(self):
        query = None
        with self.assertRaises(ValueError):
            self.parser.parse(query)

    def test_get_format_instructions(self):
        instructions = self.parser.get_format_instructions()
        expected_instructions = \
        "The output should follow RedisGraph Cypher query formalism."+\
        " Ensure the output can be parsed using RedisGraph Python client."
        self.assertEqual(instructions, expected_instructions)

if __name__ == '__main__':
    unittest.main()