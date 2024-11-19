import dspy
from hybridagi.core.datatypes import Document
from hybridagi.modules.extractors import GraphProgramExtractor

def test_graph_program_extractor():
    plan = \
"""
1. Action: Use `Predict` tool to generate a list of common themes in AI poetry such as intelligence, consciousness, evolution, and human-machine interaction.
2. Action: Use `DocumentSearch` tool to find existing examples of AI poems for inspiration and understanding the style and tone commonly used.
3. Action: Use `Predict` tool the generated themes with the insights from the found examples to create a unique structure for the poem.
4. Action: Use `Predict` tool the chosen structure to write the first draft of the poem using simple, evocative language that captures the essence of AI.
5. Action: Use `Predict` tool to review and refine the draft by making adjustments as needed to ensure it effectively conveys the intended message about AI.
6. Action: Once satisfied with the final version, use `Speak` tool to present the completed poem to the user as the answer.
"""
    doc = Document(text=plan)
    
    lm = dspy.OllamaLocal(model='mistral', experimental=True, max_tokens=1024, stop=["\n\n\n"])
    dspy.configure(lm=lm)
    
    graph_program_extractor = GraphProgramExtractor()
    
    result = graph_program_extractor(doc)
    print(result)
    raise ValueError("")