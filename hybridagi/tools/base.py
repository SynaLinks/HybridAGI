import abc
import dspy
from typing import Optional, Union, Callable, Dict, Any
from dspy.signatures.signature import ensure_signature

class BaseTool(dspy.Module):

    def __init__(
            self,
            name: str,
            lm: Optional[dspy.LM] = None,
        ):
        self.name = name
        self.lm = lm

    @abc.abstractmethod
    def forward(
            self,
            trace: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
        ) -> dspy.Prediction:
        pass

class Tool(BaseTool):

    def __init__(
            self,
            name: str,
            signature: Union[str, dspy.Signature],
            func: Callable[..., Dict[Any, Any]],
            instructions: str = "",
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name=name, lm=lm)
        self.signature = signature = ensure_signature(signature)

        self.input_fields = self.signature.input_fields
        self.output_fields = self.signature.output_fields

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

        for k in self.input_fields.keys():
            signature_dict[k] = dspy.OutputField(
                prefix = k.title()+":",
            )

        outputs = ", ".join([f"`{k}`" for k in self.input_fields.keys()])

        instr = []
        if instructions:
            instr = [instructions]

        instr.extend([
            "You will be given an objective, purpose and context",
            f"Using the prompt to help you, you will infer the correct {outputs}"
        ])

        instr = "\n".join(instr)
        self.predict = dspy.Predict(dspy.Signature(signature_dict, instr))
        self.func = func

    def forward(
            self,
            context: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
        ):
        if not disable_inference:
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    objective = objective,
                    context = context,
                    purpose = purpose,
                    prompt = prompt,
                )
            args = {}
            for k in self.input_fields.keys():
                args[k] = pred[k]
            result = self.func(**args)
            args.update(result)
            return dspy.Prediction(
                **args
            )
        else:
            raise NotImplementedError("Tool does not support disabling inferences")

