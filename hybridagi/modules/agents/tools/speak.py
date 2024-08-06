import dspy
import copy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    AgentState,
    Message,
    ToolInput,
)
from hybridagi.output_parsers import PredictionOutputParser

class SpeakSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    message = dspy.OutputField(desc = "The message")

class SpeakOutput(dspy.Prediction):
    message: str
    
    def to_dict(self):
        return {"message": self.message}

class SpeakTool(Tool):
    def __init__(
            self,
            agent_state: AgentState,
            name: str = "Speak",
            speak_func: Optional[Callable[[str], None]] = None,
            simulated: bool = True,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = name, lm = lm)
        self.predict = dspy.Predict(SpeakSignature)
        self.simulated = simulated
        self.agent_state = agent_state
        self.speak_func = speak_func
        self.prediction_parser = PredictionOutputParser()
        
    def speak(self, message: str):
        if self.speak_func:
            return self.speak_func(message)
        else:
            raise ValueError(
                "You should specify a function to call to use `Speak` outside simulation"
            )
    
    def forward(self, tool_input: ToolInput) -> SpeakOutput:
        if not isinstance(tool_input, ToolInput):
            raise ValueError(f"{type(self).__name__} input must be a ToolInput")
        if not tool_input.disable_inference:
            with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
                pred = self.predict(
                    objective = tool_input.objective,
                    context = tool_input.context,
                    purpose = tool_input.purpose,
                    prompt = tool_input.prompt,
                )
            pred.message = self.prediction_parser.parse(
                pred.message,
                prefix = "Message:",
            )
            pred.message = pred.message.strip("\"")
            self.agent_state.session.chat.msgs.append(Message(role="AI", content=pred.message))
            self.agent_state.final_answer = pred.message
            if self.simulated is False:
                self.speak(pred.message)
            return SpeakOutput(
                message = pred.message
            )
        else:
            self.agent_state.session.chat.msgs.append(Message(role="AI", content=tool_input.prompt))
            self.agent_state.final_answer = tool_input.prompt
            if self.simulated is False:
                self.speak(tool_input.prompt)
            return SpeakOutput(
                message = tool_input.prompt,
            )
    
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            agent_state = self.agent_state,
            name = self.name,
            speak_func = self.speak_func,
            simulated = self.simulated,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy