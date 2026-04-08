from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

# local import so the server can find the environment module
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from server.environment import PatternEnvironment
from models import PatternAction, PatternObservation, PatternState

# one app, one shared environment
app = FastAPI(title="Pattern Sequence Environment", version="1.0.0")
env = PatternEnvironment()   # one game instance shared across requests


# request payloads
class ResetRequest(BaseModel):
    difficulty: Optional[str] = None   # "easy", "medium", "hard", or None = random

class StepRequest(BaseModel):
    guess: str                         # the AI's answer


@app.get("/")
def root():
    return {
        "status": "running",
        "name": "pattern-puzzle-env",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/metadata")
def metadata():
    return {
        "name": "pattern-puzzle-env",
        "description": "Pattern sequence puzzle game where AI agents solve mathematical and alphabetical sequences.",
    }


@app.get("/schema")
def schema():
    return {
        "action": PatternAction.model_json_schema(),
        "observation": PatternObservation.model_json_schema(),
        "state": PatternState.model_json_schema(),
    }


@app.post("/mcp")
async def mcp(request: Request):
    payload = await request.json()
    return {
        "jsonrpc": "2.0",
        "id": payload.get("id") if isinstance(payload, dict) else None,
        "result": {"status": "ok"},
    }


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
    return {"status": "healthy"}


def main(host: str = "0.0.0.0", port: int = 7860) -> None:
    uvicorn.run(app, host=host, port=port)


# local run
if __name__ == "__main__":
    main()
    