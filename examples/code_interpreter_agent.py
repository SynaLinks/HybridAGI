import dspy
from hybridagi import GraphProgramInterpreter
from hybridagi import SentenceTransformerEmbeddings
from hybridagi import ProgramMemory, AgentState
from hybridagi.tools import (
    CodeInterpreterTool,
    SpeakTool,
)
from pydantic import BaseModel
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

print("Loading LLM & embeddings models...")
student_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n", "\n\n---"])
teacher_llm = dspy.OllamaLocal(model='mistral', max_tokens=1024, stop=["\n\n\n", "\n\n---"])

embeddings = SentenceTransformerEmbeddings(dim=384, model_name_or_path="sentence-transformers/all-MiniLM-L6-v2")

dspy.settings.configure(lm=student_llm)

model_path = "code_interpreter_agent.json"

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
    if pred.finish_reason == "max iters":
        return False
    with dspy.context(lm=teacher_llm):
        prediction = dspy.ChainOfThought(AssessAnswer)(
            assessed_answer = pred.final_answer,
            assessed_question = question,
        )
        # If the agent is stuck in a loop we discard the example
        result = dspy.TypedPredictor(CritiqueToScoreSignature)(critique=prediction.critique)
    return result.score.score

print("Initializing the program memory...")
program_memory = ProgramMemory(
    index_name = "code_interpreter_agent",
    embeddings = embeddings,
    wipe_on_start = True,
)

print("Adding programs into memory...")
program_memory.add_texts(
    texts = [
"""
// @desc: The main program
CREATE
(start:Control {name:"Start"}),
(end:Control {name:"End"}),
(plan_simulation:Action {
    name: "Plannify what to do to implement the code to answer the objective's question",
    tool: "Predict",
    prompt: "Explain what to code to answer the objective's question.
Make sure that your program answer the correct question from the objective"
}),
(simulate:Action {
    name: "Simulate the trajectory of the object using the Jupyter notebook",
    tool: "CodeInterpreter",
    prompt: "
Give me the python code to answer the objective's question.
Remember to always print out the result and to put the code inside a python code quotes
Make sure that your program answer the correct question from the objective"
}),
(is_simulation_correct:Decision {
    name: "Check if the simulation is correct",
    question: "Is the simulation correct? Meaning no error/bug"
}),
(critique:Action {
    name: "Critique the code to help you debugging it",
    tool: "Predict",
    prompt: "Critique the code to help you debugging it, if you don't known where is the bug add print statements to help for debugging"
}),
(answer:Action {
    name: "Answer the objective's question",
    tool: "Speak",
    prompt: "Answer the objective's question using the context's simulation output"
}),
(is_answer_correct:Decision {
    name: "Check if the answer to the objective's question is correct",
    question: "Is the answer correct? make sure the answer correspond"
}),
(start)-[:NEXT]->(plan_simulation),
(plan_simulation)-[:NEXT]->(simulate),
(simulate)-[:NEXT]->(is_simulation_correct),
(critique)-[:NEXT]->(simulate),
(is_simulation_correct)-[:NO]->(critique),
(is_simulation_correct)-[:UNKNOWN]->(critique),
(is_simulation_correct)-[:YES]->(answer),
(answer)-[:NEXT]->(is_answer_correct),
(is_answer_correct)-[:NO]->(simulate),
(is_answer_correct)-[:YES]->(end)
""",
    ],
    ids = [
        "main",
    ]
)

dataset = [
    dspy.Example(objective="An object is thrown upward with an initial velocity of 20 m/s. How long does it take for the object to reach a height of 10 m?").with_inputs("objective"),
    dspy.Example(objective="A car accelerates from 0 to 60 mph in 8 seconds. What is the acceleration of the car in m/s²?").with_inputs("objective"),
    dspy.Example(objective="An object is moving in a straight line with a constant acceleration of 2 m/s². If the object's initial velocity is 5 m/s, what is its velocity after 10 seconds?").with_inputs("objective"),
    dspy.Example(objective="A tank contains 100 L of water at a temperature of 20°C. How much heat energy is required to raise the temperature of the water to 80°C?").with_inputs("objective"),
    dspy.Example(objective="A plane is flying at a constant speed of 600 mph and has enough fuel to fly for 5 hours. What is the maximum distance the plane can fly?").with_inputs("objective"),
    dspy.Example(objective="A pendulum has a length of 1 m and is released from an angle of 30 degrees. What is the pendulum's angular velocity when it reaches the bottom of its swing?").with_inputs("objective"),
    dspy.Example(objective="A block of mass 5 kg is placed on a frictionless inclined plane that makes an angle of 30 degrees with the horizontal. What is the acceleration of the block down the plane?").with_inputs("objective"),
    dspy.Example(objective="A proton and an electron are separated by a distance of 1 nm. What is the electrostatic potential energy of the system?").with_inputs("objective"),
    dspy.Example(objective="A cyclist is riding around a circular track with a radius of 50 m. If the cyclist's speed is constant at 10 m/s, what is the magnitude of their acceleration?").with_inputs("objective"),
    dspy.Example(objective="A satellite is orbiting the Earth in a circular orbit with a radius of 42,000 km. What is the satellite's orbital speed?").with_inputs("objective"),
]

testset = [
    dspy.Example(objective="An object is dropped from a height of 10 m. How long does it take for the object to reach the ground?").with_inputs("objective"),
    dspy.Example(objective="A gas is contained in a cylinder with a movable piston. The gas is heated, causing the piston to move outward and the gas to expand. If the initial pressure of the gas is 100 kPa and the final pressure is 50 kPa, what is the ratio of the final volume to the initial volume?").with_inputs("objective"),
    dspy.Example(objective="A 10 V battery is connected to a 2 Ω resistor. What is the current in the circuit and the power dissipated by the resistor?").with_inputs("objective"),
    dspy.Example(objective="A ball is thrown horizontally with an initial velocity of 15 m/s from a height of 20 m. How long does it take for the ball to hit the ground?").with_inputs("objective"),
    dspy.Example(objective="A block of mass 3 kg is sliding on a horizontal surface with a speed of 4 m/s. If the coefficient of kinetic friction between the block and the surface is 0.2, how far will the block slide before coming to a stop?").with_inputs("objective"),
]

print("Initializing the graph interpreter...")

agent_state = AgentState()

tools = [
    SpeakTool(
        agent_state = agent_state,
    ),
    CodeInterpreterTool()
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
    agent_state = agent_state,
    tools = tools,
    num_history=5,
    max_iters=10, # after 10 steps we consider the agent stuck in a loop
    commit_decision_steps=False, # don't add decision steps in the context (avoid context pollution by decision steps)
    add_final_step=False, # Don't add the final step as we use Speak already
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
