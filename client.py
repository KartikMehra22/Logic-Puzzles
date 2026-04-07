import httpx
from dataclasses import dataclass
from typing import Optional

# These match the JSON shape returned by the server.
@dataclass
class PatternObservation:
    sequence:        str
    feedback:        str
    attempts_left:   int
    task_difficulty: str

@dataclass
class StepResult:
    observation: PatternObservation
    reward:      float
    done:        bool

# Main client used by inference.py.
class PatternEnvClient:

    def __init__(self, base_url: str):
        # Keep URLs consistent (no trailing slash headaches).
        self.base_url = base_url.rstrip("/")
        self._client  = None     # Created lazily in _connect().

    # Start the env container locally and return a connected client.
    @classmethod
    async def from_docker_image(cls, image_name: str) -> "PatternEnvClient":
        import subprocess, time

        # Run the container in detached mode on port 7860.
        subprocess.Popen([
            "docker", "run", "--rm", "-d",
            "-p", "7860:7860",
            "--name", "pattern-env",
            image_name
        ])

        # Give the API a second to come up before connecting.
        time.sleep(3)

        instance = cls(base_url="http://localhost:7860")
        await instance._connect()
        return instance

    # Connect to an already-running server.
    @classmethod
    async def from_url(cls, base_url: str) -> "PatternEnvClient":
        instance = cls(base_url=base_url)
        await instance._connect()
        return instance

    async def _connect(self):
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0    # Don't hang forever on slow responses.
        )

    # Start a new puzzle episode.
    async def reset(self, difficulty: Optional[str] = None) -> StepResult:
        body = {}
        if difficulty:
            body["difficulty"] = difficulty

        response = await self._client.post("/reset", json=body)
        response.raise_for_status()    # Bubble up API errors immediately.
        data = response.json()

        obs = PatternObservation(
            sequence        = data["observation"]["sequence"],
            feedback        = data["observation"]["feedback"],
            attempts_left   = data["observation"]["attempts_left"],
            task_difficulty = data["observation"]["task_difficulty"],
        )
        return StepResult(observation=obs, reward=0.0, done=False)

    # Send one guess and get the updated state.
    async def step(self, action: dict) -> StepResult:
        response = await self._client.post("/step", json=action)
        response.raise_for_status()
        data = response.json()

        obs = PatternObservation(
            sequence        = data["observation"]["sequence"],
            feedback        = data["observation"]["feedback"],
            attempts_left   = data["observation"]["attempts_left"],
            task_difficulty = data["observation"]["task_difficulty"],
        )
        return StepResult(
            observation = obs,
            reward      = data.get("reward", 0.0),
            done        = data.get("done", False),
        )

    # Clean up HTTP client and local container.
    async def close(self):
        if self._client:
            await self._client.aclose()

        # Try to stop the container quietly (fine if it's already gone).
        import subprocess
        subprocess.run(
            ["docker", "stop", "pattern-env"],
            capture_output=True    # Noisy output here is not useful.
        )
