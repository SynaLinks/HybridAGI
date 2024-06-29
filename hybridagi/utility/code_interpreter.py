import re
import builtins
import io
from .python_interpreter import CodePrompt, PythonInterpreter

DEFAULT_WHITELIST = [
    "numpy",
    "math",
]

class PrintWrapper(io.StringIO):
  def __call__(self, *args, **kwargs):
    # Pass the object instance (self) as the file
    return builtins.print(*args, file=self, **kwargs)

class CodeInterpreterUtility():

    def __init__(self, import_white_list=DEFAULT_WHITELIST):
        self.import_white_list = import_white_list

    def parse_code(self, code: str):
        code_match = re.search(r"```python[ \n](.*?)[ \n]```?", code, re.DOTALL)
        code_block = (code_match.group(1) if code_match else code).replace("\\n", "\n")
        if not code_block:
            return code, "Error: Empty code after parsing."
        if "\n" not in code_block and code_block.count("=") > 1:
            return code, "Error: Code format is not correct."
        lines = code_block.split("\n")
        last_line_match = re.match(r"^(\w+)\s*=", lines[-1].strip())
        if last_line_match and len(lines) > 1:
            code_block += "\n" + last_line_match.group(1)
        else:
            code_block = re.sub(
                r"([a-zA-Z_]\w* *=.*?)(?=[a-zA-Z_]\w* *=)", r"\1\n", code_block,
            )
            code_block = re.sub(
                r"([a-zA-Z_]\w* *=.*?)([a-zA-Z_]\w*)$", r"\1\n\2", code_block,
            )
        return code_block, None

    def execute_code(self, code: str):
        parsed_code, error = self.parse_code(code)
        if error:
            return code, None, error
        if not code:
            return code, None, "Error: Empty code before execution."
        code_prompt = CodePrompt(code, code_type="python")
        # print = PrintWrapper()
        interpreter = PythonInterpreter(action_space={}, import_white_list=self.import_white_list)
        try:
            output = str(code_prompt.execute(interpreter=interpreter)[0])
            # msg = print.getvalue()
            return code, output, None
        except Exception as e:
            return code, None, str(e)