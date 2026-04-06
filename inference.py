import asyncio
import os
import textwrap
from typing import List, Optional
from openai import OpenAI

API_KEY       = os.getenv("HF_TOKEN")
API_BASE_URL  = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME    = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
IMAGE_NAME    = os.getenv("IMAGE_NAME")   # Docker image used to start the environment

TASK_NAME     = os.getenv("PATTERN_TASK",      "sequence_guess")
BENCHMARK     = os.getenv("PATTERN_BENCHMARK", "my_pattern_env")
MAX_STEPS     = int(float(os.getenv("MAX_STEPS",   "3")))
TEMPERATURE   = float(os.getenv("TEMPERATURE",     "0.3"))
MAX_TOKENS    = int(float(os.getenv("MAX_TOKENS",  "50")))


# -----------------------------------------------
# Scoring settings
# -----------------------------------------------
# Best possible episode score:
# hard task reward (3.0) + first-try bonus (0.5) = 3.5
MAX_TOTAL_REWARD        = float(os.getenv("MAX_TOTAL_REWARD",        "3.5"))
SUCCESS_SCORE_THRESHOLD = float(os.getenv("SUCCESS_SCORE_THRESHOLD", "0.1"))


# -----------------------------------------------
# Logging helpers
# -----------------------------------------------
def log_start(task: str, env: str, model: str) -> None:
    # Keep this line format stable for log parsers.
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float,
             done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val  = str(done).lower()          # Use lowercase true/false for consistency.
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

def build_user_prompt(
    sequence: str,
    feedback: str,
    attempts_left: int,
    difficulty: str,
    history: List[str]
) -> str:
    history_block = "\n".join(history[-3:]) if history else "None"
    return textwrap.dedent(f"""
        Sequence: {sequence}
        Difficulty: {difficulty}
        Attempts left: {attempts_left}
        Last feedback: {feedback}

        Your previous guesses this episode:
        {history_block}

        What is the next value? Reply with the value only.
    """).strip()

def get_model_guess(
    client: OpenAI,
    sequence: str,
    feedback: str,
    attempts_left: int,
    difficulty: str,
    history: List[str]
) -> str:
    user_prompt = build_user_prompt(
        sequence, feedback, attempts_left, difficulty, history
    )
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else "0"   # Fallback if the model returns an empty response.
    except Exception as exc:
        # Send debug errors to stderr so stdout stays clean for structured logs.
        print(f"[DEBUG] LLM call failed: {exc}", flush=True, file=__import__('sys').stderr)
        return "0"
    
async def main() -> None:
    # Initialize API client.
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    # Start the environment client from the Docker image.
    from my_pattern_env import PatternEnvClient
    env = await PatternEnvClient.from_docker_image(IMAGE_NAME)

    # Episode tracking.
    history : List[str]  = []
    rewards : List[float] = []
    steps_taken           = 0
    score                 = 0.0
    success               = False

    # Emit start log once per run.
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        # Reset and read the first observation.
        result      = await env.reset()
        obs         = result.observation
        sequence    = obs.sequence
        feedback    = obs.feedback
        attempts_left = obs.attempts_left
        difficulty  = obs.task_difficulty

        # Keep stepping until done or step limit is reached.
        for step in range(1, MAX_STEPS + 1):

            if result.done:
                break

            # Ask the model for the next guess.
            guess = get_model_guess(
                client, sequence, feedback,
                attempts_left, difficulty, history
            )

            # Submit the guess to the environment.
            result = await env.step({"guess": guess})
            obs    = result.observation

            reward = result.reward or 0.0
            done   = result.done
            error  = None   # Wrong guesses are normal, not runtime errors.

            # Update episode trackers.
            rewards.append(reward)
            steps_taken   = step
            feedback      = obs.feedback
            attempts_left = obs.attempts_left

            # Emit step log right after the environment responds.
            log_step(step=step, action=guess,
                     reward=reward, done=done, error=error)

            # Keep short history to avoid repeating bad guesses.
            history.append(f"Step {step}: guessed '{guess}' → {feedback}")

            if done:
                break

        # Compute normalized score in [0.0, 1.0].
        score   = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score   = min(max(score, 0.0), 1.0)        # Clamp to valid range.
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        # Always close the environment, even on failure.
        try:
            await env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error: {e}",
                  flush=True, file=__import__('sys').stderr)

        # Emit final summary log no matter how the run ended.
        log_end(success=success, steps=steps_taken,
                score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())