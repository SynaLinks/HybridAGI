# This example is here to illustrate the capability of the system to simulate user interaction to optimize the quality of the interaction
# This example first clarify the objective given by the user, then update the AI objective and answer it

import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory, FileSystem, TraceMemory, AgentState
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

print("Initializing the internal filesystem...")
filesystem = FileSystem(
    index_name = "rag_that_clarify_question",
    embeddings = embeddings,
)

print("Initializing the trace memory...")
trace_memory = TraceMemory(
    index_name = "rag_that_clarify_question",
    embeddings = embeddings,
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
    name:"Find out if there is anything unclear in the Objective", 
    question:"Is the Objective unclear?"
}),
(ask_question:Action {
    name:"Ask question to clarify the objective",
    tool:"AskUser",
    prompt:"Pick one question to clarify the Objective"
}),
(refine_objective:Action {
    name:"Clarify the given objective",
    tool:"UpdateObjective", 
    prompt:"The refined Objective"
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
    dspy.Example(objective="What is the definition of machine learning?").with_inputs("objective"),
    dspy.Example(objective="Who made significant contributions to the field of quantum computing?").with_inputs("objective"),
    dspy.Example(objective="Explain me what is a Large Language Model").with_inputs("objective"),
    dspy.Example(objective="What is a neuro-symbolic artificial intelligence?").with_inputs("objective"),
    dspy.Example(objective="When did the French Revolution occur?").with_inputs("objective"),
    dspy.Example(objective="Can you explain the difference between Deep Learning and Symbolic AI?").with_inputs("objective"),
    dspy.Example(objective="Can you explain the concept of blockchain technology?").with_inputs("objective"),
    dspy.Example(objective="What ethical considerations should be taken into account regarding the integration of AI into various job sectors?").with_inputs("objective"),
    dspy.Example(objective="Can you explain Pythagoras theorem?").with_inputs("objective"),
    dspy.Example(objective="What is a blockchain?").with_inputs("objective"),
]

testset = [
    dspy.Example(objective="Can you explain the concept of blockchain technology?").with_inputs("objective"),
    dspy.Example(objective="Does the lasagna contains tomatoes?").with_inputs("objective"),
    dspy.Example(objective="When did the French Revolution occur?").with_inputs("objective"),
    dspy.Example(objective="What is a blockchain?").with_inputs("objective"),
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

config = dict(max_bootstrapped_demos=4, max_labeled_demos=4)

optimizer = BootstrapFewShot(
    teacher_settings=dict({'lm': teacher_llm}),
    metric = program_success,
    **config,
)

# we choose to not output a final answer and use the speak tool instead giving us more control over the interaction
interpreter = GraphProgramInterpreter(
    program_memory = program_memory,
    trace_memory = trace_memory,
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

filesystem.clear()
print("Evaluate baseline model")
baseline_score = evaluate(interpreter)

filesystem.clear()
print("Evaluate optimized model")
eval_score = evaluate(compiled_interpreter)

print(f"Baseline: {baseline_score}")
print(f"Score: {eval_score}")

print(f"Save optimized model to '{model_path}'")
compiled_interpreter.save(model_path)