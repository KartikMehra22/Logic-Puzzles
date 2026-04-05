from pydantic import BaseModel
from typing import Optional, List

# agent's output — just the guess, keeping it minimal on purpose
class PatternAction(BaseModel):
    guess: str                  # raw string, could be "10", "I", whatever the pattern resolves to

# everything the agent sees after each step
class PatternObservation(BaseModel):
    sequence: str               # the actual pattern string, example: "2, 4, 6, 8, ?"
    feedback: str               # simple pass/fail message back to the agent
    attempts_left: int          # countdown — agent needs this to know when to stop retrying
    task_difficulty: str        # drives how we sample tasks; easy/medium/hard buckets

# server-side only — agent never touches this directly
class PatternState(BaseModel):
    correct_answer: str         # ground truth, compared against PatternAction.guess
    task_id: int                # tracks which task we're on across episodes
    solved: bool = False        # flipped to True on first correct guess
    total_attempts: int = 0     # useful for logging and reward shaping later
