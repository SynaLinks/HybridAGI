# This example is here to illustrate the capability of the system to simulate user interaction to optimize the quality of the interaction
# This example first clarify the objective given by the user, then update the AI objective and answer it

import os
import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory, AgentState
from hybridagi.tools import (
    SpeakTool,
    AskUserTool,
    UpdateObjectiveTool,
)
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShot

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n"])
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n"])

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "rag_that_clarify_question.json"

class AssessInteraction(dspy.Signature):
    """Assess the success of the trace according to the objective"""
    assessed_interaction = dspy.InputField(desc="The interaction to assess")
    critique = dspy.OutputField(desc="The critique of the answer")

class Score(BaseModel):
    score: float

class CritiqueToScoreSignature(dspy.Signature):
    """Convert a critique into a score between 0.0 and 1.0"""
    critique = dspy.InputField(desc="The critique to convert into a score")
    score: Score = dspy.OutputField(desc="A score between 0.0 and 1.0")

def program_success(example, pred, trace=None):
    question = example.objective
    with dspy.context(lm=teacher_llm):
        prediction = dspy.ChainOfThought(AssessInteraction)(
            assessed_interaction = pred.final_answer,
            assessed_question = question,
        )
        result = dspy.TypedPredictor(CritiqueToScoreSignature)(critique=prediction.critique)
    return result.score.score

print("Initializing the program memory...")
program_memory = ProgramMemory(
    index_name = "rag_that_clarify_question",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Adding Cypher programs into the program memory...")
program_memory.add_texts(
    texts = [
"""
// @desc: The main program
// Nodes declaration
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(clarify_objective:Program {
    name:"Clarify the objective if needed",
    program:"clarify_objective"
}),
(answer:Action {
    name:"Answer the objective's question",
    tool:"Speak",
    prompt:"Answer the objective's question"
}),
// Structure declaration
(start)-[:NEXT]->(clarify_objective),
(clarify_objective)-[:NEXT]->(answer),
(answer)-[:NEXT]->(end)
""",
"""
// @desc: Clarify the objective if needed
CREATE
// Nodes declaration
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(is_anything_unclear:Decision {
    name:"Check if the objective is unclear", 
    question:"Is the objective still unclear?"
}),
(ask_question:Action {
    name:"Ask question to clarify the objective",
    tool:"AskUser",
    prompt:"Pick one question to clarify the Objective"
}),
(refine_objective:Action {
    name:"Clarify the given objective",
    tool:"UpdateObjective", 
    prompt:"Clarify the objective based on the user answer"
}),
// Structure declaration
(start)-[:NEXT]->(is_anything_unclear),
(ask_question)-[:NEXT]->(refine_objective),
(refine_objective)-[:NEXT]->(is_anything_unclear),
(is_anything_unclear)-[:YES]->(ask_question),
(is_anything_unclear)-[:MAYBE]->(ask_question),
(is_anything_unclear)-[:NO]->(end)
"""
    ],
    ids = ["main", "clarify_objective"]
)

dataset = [
    dspy.Example(objective="Can you tell me how to be successful and be happy?").with_inputs("objective"),
    dspy.Example(objective="What's the meaning of life?").with_inputs("objective"),
    dspy.Example(objective="What's the key to improve?").with_inputs("objective"),
    dspy.Example(objective="Wander the winding paths of words, where each turn may lead to a new interpretation, a new revelation, or a new puzzle to solve.").with_inputs("objective"),
    dspy.Example(objective="I want to make a snake python game").with_inputs("objective"),
    dspy.Example(objective="Are there any potential risks or obstacles we should be aware of?").with_inputs("objective"),
    dspy.Example(objective="What's the best way to travel on a budget?").with_inputs("objective"),
    dspy.Example(objective="How do I achieve work-life balance?").with_inputs("objective"),
    dspy.Example(objective="Can you explain Pythagoras theorem?").with_inputs("objective"),
    dspy.Example(objective="What's the key to a fulfilling life?").with_inputs("objective"),
]

testset = [
    dspy.Example(objective="What's the best way to improve my life?").with_inputs("objective"),
    dspy.Example(objective="What's the meaning of life?").with_inputs("objective"),
    dspy.Example(objective="When did the French Revolution occur?").with_inputs("objective"),
    dspy.Example(objective="How can I be happy?").with_inputs("objective"),
    dspy.Example(objective="What is the recipe of lasagna?").with_inputs("objective"),
]

agent_state = AgentState()

tools = [
    AskUserTool(
        agent_state = agent_state,
    ),
    SpeakTool(
        agent_state = agent_state,
    ),
    UpdateObjectiveTool(
        agent_state = agent_state,
    ),
]

print("Optimizing underlying prompts...")

config = dict(max_bootstrapped_demos=4, max_labeled_demos=0)

optimizer = BootstrapFewShot(
    teacher_settings=dict({'lm': teacher_llm}),
    metric = program_success,
    **config,
)

# we choose to not output a final answer and use the speak tool instead giving us more control over the interaction
interpreter = GraphProgramInterpreter(
    program_memory = program_memory,
    agent_state = agent_state,
    tools = tools,
    return_final_answer = False,
)

compiled_interpreter = optimizer.compile(
    interpreter,
    trainset=dataset,
    valset=testset,
)

evaluate = dspy.evaluate.Evaluate(
    devset = testset,
    metric = program_success,
    num_threads = 1,
    display_progress = True,
    display_table = 0,
)

print("Evaluate baseline model")
try:
    baseline_score = evaluate(interpreter)
except Exception:
    baseline_score = 0.0
print("Evaluate optimized model")
try:
    eval_score = evaluate(compiled_interpreter)
except Exception:
    eval_score = 0.0

print(f"Baseline: {baseline_score}")
print(f"Score: {eval_score}")

print(f"Save optimized model to '{model_path}'")
compiled_interpreter.save(model_path)