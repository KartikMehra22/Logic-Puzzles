# Installation

## 1. Clone the repository

```bash
git clone https://github.com/MAYANKSHARMA01010/Logic-Puzzles.git
cd Logic-Puzzles
```

## 2. Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Create the env file

```bash
cp .env.example .env
nano .env
```

Add your Hugging Face token and API values.

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Validate the setup

```bash
python validate.py
```