import dspy

class GraphInterpreterAgent(dspy.Module):
    
    def forward(query_or_query_with_session: Union[Query, QueryWithSession]) -> AgentOutput:
        pass
        #TODO