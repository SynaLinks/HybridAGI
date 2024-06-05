"""The python code interpreter. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""
# modified from OpenCodeInterpreter to extract plots as base64 image
# Copyright 2024 OpenCodeInterpreter

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from jupyter_client import KernelManager
import threading
import re
import os
import sys
from typing import Optional, Tuple, List
import PIL
from PIL import Image
import base64
import io

prj_root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(prj_root_path)

TOOLS_CODE = """
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os,sys
import re
from datetime import datetime
from sympy import symbols, Eq, solve
import torch
import requests
from bs4 import BeautifulSoup
import json
import math
import yfinance
import time
import io
import base64
"""

write_denial_function = 'lambda *args, **kwargs: (_ for _ in ()).throw(PermissionError("Writing to disk operation is not permitted due to safety reasons. Please do not try again!"))'
read_denial_function = 'lambda *args, **kwargs: (_ for _ in ()).throw(PermissionError("Reading from disk operation is not permitted due to safety reasons. Please do not try again!"))'
class_denial = """Class Denial:
    def __getattr__(self, name):
        def method(*args, **kwargs):
            return "Using this class is not permitted due to safety reasons. Please do not try again!"
        return method
"""

show_plot = """def show(*args, **kwargs) -> None:
    import io
    import base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    encoded_img = base64.b64encode(buffer.read())
    print(f"<image>{encoded_img.decode('utf8')}</image>")"""

GUARD_CODE = f"""
{show_plot}

import matplotlib.pyplot as plt

plt.show = show

import os

os.kill = {write_denial_function}
os.system = {write_denial_function}
os.putenv = {write_denial_function}
os.remove = {write_denial_function}
os.removedirs = {write_denial_function}
os.rmdir = {write_denial_function}
os.fchdir = {write_denial_function}
os.setuid = {write_denial_function}
os.fork = {write_denial_function}
os.forkpty = {write_denial_function}
os.killpg = {write_denial_function}
os.rename = {write_denial_function}
os.renames = {write_denial_function}
os.truncate = {write_denial_function}
os.replace = {write_denial_function}
os.unlink = {write_denial_function}
os.fchmod = {write_denial_function}
os.fchown = {write_denial_function}
os.chmod = {write_denial_function}
os.chown = {write_denial_function}
os.chroot = {write_denial_function}
os.fchdir = {write_denial_function}
os.lchflags = {write_denial_function}
os.lchmod = {write_denial_function}
os.lchown = {write_denial_function}
os.getcwd = {write_denial_function}
os.chdir = {write_denial_function}
os.popen = {write_denial_function}

import shutil

shutil.rmtree = {write_denial_function}
shutil.move = {write_denial_function}
shutil.chown = {write_denial_function}

import subprocess

subprocess.Popen = {write_denial_function}  # type: ignore

import sys

sys.modules["ipdb"] = {write_denial_function}
sys.modules["joblib"] = {write_denial_function}
sys.modules["resource"] = {write_denial_function}
sys.modules["tkinter"] = {write_denial_function}
"""

class JupyterNotebook():
    def __init__(self):
        self.km = KernelManager()
        self.km.start_kernel()
        self.kc = self.km.client()
        # This throw Exception during subprocesses termination 'function' object has no attribute 'PROCFS_PATH'
        # I need to find a way to properly protect the filesystem
        _,_ = self.add_and_run(TOOLS_CODE)
        _,_ = self.add_and_run(GUARD_CODE)

    def clean_output(self, outputs: List[str]):
        outputs_only_str = list()
        for i in outputs:
            if type(i) == dict:
                if "text/plain" in list(i.keys()):
                    outputs_only_str.append(i["text/plain"])
            elif type(i) == str:
                outputs_only_str.append(i)
            elif type(i) == list:
                error_msg = "\n".join(i)
                error_msg = re.sub(r"\x1b\[.*?m", "", error_msg)
                outputs_only_str.append(error_msg)

        return "\n".join(outputs_only_str).strip()

    def add_and_run(self, code_string: str):
        # This inner function will be executed in a separate thread
        def run_code_in_thread():
            nonlocal outputs, error_flag

            # Execute the code and get the execution count
            msg_id = self.kc.execute(code_string)

            while True:
                try:
                    msg = self.kc.get_iopub_msg(timeout=20)

                    msg_type = msg["header"]["msg_type"]
                    content = msg["content"]

                    if msg_type == "execute_result":
                        outputs.append(content["data"])
                    elif msg_type == "stream":
                        outputs.append(content["text"])
                    elif msg_type == "error":
                        error_flag = True
                        outputs.append(content["traceback"])

                    # If the execution state of the kernel is idle, it means the cell finished executing
                    if msg_type == "status" and content["execution_state"] == "idle":
                        break
                except:
                    break

        outputs = []
        error_flag = False

        # Start the thread to run the code
        thread = threading.Thread(target=run_code_in_thread)
        thread.start()

        # Wait for 20 seconds for the thread to finish
        thread.join(timeout=20)

        # If the thread is still alive after 20 seconds, it's a timeout
        if thread.is_alive():
            outputs = ["Execution timed out."]
            error_flag = True
        return self.clean_output(outputs), error_flag

    def close(self):
        """Shutdown the kernel."""
        self.km.shutdown_kernel()
    
    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        new_copy = type(self)()
        memo[id(self)] = new_copy
        return new_copy   

class CodeInterpreterUtility:

    def __init__(
            self,
            nb : Optional[JupyterNotebook] = None,
        ):
        if nb is None:
            self.nb = JupyterNotebook()
        else:
            self.nb = nb

    def extract_code_blocks(self, prompt: str) -> Tuple[bool, str]:
        pattern = re.escape("```python") + r"(.*?)" + re.escape("```")
        matches = re.findall(pattern, prompt, re.DOTALL)

        if matches:
            # Return the last matched code block
            return True, matches[-1].strip()
        else:
            return False, ""

    def clean_code_output(self, output: str) -> str:
        if self.MAX_CODE_OUTPUT_LENGTH < len(output):
            return (
                output[: self.MAX_CODE_OUTPUT_LENGTH // 5]
                + "\n...(truncated due to length)...\n"
                + output[-self.MAX_CODE_OUTPUT_LENGTH // 5 :]
            )
        return output

    def execute_code_and_return_output(self, code_str: str) -> Tuple[str, str]:
        outputs, error = self.nb.add_and_run(code_str)
        return outputs, error

    def extract_plots(self, output: str) -> List[Image.Image]:
        plots = []
        pattern = r"<image>(.*?)</image>"
        matches = re.findall(pattern, output, re.DOTALL)
        for m in matches:
            output = output.replace("<image>"+m+"</image>", "")
            msg = base64.b64decode(m)
            buffer = io.BytesIO(msg)
            img = Image.open(buffer)
            plots.append(img)
        return output, plots

    def add_and_run(self, code: str) -> Tuple[str, List[Image.Image], bool]:
        plots = []
        output, error = self.execute_code_and_return_output(code)
        if not error:
            output, plots = self.extract_plots(output)
        return output, plots, error
        
    def reset(self):
        self.nb.close()
        self.nb = JupyterNotebook()