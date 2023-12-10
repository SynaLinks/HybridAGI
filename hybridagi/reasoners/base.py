from pydantic.v1 import BaseModel
from langchain.base_language import BaseLanguageModel
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from ..parsers.reasoner_output_parser import ReasonerOutputParser
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
            ):
        if use_smart_llm:
            chain = LLMChain(
                llm = self.smart_llm,
                prompt = prompt,
                verbose = self.debug,
            )
        else:
            chain = LLMChain(
                llm = self.fast_llm,
                prompt = prompt,
                verbose = self.debug,
            )
        return self.output_parser.parse(chain.run(**args))

    async def async_predict(
                self,
                prompt: str,
                use_smart_llm: bool = False,
                **args,
            ):
        if use_smart_llm:
            chain = LLMChain(
                llm = self.smart_llm,
                prompt = prompt,
                verbose = self.debug,
            )
        else:
            chain = LLMChain(
                llm = self.fast_llm,
                prompt = prompt,
                verbose = self.debug,
            )
        return self.output_parser.parse(await chain.arun(**args))