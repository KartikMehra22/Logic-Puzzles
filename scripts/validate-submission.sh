#!/usr/bin/env bash
#
# validate-submission.sh — Round 1 Submission Validator
#
# Checks that Docker builds, openenv validates, and baseline runs
#
# Prerequisites:
#   - Docker: https://docs.docker.com/get-docker/
#   - pip install openenv-core
#   - .env file with HF_TOKEN, API_BASE_URL, MODEL_NAME
#
# Run:
#   chmod +x scripts/validate-submission.sh
#   ./scripts/validate-submission.sh
#

set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0

log()  { printf "[%s] %b\n" "$(date -u +%H:%M:%S)" "$*"; }
pass() { log "${GREEN}✓${NC} $1"; PASS=$((PASS + 1)); }
fail() { log "${RED}✗${NC} $1"; FAIL=$((FAIL + 1)); }
hint() { printf "  ${YELLOW}→${NC} %b\n" "$1"; }

printf "\n%b%bOpenEnv Round 1 Submission Validator%b\n" "$BOLD" "$GREEN" "$NC"
printf "%b========================================%b\n\n" "$BOLD" "$NC"

# Check 1: .env exists
log "${BOLD}Check 1: Environment file${NC}"
if [ -f "$REPO_DIR/.env" ]; then
  pass ".env file found"
  if grep -q "HF_TOKEN=" "$REPO_DIR/.env"; then
    pass "HF_TOKEN defined"
  else
    fail "HF_TOKEN not in .env"
    hint "Add: HF_TOKEN=hf_xxxxx"
  fi
else
  fail ".env file missing"
  hint "cp .env.example .env && nano .env"
  exit 1
fi

# Check 2: openenv.yaml exists
log "${BOLD}Check 2: OpenEnv spec${NC}"
if [ -f "$REPO_DIR/openenv.yaml" ]; then
  pass "openenv.yaml found"
else
  fail "openenv.yaml missing"
  hint "Create openenv.yaml with environment spec"
  exit 1
fi

# Check 3: Dockerfile builds
log "${BOLD}Check 3: Docker build${NC}"
if ! command -v docker &>/dev/null; then
  fail "Docker not installed"
  hint "Install: https://docs.docker.com/get-docker/"
  exit 1
fi

if docker build -t pattern-puzzle-env:test -f "$REPO_DIR/server/Dockerfile" "$REPO_DIR" > /dev/null 2>&1; then
  pass "Docker build succeeded"
else
  fail "Docker build failed"
  hint "Run: docker build -f server/Dockerfile . to see errors"
  exit 1
fi

# Check 4: openenv validate
log "${BOLD}Check 4: OpenEnv validation${NC}"
if ! command -v openenv &>/dev/null; then
  fail "openenv CLI not found"
  hint "Install: pip install openenv-core"
  exit 1
fi

if cd "$REPO_DIR" && openenv validate > /dev/null 2>&1; then
  pass "openenv validate passed"
else
  fail "openenv validate failed"
  hint "Run: openenv validate (in repo root) to see errors"
  exit 1
fi

# Check 5: inference.py exists
log "${BOLD}Check 5: Baseline script${NC}"
if [ -f "$REPO_DIR/inference.py" ]; then
  pass "inference.py found"
else
  fail "inference.py not in root"
  hint "Baseline script must be in project root"
  exit 1
fi

# Check 6: validate.py exists
log "${BOLD}Check 6: Validation suite${NC}"
if [ -f "$REPO_DIR/validate.py" ]; then
  pass "validate.py found"
else
  fail "validate.py not in root"
  hint "Quick validation script recommended"
  exit 1
fi

# Check 7: requirements.txt exists
log "${BOLD}Check 7: Dependencies${NC}"
if [ -f "$REPO_DIR/requirements.txt" ]; then
  pass "requirements.txt found"
else
  fail "requirements.txt missing"
  hint "Create requirements.txt with all dependencies"
  exit 1
fi

# Check 8: README complete
log "${BOLD}Check 8: Documentation${NC}"
if [ -f "$REPO_DIR/README.md" ]; then
  if grep -q "## Installation" "$REPO_DIR/README.md" && grep -q "## Project Structure" "$REPO_DIR/README.md"; then
    pass "README has required sections"
  else
    fail "README missing required sections"
    hint "Add: Installation, Project Structure, API Endpoints"
  fi
else
  fail "README.md not found"
  exit 1
fi

# Summary
printf "\n%b========================================%b\n" "$BOLD" "$NC"
printf "%b✓ Passed  %b %d checks\n" "$GREEN" "$NC" "$PASS"
if [ "$FAIL" -gt 0 ]; then
  printf "%b✗ Failed  %b %d checks\n" "$RED" "$NC" "$FAIL"
  printf "\n%bFix the above issues before submitting.%b\n\n" "$RED" "$NC"
  exit 1
else
  printf "%b✅ All checks passed! Ready for Round 1.%b\n\n" "$GREEN" "$NC"
  exit 0
fi
