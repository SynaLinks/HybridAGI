import subprocess
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CmdExecRequest(BaseModel):
    cmd: str

@app.post("/cmdexec")
async def command_execution(request: CmdExecRequest):
    sp = subprocess.Popen(request.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    output_bytes = sp.stdout.read() + sp.stderr.read()
    output_str = str(output_bytes, "utf-8")
    return output_str