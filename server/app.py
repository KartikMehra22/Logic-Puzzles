from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

# local import so the server can find the environment module
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from server.environment import PatternEnvironment

# one app, one shared environment
app = FastAPI(title="Pattern Sequence Environment")
env = PatternEnvironment()   # one game instance shared across requests


# request payloads
class ResetRequest(BaseModel):
    difficulty: Optional[str] = None   # "easy", "medium", "hard", or None = random

class StepRequest(BaseModel):
    guess: str                         # the AI's answer


# reset the game
@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    try:
        obs = env.reset(difficulty=req.difficulty)
        return JSONResponse(content={"observation": obs, "done": False})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# process one guess
@app.post("/step")
def step(req: StepRequest):
    try:
        result = env.step(action={"guess": req.guess})
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# debug state
@app.get("/state")
def state():
    try:
        return JSONResponse(content=env.state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# simple health check
@app.get("/health")
def health():
    return {"status": "ok"}


# local run
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=True)
    