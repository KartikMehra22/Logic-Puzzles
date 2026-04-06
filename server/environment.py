import random
from typing import List, Dict, Any
from openenv.core import Environment  # base class from OpenEnv

TASKS: List[Dict[str, Any]] = [
    # easy tier — single-step arithmetic, agent should nail these fast
    {
        "id": 0,
        "difficulty": "easy",
        "sequence": "2, 4, 6, 8, ?",
        "answer": "10",
        "rule": "Add 2 each time",
        "max_attempts": 3,
    },
    {
        "id": 1,
        "difficulty": "easy",
        "sequence": "5, 10, 15, 20, ?",
        "answer": "25",
        "rule": "Add 5 each time",
        "max_attempts": 3,
    },
    {
        "id": 2,
        "difficulty": "easy",
        "sequence": "1, 1, 2, 3, 5, ?",
        "answer": "8",
        "rule": "Fibonacci sequence",
        "max_attempts": 3,
    },
    {
        "id": 9,
        "difficulty": "easy",
        "sequence": "10, 20, 30, 40, ?",
        "answer": "50",
        "rule": "Add 10 each time",
        "max_attempts": 3,
    },
    {
        "id": 10,
        "difficulty": "easy",
        "sequence": "7, 14, 21, 28, ?",
        "answer": "35",
        "rule": "Add 7 each time",
        "max_attempts": 3,
    },
    {
        "id": 11,
        "difficulty": "easy",
        "sequence": "9, 8, 7, 6, ?",
        "answer": "5",
        "rule": "Subtract 1 each time",
        "max_attempts": 3,
    },
    {
        "id": 12,
        "difficulty": "easy",
        "sequence": "3, 6, 9, 12, ?",
        "answer": "15",
        "rule": "Add 3 each time",
        "max_attempts": 3,
    },
    {
        "id": 13,
        "difficulty": "easy",
        "sequence": "2, 5, 8, 11, ?",
        "answer": "14",
        "rule": "Add 3 each time",
        "max_attempts": 3,
    },

    # medium tier — introduces non-linear rules, alternating patterns, alpha sequences
    {
        "id": 3,
        "difficulty": "medium",
        "sequence": "3, 9, 27, 81, ?",
        "answer": "243",
        "rule": "Multiply by 3 each time",
        "max_attempts": 3,
    },
    {
        "id": 4,
        "difficulty": "medium",
        "sequence": "A, C, E, G, ?",
        "answer": "I",
        "rule": "Skip one letter",
        "max_attempts": 3,
    },
    {
        "id": 5,
        "difficulty": "medium",
        "sequence": "100, 50, 25, 12.5, ?",
        "answer": "6.25",
        "rule": "Divide by 2",
        "max_attempts": 3,
    },
    {
        "id": 14,
        "difficulty": "medium",
        "sequence": "4, 16, 64, 256, ?",
        "answer": "1024",
        "rule": "Multiply by 4",
        "max_attempts": 3,
    },
    {
        "id": 15,
        "difficulty": "medium",
        "sequence": "2, 6, 7, 21, 22, ?",
        "answer": "66",
        "rule": "Alternate: ×3, +1",
        "max_attempts": 3,
    },
    {
        "id": 16,
        "difficulty": "medium",
        "sequence": "B, E, H, K, ?",
        "answer": "N",
        "rule": "Skip two letters",
        "max_attempts": 3,
    },
    {
        "id": 17,
        "difficulty": "medium",
        "sequence": "81, 27, 9, 3, ?",
        "answer": "1",
        "rule": "Divide by 3",
        "max_attempts": 3,
    },
    {
        "id": 18,
        "difficulty": "medium",
        "sequence": "1, 4, 3, 8, 5, ?",
        "answer": "12",
        "rule": "Alternating pattern",
        "max_attempts": 3,
    },

    # hard tier — factorials, primes, look-and-say; needs actual reasoning, not just delta guessing
    {
        "id": 6,
        "difficulty": "hard",
        "sequence": "1, 4, 9, 16, 25, ?",
        "answer": "36",
        "rule": "Squares",
        "max_attempts": 2,
    },
    {
        "id": 7,
        "difficulty": "hard",
        "sequence": "2, 3, 5, 7, 11, ?",
        "answer": "13",
        "rule": "Prime numbers",
        "max_attempts": 2,
    },
    {
        "id": 8,
        "difficulty": "hard",
        "sequence": "1, 2, 6, 24, 120, ?",
        "answer": "720",
        "rule": "Factorials",
        "max_attempts": 2,
    },
    {
        "id": 19,
        "difficulty": "hard",
        "sequence": "2, 6, 12, 20, 30, ?",
        "answer": "42",
        "rule": "n(n+1)",
        "max_attempts": 2,
    },
    {
        "id": 20,
        "difficulty": "hard",
        "sequence": "1, 3, 6, 10, 15, ?",
        "answer": "21",
        "rule": "Triangular numbers",
        "max_attempts": 2,
    },
    {
        "id": 21,
        "difficulty": "hard",
        "sequence": "3, 6, 18, 72, 360, ?",
        "answer": "2160",
        "rule": "Multiply by increasing numbers",
        "max_attempts": 2,
    },
    {
        "id": 22,
        "difficulty": "hard",
        "sequence": "1, 11, 21, 1211, 111221, ?",
        "answer": "312211",
        "rule": "Look-and-say sequence",
        "max_attempts": 2,
    },
    {
        "id": 23,
        "difficulty": "hard",
        "sequence": "0, 1, 1, 2, 4, 7, ?",
        "answer": "13",
        "rule": "Sum of previous three",
        "max_attempts": 2,
    },
]


def grade_answer(guess: str, correct_answer: str) -> bool:
    """
    Normalize both sides before comparing — agents tend to add trailing spaces
    or return '6.250' instead of '6.25', so we handle that gracefully.
    String match runs first, numeric fallback only if that fails.
    """
    guess = guess.strip().lower()
    correct = correct_answer.strip().lower()

    # covers most cases — letters, words, clean integers
    if guess == correct:
        return True

    # float comparison catches things like '6.25' vs '6.250' or '10' vs '10.0'
    try:
        return float(guess) == float(correct)
    except ValueError:
        pass

    return False


# base reward per tier — scale this up later if we want harder tasks to feel more impactful
DIFFICULTY_BASE_REWARD = {
    "easy":   1.0,
    "medium": 2.0,
    "hard":   3.0,
}

def calculate_reward(
    correct: bool,
    difficulty: str,
    attempts_used: int,
    max_attempts: int
) -> float:
    """
    Wrong guess always returns 0 — no partial credit, keeps the signal clean.
    For correct guesses, reward = base + efficiency bonus.

    Efficiency is how many attempts were still left before this guess landed.
    First-try solve on a 3-attempt task gives full 1.0 bonus;
    second-try solve on a 3-attempt task gives 0.5 bonus;
    last-attempt solve gives 0 — agent burned through all its chances.
    """
    if not correct:
        return 0.0

    base = DIFFICULTY_BASE_REWARD.get(difficulty, 1.0)

    # remaining attempts BEFORE this guess counts — not after
    attempts_remaining = max_attempts - attempts_used
    efficiency = attempts_remaining / max_attempts

    return round(base + efficiency, 2)


class PatternEnvironment(Environment):

    def __init__(self):
        # episode state — none of this leaks to the agent
        self._task = None           # whichever task got sampled this episode
        self._attempts_used = 0     # increments on every step call
        self._solved = False        # flipped only on a correct guess
        self._done = False          # signals the runner to stop stepping
        self._reward_history = []   # handy for post-episode analysis

    def reset(self, difficulty: str = None) -> dict:
        # if a difficulty is passed, restrict the pool — useful for curriculum training
        pool = TASKS
        if difficulty in ("easy", "medium", "hard"):
            pool = [t for t in TASKS if t["difficulty"] == difficulty]

        self._task = random.choice(pool)
        self._attempts_used = 0
        self._solved = False
        self._done = False
        self._reward_history = []

        # first obs has no feedback yet, agent just sees the sequence cold
        return {
            "sequence": self._task["sequence"],
            "feedback": "Game started! What comes next?",
            "attempts_left": self._task["max_attempts"],
            "task_difficulty": self._task["difficulty"],
        }

    def step(self, action: dict) -> dict:
        guess = action.get("guess", "").strip()

        self._attempts_used += 1
        attempts_left = self._task["max_attempts"] - self._attempts_used

        correct = grade_answer(guess, self._task["answer"])

        reward = calculate_reward(
            correct=correct,
            difficulty=self._task["difficulty"],
            attempts_used=self._attempts_used,
            max_attempts=self._task["max_attempts"],
        )
        self._reward_history.append(reward)

        # three terminal cases: solved, ran out of attempts, or still going
        if correct:
            self._solved = True
            self._done = True
            feedback = f"Correct! '{guess}' is right. Rule: {self._task['rule']}"
        elif attempts_left == 0:
            self._done = True
            feedback = (
                f"Out of attempts! The answer was '{self._task['answer']}'. "
                f"Rule: {self._task['rule']}"
            )
        else:
            feedback = f"Wrong! '{guess}' is not right. {attempts_left} attempt(s) left."

        return {
            "observation": {
                "sequence": self._task["sequence"],
                "feedback": feedback,
                "attempts_left": attempts_left,
                "task_difficulty": self._task["difficulty"],
            },
            "reward": reward,
            "done": self._done,
        }

    @property
    def state(self) -> dict:
        # server-side only — expose this for logging/debugging, never pass it to the agent
        return {
            "correct_answer": self._task["answer"] if self._task else None,
            "task_id": self._task["id"] if self._task else None,
            "difficulty": self._task["difficulty"] if self._task else None,
            "solved": self._solved,
            "attempts_used": self._attempts_used,
            "reward_history": self._reward_history,
        }
