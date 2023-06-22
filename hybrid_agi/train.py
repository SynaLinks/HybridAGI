"""The script to generate training datasets. Copyright (C) 2023 SynaLinks. License: GPLv3"""

import os
import argparse
from colorama import Fore
from colorama import Style
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.llm import LLMChain

from langchain.embeddings import OpenAIEmbeddings
from hybrid_agi.config import Config

from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

from hybrid_agi.agents.trainers.curriculum_trainer import CurriculumTrainer

from hybrid_agi.prompt import (
    HYBRID_AGI_SELF_DESCRIPTION,
    HYBRID_AGI_CORE_VALUES
)

BANNER =\
"""
o  o o   o o--o  o--o  o-O-o o-o         O   o-o  o-O-o 
|  |  \ /  |   | |   |   |   |  \       / \ o       |   
O--O   O   O--o  O-Oo    |   |   O     o---o|  -o   |   
|  |   |   |   | |  \    |   |  /      |   |o   |   |   
o  o   o   o--o  o   o o-O-o o-o       o   o o-o  o-O-o
    Unleash the Power of Combined Vector and Graph Databases
"""

def main():
    print(f"{Fore.YELLOW}{BANNER}{Style.RESET_ALL}")
    parser = argparse.ArgumentParser(
                    prog='HybridAGI Trainer',
                    description='The AI used to create a dataset of tasks for the Hybrid AGI',
                    epilog='See https://github.com/SynaLinks/HybridAGI for more information.')

    args = parser.parse_args()

    cfg = Config()
    embedding = OpenAIEmbeddings()

    if cfg.private_mode is True:
        llm = ChatOpenAI(temperature=cfg.temperature, model_name=cfg.fast_llm_model, openai_api_base=cfg.openai_base_path)
    else:
        llm = ChatOpenAI(temperature=cfg.temperature, model_name=cfg.fast_llm_model)
    
    trainer = CurriculumTrainer(
        llm,
        verbose=cfg.debug_mode
    )
    template = """
    You are Hybrid AGI. Present yourself and ask in {language} about the domain they want you to become expert.
    Output:"""
    prompt = PromptTemplate(
        input_variables=["language"],
        template = template
    )
    message = LLMChain(llm=llm, prompt=prompt).predict(
        language=cfg.user_language
    )
    print(f"{Fore.YELLOW}[*] "+message+f"{Style.RESET_ALL}")
    expertise_domain = input(f"{Fore.YELLOW}> {Style.RESET_ALL}")
    trainer.run(expertise_domain)
    filename = expertise_domain.lower().replace(" ", "_")
    output_path = os.path.join(cfg.downloads_directory, filename)+".txt"
    print(f"{Fore.YELLOW}[*] Saved into: {output_path} {Style.RESET_ALL}")
    trainer.save(output_path)
