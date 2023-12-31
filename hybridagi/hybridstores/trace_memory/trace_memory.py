"""The base trace memory. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import uuid
from colorama import Fore, Style
from time import gmtime, strftime
from datetime import datetime
from collections import deque
from .base import BaseTraceMemory
from typing import Optional, Callable, Any, Dict, List
from langchain.schema.embeddings import Embeddings
from ..hybridstore import BaseHybridStore

COLORS = [f"{Fore.BLUE}", f"{Fore.MAGENTA}"]

START_PROGRAM_DESCRIPTION = \
"""Start Program: {program_name}
Program Purpose: {purpose}"""

END_PROGRAM_DESCRIPTION = \
"""End Program: {program_name}"""

ACTION_DESCRIPTION = \
"""Action Purpose: {purpose}
Action: {tool_name}
Action Input: {tool_input}
Action Observation: {tool_observation}"""

DECISION_DESCRIPTION = \
"""Decision Purpose: {purpose}
Decision: {question}
Decision Answer: {decision}"""

def _default_norm(value):
    return value

class TraceMemory(BaseTraceMemory, BaseHybridStore):
    """The trace memory"""
    commit_index_trace: deque = deque()
    current_iteration = 0 # Used to display the trace

    def __init__(
            self,
            index_name: str,
            redis_url: str,
            embeddings: Embeddings,
            embeddings_dim: int,
            normalize: Optional[Callable[[Any], Any]] = _default_norm,
            verbose: bool = True):
        super().__init__(
            index_name = index_name,
            redis_url = redis_url,
            embeddings = embeddings,
            embeddings_dim = embeddings_dim,
            graph_index = "trace_memory",
            indexed_label = "Action",
            normalize = normalize,
            verbose = verbose,
        )

    def get_timestamp(self):
        """Returns a timestamp"""
        return strftime("%Y-%m-%d_%H:%M:%S.%f%z", gmtime())

    def get_commit_time(
            self,
            commit_index: str,
        ) -> Optional[datetime]:
        """Returns the commit timestamp in datetime format"""
        result = self.query(
            'MATCH (n {name:"'+commit_index+'"}) RETURN n.time as time'
        )
        if len(result) > 0:
            date_string = result[0]
            return datetime.strptime(date_string, '%Y-%m-%d_%H:%M:%S.%f%z')
        return None

    def get_current_commit(self) -> str:
        """Returns the current commit index"""
        if len(self.commit_index_trace) > 0:
            return self.commit_index_trace[-1]
        return ""

    def get_next_commit(self, commit_index: str) -> str:
        """Method to return the next content index"""
        result = self.query(
            'MATCH ({name:"'+commit_index+'"})-[:NEXT]->(n) RETURN n')
        if len(result) > 0:
            return result[0][0].properties["name"]
        return ""

    def get_previous_commit(self, commit_index: str) -> str:
        """Method to return the next content index"""
        result = self.query(
            'MATCH (n:Step)-[:NEXT]->(:Step {name:"'+commit_index+'"}) RETURN n')
        if len(result) > 0:
            return result[0][0].properties["name"]
        return ""

    def start_new_trace(self):
        """Start a new trace"""
        self.commit_index_trace = deque()
        self.clear_trace()

    def commit(
            self,
            label: str,
            description: str,
            metadata: Dict[str, Any] = {}
        ):
        """Commit a step of the program into memory"""
        metadata["time"] = self.get_timestamp()
        if label == self.indexed_label:
            indexes = self.add_texts(
                texts = [description],
                metadatas = [metadata],
            )
            new_commit = indexes[0]
        else:
            new_commit = str(uuid.uuid4().hex)
            self.query('MERGE (:'+label+' {name:"'+new_commit+'"})')
            for key, value in metadata.items():
                self.query(
                    'MATCH (n:'+label+' {name:"'+new_commit+'"})'
                    +' SET n.'+str(key)+'='+repr(value))
        current_commit = self.get_current_commit()
        if current_commit:
            self.query('MATCH (n {name:"'+current_commit
                    +'"}), (m {name:"'+new_commit+'"})'
                    +' MERGE (n)-[:NEXT]->(m)')
        self.commit_index_trace.append(new_commit)
        if self.verbose:
            print(COLORS[self.current_iteration%2])
            print(f"{description}{Style.RESET_ALL}")
        self.current_iteration += 1
        return new_commit
        
    def commit_action(
            self,
            purpose: str,
            tool_name: str,
            tool_input: str,
            tool_observation: str,
            metadata: Dict[str, Any] = {},
        ):
        """Commit an action"""
        metadata["program"] = self.current_program
        metadata["objective"] = self.objective
        metadata["note"] = self.note
        action_desc = ACTION_DESCRIPTION.format(
            purpose = purpose,
            tool_name = tool_name,
            tool_input = tool_input,
            tool_observation = tool_observation,
        )
        self.update_trace(action_desc)
        self.commit(
            label = "Action",
            description = action_desc,
            metadata = metadata)

    def commit_decision(
            self,
            purpose: str,
            question: str,
            options: List[str],
            decision: str,
            metadata: Dict[str, Any] = {},
        ):
        """Commit a decision"""
        metadata["purpose"] = purpose
        metadata["program"] = self.current_program
        metadata["question"] = question
        metadata["options"] = options
        metadata["decision"] = decision
        metadata["objective"] = self.objective
        metadata["note"] = self.note
        decision_desc = DECISION_DESCRIPTION.format(
            purpose = purpose,
            question = question,
            choice = " or ".join(options),
            decision = decision,
        )
        self.update_trace(decision_desc)
        self.commit(
            label = "Decision",
            description = decision_desc,
            metadata = metadata)

    def commit_program_start(
            self,
            purpose: str,
            program_name: str,
        ):
        """Commit the starting of a program"""
        metadata = {}
        metadata["purpose"] = purpose
        metadata["program"] = program_name
        metadata["objective"] = self.objective
        metadata["note"] = self.note
        start_desc = START_PROGRAM_DESCRIPTION.format(
            purpose = purpose,
            program_name = program_name,
        )
        self.update_trace(start_desc)
        self.commit(
            label = "StartProgram",
            description = start_desc,
            metadata = metadata)

    def commit_program_end(
            self,
            program_name: str,
        ):
        """Commit the ending of a program"""
        metadata = {}
        metadata["program"] = program_name
        metadata["objective"] = self.objective
        metadata["note"] = self.note
        end_desc = END_PROGRAM_DESCRIPTION.format(
            program_name = program_name,
        )
        self.update_trace(end_desc)
        self.commit(
            label = "EndProgram",
            description = end_desc,
            metadata = metadata)

    def get_trace_indexes(
            self,
        ) -> List[str]:
        """Get the traces indexes (the first commit index of each trace)"""
        trace_indexes = []
        result = self.query('MATCH (n:StartProgram {program:"main"}) RETURN n.name as name')
        for record in result:
            trace_indexes.append(record[0])
        return trace_indexes

    def is_finished(
            self,
            trace_index: str,
        ) -> bool:
        """Returns True if the execution of the program terminated"""
        result = self.query(
            'MATCH (n:StartProgram {name:"'+trace_index+'", program:"main"})'
            +'-[:NEXT*]->(m:EndProgram {program:"main"}) RETURN m')
        if len(result) == 0:
            return False
        return True