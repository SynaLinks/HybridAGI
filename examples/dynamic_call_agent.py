import dspy
import os
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory, TraceMemory, FileSystem, AgentState
from hybridagi.tools import (
    DuckDuckGoSearchTool,
    ProgramSearchTool,
    DocumentSearchTool,
    CallProgramTool,
    InternalShellTool,
    WriteFileTool,
    AppendFileTool,
    ReadFileTool,
    SpeakTool,
    AskUserTool,
    UpdateObjectiveTool,
    UploadTool,
)
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n", "\n\n---\n"])
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n", "\n\n---\n"])

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "dynamic_call_agent.json"

class AssessAnswer(dspy.Signature):
    """Assess the success of the trace according to the objective"""
    assessed_answer = dspy.InputField(desc="The answer to assess")
    assessed_question = dspy.InputField(desc="The question to be assessed")
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
        prediction = dspy.ChainOfThought(AssessAnswer)(
            assessed_answer = pred.final_answer,
            assessed_question = question,
        )
        result = dspy.TypedPredictor(CritiqueToScoreSignature)(critique=prediction.critique)
    return result.score.score

print("Initializing the program memory...")
program_memory = ProgramMemory(
    index_name = "dynamic_call_agent",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Initializing the trace memory...")
trace_memory = TraceMemory(
    index_name = "dynamic_call_agent",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Initializing the filesystem...")
filesystem = FileSystem(
    index_name = "dynamic_call_agent",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Adding programs into memory...")

program_memory.add_folders(["examples/primitives"])

program_memory.add_texts(
    texts = [
"""
// @desc: Try to call an existing program to fulfill the objective
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(program_search:Action {
    name:"Search for existing routine to fulfill the objective", 
    tool:"ProgramSearch",
    prompt:"Use the objective to describe in ONE short sentence the action to take"
}),
(is_program_known:Decision {
    name: "Check if the routine to fulfill the objective is in the previous search",
    question: "Is the routine to fulfill the objective in the above search?"
}),
(call_program:Action {
    name:"Pick the most appropriate routine from the previous search", 
    tool:"CallProgram",
    prompt:"Use the context to known which program to pick. Only infer the name of the program without addtionnal details."
}),
(start)-[:NEXT]->(program_search),
(program_search)-[:NEXT]->(is_program_known),
(is_program_known)-[:YES]->(call_program),
(is_program_known)-[:NO]->(end),
(call_program)-[:NEXT]->(end)
""",
"""
// @desc: Try to call an existing program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(is_objective_question:Decision {
    name: "Check if the objective is a question or an instruction",
    question: "Choose between INSTRUCTION or QUESTION using the objective"
}),
(answer:Action {
    name: "Answer the objective's question",
    tool: "Predict",
    prompt: "Answer the objective's question"
}),
(fulfill_objective:Program {
    name: "Fullfil the objective",
    program: "fulfill_objective"
}),
(start)-[:NEXT]->(is_objective_question),
(is_objective_question)-[:QUESTION]->(answer),
(is_objective_question)-[:INSTRUCTION]->(fulfill_objective),
(fulfill_objective)-[:NEXT]->(end),
(answer)-[:NEXT]->(end)
""",
    ],
    ids = [
        "fulfill_objective",
        "main",
    ]
)

dataset = [
    dspy.Example(objective="Create a folder called Test").with_inputs("objective"),
    dspy.Example(objective="Write a poem about AI and nature into a file called poem.txt").with_inputs("objective"),
    dspy.Example(objective="What is a neuro-symbolic artificial intelligence?").with_inputs("objective"),
    dspy.Example(objective="Write a python script for a snake game into a file").with_inputs("objective"),
    dspy.Example(objective="Navigate into the folder Test").with_inputs("objective"),
    dspy.Example(objective="List the Test directory").with_inputs("objective"),
    dspy.Example(objective="Read the file called poem.txt").with_inputs("objective"),
    dspy.Example(objective="What is a neuro-symbolic artificial intelligence?").with_inputs("objective"),
    dspy.Example(objective="List your home directory").with_inputs("objective"),
    dspy.Example(objective="List the Test directory").with_inputs("objective"),
]

testset = [
    dspy.Example(objective="Write a poem into a .txt file").with_inputs("objective"),
    dspy.Example(objective="What is a neuro-symbolic artificial intelligence?").with_inputs("objective"),
    dspy.Example(objective="Search for HybridAGI on internet").with_inputs("objective"),
    dspy.Example(objective="Print the current working directory").with_inputs("objective"),
    dspy.Example(objective="List the Test folder in you filesystem").with_inputs("objective"),
]

print("Initializing the graph interpreter...")

agent_state = AgentState()

tools = [
    DuckDuckGoSearchTool(),
    ProgramSearchTool(
        program_memory = program_memory,
        embeddings = embeddings,
    ),
    DocumentSearchTool(
        filesystem = filesystem,
        embeddings = embeddings,
    ),
    CallProgramTool(
        program_memory = program_memory,
        agent_state = agent_state,
    ),
    InternalShellTool(
        filesystem = filesystem,
        agent_state = agent_state,
    ),
    WriteFileTool(
        filesystem = filesystem,
        agent_state = agent_state,
    ),
    AppendFileTool(
        filesystem = filesystem,
        agent_state = agent_state,
    ),
    ReadFileTool(
        filesystem = filesystem,
        agent_state = agent_state,
    ),
    UploadTool(
        filesystem = filesystem,
        agent_state = agent_state,
    ),
    SpeakTool(
        agent_state = agent_state,
    ),
    AskUserTool(
        agent_state = agent_state,
    ),
]

print("Optimizing underlying prompts...")

config = dict(max_bootstrapped_demos=4, max_labeled_demos=0)

optimizer = BootstrapFewShotWithRandomSearch(
    num_threads = 1,
    teacher_settings=dict({'lm': teacher_llm}),
    metric = program_success,
    **config,
)

interpreter = GraphProgramInterpreter(
    program_memory = program_memory,
    trace_memory = trace_memory,
    agent_state = agent_state,
    tools = tools,
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