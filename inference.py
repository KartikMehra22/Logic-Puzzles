import asyncio
import os
import textwrap
from typing import List, Optional
from openai import OpenAI

API_KEY       = os.getenv("HF_TOKEN")
API_BASE_URL  = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME    = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
IMAGE_NAME    = os.getenv("IMAGE_NAME")   # Docker image to run for the env

TASK_NAME     = os.getenv("PATTERN_TASK",      "sequence_guess")
BENCHMARK     = os.getenv("PATTERN_BENCHMARK", "my_pattern_env")
MAX_STEPS     = int(float(os.getenv("MAX_STEPS",   "3")))
TEMPERATURE   = float(os.getenv("TEMPERATURE",     "0.3"))
MAX_TOKENS    = int(float(os.getenv("MAX_TOKENS",  "50")))


# -----------------------------------------------
# Scoring config
# -----------------------------------------------
# Max score in one episode:
# hard task reward (3.0) + first-try bonus (0.5) = 3.5
MAX_TOTAL_REWARD        = float(os.getenv("MAX_TOTAL_REWARD",        "3.5"))
SUCCESS_SCORE_THRESHOLD = float(os.getenv("SUCCESS_SCORE_THRESHOLD", "0.1"))


# -----------------------------------------------
# Logging helpers (stdout goes through these only)
# -----------------------------------------------
def log_start(task: str, env: str, model: str) -> None:
    # Keep format stable so logs are easy to parse.
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float,
             done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val  = str(done).lower()          # Match JSON-style true/false.
    print(
        f"[STEP] step={step} action={action} "
        f"reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int,
            score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.3f} rewards={rewards_str}",
        flush=True,
    )

SYSTEM_PROMPT = textwrap.dedent("""
    You are an expert at solving number and letter pattern sequences.

    Rules:
    - You will be shown an incomplete sequence ending with ?
    - Reply with ONLY the next value — no explanation, no punctuation
    - Examples:
        Sequence: 2, 4, 6, 8, ?    → Reply: 10
        Sequence: A, C, E, G, ?    → Reply: I
        Sequence: 3, 9, 27, 81, ?  → Reply: 243

    One word or number only. Nothing else.
""").strip()