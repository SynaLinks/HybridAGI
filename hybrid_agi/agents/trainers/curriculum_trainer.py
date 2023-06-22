"""The curriculum trainer. Copyright (C) 2023 SynaLinks. License: GPLv3"""

from colorama import Fore
from colorama import Style
from langchain.base_language import BaseLanguageModel
from langchain.chains.llm import LLMChain

from hybrid_agi.agents.trainers.prompt import (
    TRAINER_PROMPT,
    TRAINING_SUMMARIZER_PROMPT
)

from hybrid_agi.prompt import (
    HYBRID_AGI_SELF_DESCRIPTION,
    HYBRID_AGI_CORE_VALUES
)

TRAINING_LEVELS = [
    "1st year University Student",
    "2nd year University Student",
    "License Student",
    "Master Student",
    "PhD Student",
]

class CurriculumTrainer():
    """Curriculum trainer for the HybridAGI"""
    def __init__(
        self,
        llm:BaseLanguageModel,
        verbose:bool = True,
        nb_tasks = 25,
        ):
        self.llm = llm
        self.verbose = verbose
        self.nb_tasks = nb_tasks
        self.dataset = []

    def run(self, expertise:str):
        summary = ""
        for level in TRAINING_LEVELS:
            if summary != "":
                chain = LLMChain(llm=self.llm, prompt=TRAINING_SUMMARIZER_PROMPT, verbose=self.verbose)
                summary = chain.predict(tasks=summary)
                summary_tasks = summary
            else:
                summary_tasks = "Nothing learned yet." 
            chain = LLMChain(llm=self.llm, prompt=TRAINER_PROMPT, verbose=self.verbose)
            result = chain.predict(
                self_description=HYBRID_AGI_SELF_DESCRIPTION,
                core_values=HYBRID_AGI_CORE_VALUES,
                n = self.nb_tasks,
                expertise = expertise,
                level = level,
                tasks = summary_tasks,
            )
            result = result.lstrip()
            if summary == "":
                summary = result
            else:
                summary += result
            if self.verbose:
                print(f"{Fore.YELLOW}"+result+f"{Style.RESET_ALL}")
            self.dataset.extend((result.replace("\n- ", "- ")).split("- "))

    def save(self, filepath:str):
        f = open(filepath, "w")
        for data in self.dataset:
            if data:
                f.write(data+"\n")

