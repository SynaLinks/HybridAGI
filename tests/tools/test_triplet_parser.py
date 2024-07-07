import dspy
from hybridagi.tools import TripletParserTool
from dspy.utils.dummies import DummyLM

def test_triplet_parser_tool_with_lm():
    # Test multiple formats and multiple triplets
    answers = [
        """(SynaLinks, is a young French start-up, founded in Toulouse in 2023)""",
        """(Subject: SynaLinks, Predicate: is a, Object: young French start-up)
        (Subject: SynaLinks, Predicate: was founded, Object: in Toulouse in 2023)""",
        """[("Python", "is", "a programming language"), ("JavaScript", "is used for", "web development")]"""
    ]
    expected_results = [
        [("SynaLinks", "is a young French start-up", "founded in Toulouse in 2023")],
        [("SynaLinks", "is a", "young French start-up"), ("SynaLinks", "was founded", "in Toulouse in 2023")],
        [("Python", "is", "a programming language"), ("JavaScript", "is used for", "web development")]
    ]

    for answer, expected in zip(answers, expected_results):
        dspy.settings.configure(lm=DummyLM(answers=[answer]))
        tool = TripletParserTool()

        prediction = tool(
            objective="test objective",
            context="Nothing done yet",
            purpose="test purpose",
            prompt="test prompt",
            disable_inference=False,
        )
        assert prediction.message == expected, f"Failed on input: {answer}\nExpected: {expected}\nGot: {prediction.message}"

def test_triplet_parser_tool_without_lm():
    tool = TripletParserTool()

    # Test cases for different input formats
    test_cases = [
        (
            """[("Capital_of_England", "is equal to", "London"), ("Location_of_Westminster", "is", "London"), ("Part_of_London", "is", "Westminster")]""",
            [("Capital_of_England", "is equal to", "London"), ("Location_of_Westminster", "is", "London"), ("Part_of_London", "is", "Westminster")]
        ),
        (
            """("Paris", "is the capital of", "France")""",
            [("Paris", "is the capital of", "France")]
        ),
        (
            """(Subject: Earth, Predicate: is a, Object: planet)""",
            [("Earth", "is a", "planet")]
        ),
        (
            """[("Water", "boils at", "100 degrees Celsius"), ("Ice", "melts at", "0 degrees Celsius")]""",
            [("Water", "boils at", "100 degrees Celsius"), ("Ice", "melts at", "0 degrees Celsius")]
        )
    ]

    for input_str, expected_output in test_cases:
        prediction = tool(
            objective="test objective",
            context="Nothing done yet",
            purpose="test purpose",
            prompt=input_str,
            disable_inference=True,
        )
        assert prediction.message == expected_output, f"Failed on input: {input_str}"

def test_parse_triplet():
    # Test cases for parse_triplet method
    test_cases = [
        (
            "(Subject: Earth, Predicate: is a, Object: planet)",
            ("Earth", "is a", "planet")
        ),
        (
            "(Paris, is the capital of, France)",
            ("Paris", "is the capital of", "France")
        ),
        (
            "(Subject: Python, Predicate: is, Object: a programming language)",
            ("Python", "is", "a programming language")
        ),
        (
            "(OpenAI, developed, ChatGPT)",
            ("OpenAI", "developed", "ChatGPT")
        ),
        (
            "(Subject: The sun, Predicate: is at the center of, Object: our solar system)",
            ("The sun", "is at the center of", "our solar system")
        ),
        # Test case with newlines and extra spaces
        (
            """(Subject: Machine Learning,
               Predicate: is a subset of,
               Object:    Artificial Intelligence)""",
            ("Machine Learning", "is a subset of", "Artificial Intelligence")
        )
    ]

    for input_str, expected_output in test_cases:
        result = TripletParserTool.parse_triplet(input_str)
        assert result == expected_output, f"Failed on input: {input_str}"

    # Test invalid input
    invalid_inputs = [
        "This is not a triplet",
        "(Only two, parts)",
        "(Too, many, parts, in, this, triplet)",
        "Subject: X, Predicate: Y, Object: Z"  # Missing parentheses
    ]

    for invalid_input in invalid_inputs:
        result = TripletParserTool.parse_triplet(invalid_input)
        assert result is None, f"Should return None for invalid input: {invalid_input}"

def test_parse_triplets():
    # Test multiple triplets in a single string
    multi_triplet_input = """(Subject: SynaLinks, Predicate: is a, Object: young French start-up)
    (Subject: SynaLinks, Predicate: was founded, Object: in Toulouse in 2023)"""
    result = TripletParserTool.parse_triplets(multi_triplet_input)
    expected_output = [
        ("SynaLinks", "is a", "young French start-up"),
        ("SynaLinks", "was founded", "in Toulouse in 2023")
    ]
    assert result == expected_output, f"Failed on multi-triplet input:\nExpected: {expected_output}\nGot: {result}"

    # Test nested list structure
    nested_list_input = '''[["SynaLinks", "is a young French start-up founded in Toulouse in 2023"], ["SynaLinks", "has a mission to promote a responsible and pragmatic approach to general artificial intelligence"]]'''
    result = TripletParserTool.parse_triplets(nested_list_input)
    expected_output = [
        ("SynaLinks", "is a young French start-up founded in Toulouse in 2023", ""),
        ("SynaLinks", "has a mission to promote a responsible and pragmatic approach to general artificial intelligence", "")
    ]
    assert result == expected_output, f"Failed on nested list input:\nExpected: {expected_output}\nGot: {result}"
    
    # Test nested list structure
    nested_list_input = '''[["SynaLinks", "is", "a young French start-up founded in Toulouse in 2023"], ["SynaLinks", "has", "a mission to promote a responsible and pragmatic approach to general artificial intelligence"]'''
    result = TripletParserTool.parse_triplets(nested_list_input)
    expected_output = [
        ("SynaLinks", "is", "a young French start-up founded in Toulouse in 2023"),
        ("SynaLinks", "has", "a mission to promote a responsible and pragmatic approach to general artificial intelligence")
    ]
    assert result == expected_output, f"Failed on poorly formatted input:\nExpected: {expected_output}\nGot: {result}"    

    # Test poorly formatted input
    poorly_formatted_input = '''[["SynaLinks", "is a young French start-up founded in Toulouse in 2023"], ["SynaLinks", "has a mission to promote a responsible and pragmatic approach to general artificial intelligence"]'''
    result = TripletParserTool.parse_triplets(poorly_formatted_input)
    expected_output = [
        ("SynaLinks", "is a young French start-up founded in Toulouse in 2023", ""),
        ("SynaLinks", "has a mission to promote a responsible and pragmatic approach to general artificial intelligence", "")
    ]
    assert result == expected_output, f"Failed on poorly formatted input:\nExpected: {expected_output}\nGot: {result}"