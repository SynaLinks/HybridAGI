from pydantic.v1 import BaseModel
from langchain.base_language import BaseLanguageModel
from langchain.prompts import PromptTemplate
from ..parsers.reasoner import ReasonerOutputParser
from ..hybridstores.trace_memory.trace_memory import TraceMemory

class BaseReasoner(BaseModel):
    trace_memory: TraceMemory

    smart_llm: BaseLanguageModel
    fast_llm: BaseLanguageModel

    smart_llm_max_token: int
    fast_llm_max_token: int

    debug: bool = False
    verbose: bool = False

    output_parser: ReasonerOutputParser = ReasonerOutputParser()

    def predict(
                self,
                prompt: PromptTemplate,
                use_smart_llm: bool = False,
                **args,
            ) -> str:
        if use_smart_llm:
            chain = prompt | self.smart_llm
        else:
            chain = prompt | self.fast_llm
        return self.output_parser.parse(chain.invoke(input=args).content)

    async def async_predict(
                self,
                prompt: str,
                use_smart_llm: bool = False,
                **args,
            ) -> str:
        if use_smart_llm:
            chain = prompt | self.smart_llm
        else:
            chain = prompt | self.fast_llm
        return self.output_parser.parse((await chain.ainvoke(input=args)).content)