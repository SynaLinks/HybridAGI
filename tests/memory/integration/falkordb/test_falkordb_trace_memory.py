# import pytest
# import uuid
# from hybridagi.memory.integration.falkordb.falkordb_trace_memory import FalkorDBTraceMemory
# from hybridagi.core.datatypes import AgentStep, AgentStepList, AgentStepType
# from hybridagi.embeddings.fake import FakeEmbeddings

# def test_add_and_get_step(memory):
#     step = AgentStep(
#         id=uuid.uuid4(),
#         step_type=AgentStepType.Action,
#         name="Test Step",
#         description="This is a test step",
#         vector=[0.1, 0.2, 0.3]
#     )
#     memory.add(step)

#     retrieved_steps = memory.get(step.id)
#     assert len(retrieved_steps.steps) == 1
#     assert retrieved_steps.steps[0].id == step.id
#     assert retrieved_steps.steps[0].name == step.name

# def test_update_step(memory):
#     step = AgentStep(
#         id=uuid.uuid4(),
#         step_type=AgentStepType.Action,
#         name="Original Step",
#         description="This is the original step",
#         vector=[0.1, 0.2, 0.3]
#     )
#     memory.add(step)

#     updated_step = AgentStep(
#         id=step.id,
#         step_type=AgentStepType.Decision,
#         name="Updated Step",
#         description="This is the updated step",
#         vector=[0.4, 0.5, 0.6]
#     )
#     memory.update(updated_step)

#     retrieved_steps = memory.get(step.id)
#     assert len(retrieved_steps.steps) == 1
#     assert retrieved_steps.steps[0].name == "Updated Step"
#     assert retrieved_steps.steps[0].step_type == AgentStepType.Decision

# def test_remove_step(memory):
#     step = AgentStep(
#         id=uuid.uuid4(),
#         step_type=AgentStepType.Action,
#         name="Step to Remove",
#         description="This step will be removed",
#         vector=[0.1, 0.2, 0.3]
#     )
#     memory.add(step)
#     memory.remove(step.id)

#     retrieved_steps = memory.get(step.id)
#     assert len(retrieved_steps.steps) == 0

# def test_search(memory):
#     steps = [
#         AgentStep(
#             id=uuid.uuid4(),
#             step_type=AgentStepType.Action,
#             name=f"Step {i}",
#             description=f"This is step {i}",
#             vector=[0.1] * 250  # Use the same dimension as FakeEmbeddings
#         ) for i in range(5)
#     ]
#     memory.add_many(AgentStepList(steps=steps))

#     # Add a step that should match the search query
#     matching_step = AgentStep(
#         id=uuid.uuid4(),
#         step_type=AgentStepType.Action,
#         name="Matching Step",
#         description="This step contains the test query",
#         vector=[0.1] * 250
#     )
#     memory.add(matching_step)

#     search_results = memory.search("test query", k=3)
#     assert len(search_results.steps) > 0
#     assert any(step.name == "Matching Step" for step in search_results.steps)
#     for step in search_results.steps:
#         assert isinstance(step, AgentStep)
#         assert step.vector is not None

# def test_get_full_trace(memory):
#     steps = []
#     for i in range(5):
#         step = AgentStep(
#             id=uuid.uuid4(),
#             step_type=AgentStepType.Action,
#             name=f"Step {i}",
#             description=f"This is step {i}",
#             vector=[0.1 * i, 0.2 * i, 0.3 * i],
#             parent_id=steps[i-1].id if i > 0 else None
#         )
#         steps.append(step)
#     memory.add_many(AgentStepList(steps=steps))

#     full_trace = memory.get_full_trace()
#     assert len(full_trace.steps) == 5
#     step_names = set(step.name for step in full_trace.steps)
#     assert step_names == set(f"Step {i}" for i in range(5))

# def test_clear(memory):
#     steps = [
#         AgentStep(
#             id=uuid.uuid4(),
#             step_type=AgentStepType.Action,
#             name=f"Step {i}",
#             description=f"This is step {i}",
#             vector=[0.1 * i, 0.2 * i, 0.3 * i]
#         ) for i in range(3)
#     ]
#     memory.add_many(AgentStepList(steps=steps))

#     memory.clear()
#     full_trace = memory.get_full_trace()
#     assert len(full_trace.steps) == 0
