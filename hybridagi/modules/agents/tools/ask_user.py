import dspy
import json
import copy
from .tool import Tool
from typing import Optional, Callable
from hybridagi.core.datatypes import (
    ToolInput,
    AgentState,
    Message,
)
from hybridagi.output_parsers import PredictionOutputParser

class AskUserSignature(dspy.Signature):
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    question = dspy.OutputField(desc = "The question to ask to the user")
    
class SimulateAnswerSignature(dspy.Signature):
    """Answer from the perspective of the user, if you don't known imagine what a user with the given profile would answer"""
    user_profile = dspy.InputField(desc = "The user profile")
    chat_history = dspy.InputField(desc = "The chat history")
    user_answer = dspy.OutputField(desc = "The answer from the perspective of the user (only few words)")

class AskUserOutput(dspy.Prediction):
    question: str
    answer: str
    
    def to_dict(self):
        return {"question": self.question, "answer": self.answer}

class AskUserTool(Tool):
    def __init__(
            self,
            agent_state: AgentState,
            name: str = "AskUser",
            ask_user_func: Optional[Callable[[str], str]] = None,
            simulated: bool = True,
            lm: Optional[dspy.LM] = None,
        ):
        super().__init__(name = name, lm = lm)
        self.predict = dspy.Predict(AskUserSignature)
        self.prediction_parser = PredictionOutputParser()
        self.simulated = simulated
        self.simulate = dspy.Predict(SimulateAnswerSignature)
        self.agent_state = agent_state
        self.ask_user_func = ask_user_func
        
    def ask_user(self, question : str) -> str:
        if self.ask_user_func:
            return self.ask_user_func(question)
        else:
            raise ValueError(
                "You should specify a function to call to use `AskUser` outside simulation")
            
    def simulate_ask_user(self, question: str):
        chat_history = json.dumps(self.agent_state.session.chat.to_dict(), indent=2)
        with dspy.context(lm=self.lm if self.lm is not None else dspy.settings.lm):
            pred = self.simulate(
                user_profile = self.agent_state.session.user.profile,
                chat_history = chat_history,
            )
        pred.answer = self.prediction_parser.parse(
            pred.user_answer,
            prefix = "Answer:",
        )
        pred.answer = pred.answer.strip("\"")
        return pred.answer
        
    def forward(self, tool_input: ToolInput) -> AskUserOutput:
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
            pred.question = self.prediction_parser.parse(
                pred.question,
                prefix = "Question:",
            )
            pred.question = pred.question.strip("\"")
            self.agent_state.session.chat.msgs.append(Message(role="AI", content=pred.question))
            if self.simulated:
                answer = self.simulate_ask_user(pred.question)
            else:
                answer = self.ask_user(pred.question)
            self.agent_state.session.chat.msgs.append(Message(role="User", content=answer))
            return AskUserOutput(
                question = pred.question,
                answer = answer,
            )
        else:
            self.agent_state.session.chat.msgs.append(Message(role="AI", content=tool_input.prompt))
            if self.simulated:
                answer = self.simulate_ask_user(tool_input.prompt)
            else:
                answer = self.ask_user(tool_input.prompt)
            self.agent_state.session.chat.msgs.append(Message(role="User", content=answer))
            return AskUserOutput(
                question = tool_input.prompt,
                answer = answer,
            )
            
    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            agent_state = self.agent_state,
            name = self.name,
            ask_user_func = self.ask_user_func,
            simulated = self.simulated,
            lm = self.lm,
        )
        cpy.predict = copy.deepcopy(self.predict)
        cpy.simulate = copy.deepcopy(self.simulate)
        return cpy