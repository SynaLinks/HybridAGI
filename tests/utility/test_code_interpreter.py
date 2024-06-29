from hybridagi import CodeInterpreterUtility

# def test_code_interpreter_hello_world():
#     interpreter = CodeInterpreterUtility()

#     code = \
# """
# print("Hello world")
# """
#     code, output, err = interpreter.execute_code(code)
#     print("code:"+code)
#     assert output == "Hello world"
#     assert not err

def test_code_interpreter_math_import():
    interpreter = CodeInterpreterUtility()

    code = \
"""
import math

a = math.sqrt(2)

print(f"The result is {a}")
"""
    code, output, err = interpreter.execute_code(code)
    assert output == "1.4142135623730951"
    assert not err

def test_code_interpreter_functions():
    interpreter = CodeInterpreterUtility()

    code = \
"""
import math

def calculate_a():
    a = math.sqrt(2)

a = calculate_a()
print(f"The result is {a}")
"""
    code, output, err = interpreter.execute_code(code)
    print(code, output, err)
    assert output == "1.4142135623730951"
    assert not err