import dspy
import inspect
from hybridagi.core.datatypes import ToolInput
from typing import Optional, Callable, Any
from .tool import Tool

class FunctionToolOutput(dspy.Prediction):
    
    def __init__(self, **kwargs):
        dspy.Prediction.__init__(self, **kwargs)
    
    def to_dict(self):
        return dict(self)

class FunctionTool(Tool):
    
    def __init__(
            self,
            name: str,
            func: Callable,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(lm = lm, name = name)
        signature_dict = {}
        signature_dict["objective"] = dspy.InputField(
            prefix = "Objective:",
            desc = "The long-term objective (what you are doing)",
        )
        signature_dict["context"] = dspy.InputField(
            prefix = "Context:",
            desc = "The previous actions (what you have done)",
        )
        signature_dict["purpose"] = dspy.InputField(
            prefix = "Purpose:",
            desc = "The purpose of the action (what you have to do now)",
        )
        signature_dict["prompt"] = dspy.InputField(
            prefix = "Prompt:",
            desc = "The action specific instructions (How to do it)",
        )
        
        func_signature = inspect.signature(func)
        
        for param in func_signature.parameters:
            if not isinstance(param, str):
                raise ValueError(f"{type(self).__name__} function calling only support string inputs")
            signature_dict[param] = dspy.OutputField(prefix=param.title()+":")
            
        docstring = func.__doc__
        if docstring is not None:
            instr = docstring.strip()
            self.predict = dspy.Predict(dspy.Signature(signature_dict, instr))
        else:
            self.predict = dspy.Predict(dspy.Signature(signature_dict))
        self.func = func
        
    def forward(self, tool_input: ToolInput) -> FunctionToolOutput:
        if not tool_input.disable_inference:
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    objective = tool_input.objective,
                    context = tool_input.context,
                    purpose = tool_input.purpose,
                    prompt = tool_input.prompt,
                )
            args = {}
            for param in inspect.signature(self.func).parameters:
                args[param] = pred[param]
            result = self.func(**args)
            return FunctionToolOutput(
                **result
            )
        else:
            raise NotImplementedError(f"{type(self).__name__} doesn't support disabling inference")