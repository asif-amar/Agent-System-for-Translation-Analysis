#!/bin/bash

################################################################################
# Translation Quality Analysis Experiment Runner
#
# This script sets up the environment and runs translation experiments.
# It can work with or without an API key:
#   - With API key: Uses Anthropic API
#   - Without API key: Uses Claude Code (manual translation by Claude)
#
# Usage:
#   ./run_experiment.sh [sanity|same|different|all]
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}================================================================================${NC}"
echo -e "${BLUE}        Translation Quality Analysis - Experiment Runner${NC}"
echo -e "${BLUE}================================================================================${NC}"
echo ""

################################################################################
# Step 1: Create .env from example if it doesn't exist
################################################################################

echo -e "${YELLOW}[Step 1/5] Checking environment configuration...${NC}"

if [ ! -f ".env" ]; then
    if [ -f "example.env" ]; then
        echo -e "${GREEN}✓${NC} Creating .env from example.env..."
        cp example.env .env
        echo -e "${YELLOW}⚠${NC}  Please edit .env and add your ANTHROPIC_API_KEY if you have one"
        echo -e "   (If you don't have an API key, Claude Code will run translations)"
    else
        echo -e "${RED}✗${NC} example.env not found!"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Check if API key is set
if grep -q "ANTHROPIC_API_KEY=sk-ant-" .env 2>/dev/null; then
    HAS_API_KEY=true
    echo -e "${GREEN}✓${NC} API key found in .env"
    MODE="API"
else
    HAS_API_KEY=false
    echo -e "${YELLOW}⚠${NC}  No API key found - will use Claude Code for translations"
    MODE="CLAUDE_CODE"
fi

echo ""

################################################################################
# Step 2: Create virtual environment if needed
################################################################################

echo -e "${YELLOW}[Step 2/5] Checking Python virtual environment...${NC}"

if [ ! -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment exists"
fi

echo ""

################################################################################
# Step 3: Activate venv and install dependencies
################################################################################

echo -e "${YELLOW}[Step 3/5] Installing dependencies...${NC}"

# Activate virtual environment
source venv/bin/activate

# Check if requirements are installed
if ! python -c "import anthropic" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Installing Python packages..."
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${GREEN}✓${NC} Dependencies already installed"
fi

echo ""

################################################################################
# Step 4: Determine which input to run
################################################################################

echo -e "${YELLOW}[Step 4/5] Selecting input file(s)...${NC}"

# Parse command line argument
INPUT_TYPE="${1:-menu}"

# Input files
SANITY_INPUT="data/input/sanity_check.json"
SAME_INPUT="data/input/same_sentence_progressive.json"
DIFFERENT_INPUT="data/input/different_sentences_progressive.json"

# If no argument or "menu", show interactive menu
if [ "$INPUT_TYPE" == "menu" ]; then
    echo ""
    echo "Select which input to run:"
    echo "  1) Sanity Check (1 test case, ~10 seconds)"
    echo "  2) Same Sentence Progressive (11 test cases, ~2-3 minutes)"
    echo "  3) Different Sentences Progressive (11 test cases, ~2-3 minutes)"
    echo "  4) All three (23 test cases total)"
    echo ""
    read -p "Enter choice (1-4): " choice

    case $choice in
        1) INPUT_TYPE="sanity" ;;
        2) INPUT_TYPE="same" ;;
        3) INPUT_TYPE="different" ;;
        4) INPUT_TYPE="all" ;;
        *) echo -e "${RED}✗${NC} Invalid choice"; exit 1 ;;
    esac
fi

# Set input files based on selection
case $INPUT_TYPE in
    sanity)
        INPUTS=("$SANITY_INPUT")
        DESCRIPTIONS=("Sanity Check")
        ;;
    same)
        INPUTS=("$SAME_INPUT")
        DESCRIPTIONS=("Same Sentence Progressive")
        ;;
    different)
        INPUTS=("$DIFFERENT_INPUT")
        DESCRIPTIONS=("Different Sentences Progressive")
        ;;
    all)
        INPUTS=("$SANITY_INPUT" "$SAME_INPUT" "$DIFFERENT_INPUT")
        DESCRIPTIONS=("Sanity Check" "Same Sentence Progressive" "Different Sentences Progressive")
        ;;
    *)
        echo -e "${RED}✗${NC} Invalid input type: $INPUT_TYPE"
        echo "Usage: $0 [sanity|same|different|all]"
        exit 1
        ;;
esac

echo -e "${GREEN}✓${NC} Selected: ${DESCRIPTIONS[*]}"
echo ""

################################################################################
# Step 5: Run experiments
################################################################################

echo -e "${YELLOW}[Step 5/5] Running experiments...${NC}"
echo ""

# Run each selected input
for i in "${!INPUTS[@]}"; do
    INPUT_FILE="${INPUTS[$i]}"
    DESCRIPTION="${DESCRIPTIONS[$i]}"

    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${BLUE}Running: $DESCRIPTION${NC}"
    echo -e "${BLUE}Input: $INPUT_FILE${NC}"
    echo -e "${BLUE}Mode: $MODE${NC}"
    echo -e "${BLUE}================================================================================${NC}"
    echo ""

    if [ ! -f "$INPUT_FILE" ]; then
        echo -e "${RED}✗${NC} Input file not found: $INPUT_FILE"
        continue
    fi

    if [ "$HAS_API_KEY" = true ]; then
        # Use API mode
        echo -e "${GREEN}✓${NC} Running with Anthropic API..."
        python src/run_with_agents.py "$INPUT_FILE"
    else
        # Use Claude Code mode
        echo -e "${YELLOW}⚠${NC}  Running in Claude Code mode..."
        echo -e "${YELLOW}⚠${NC}  This requires Claude Code to execute translations interactively"
        echo ""
        echo -e "${BLUE}INSTRUCTIONS:${NC}"
        echo -e "1. The script will call Python to run translations"
        echo -e "2. Claude Code will execute the SKILL agents"
        echo -e "3. Results will be saved automatically"
        echo ""

        # Call Python script that will use Claude Code
        python src/run_with_claude_code.py "$INPUT_FILE"
    fi

    echo ""
    echo -e "${GREEN}✓${NC} Completed: $DESCRIPTION"
    echo ""

    # Pause between experiments if running multiple
    if [ ${#INPUTS[@]} -gt 1 ] && [ $i -lt $((${#INPUTS[@]} - 1)) ]; then
        echo -e "${YELLOW}Press Enter to continue to next experiment...${NC}"
        read
    fi
done

################################################################################
# Summary
################################################################################

echo -e "${BLUE}================================================================================${NC}"
echo -e "${BLUE}                            EXPERIMENTS COMPLETE${NC}"
echo -e "${BLUE}================================================================================${NC}"
echo ""
echo -e "${GREEN}✓${NC} All experiments completed successfully!"
echo ""
echo "Results are in:"
if [ "$HAS_API_KEY" = true ]; then
    echo "  - results/api_run/"
else
    echo "  - results/claude_code_run/"
fi
echo ""
echo "To analyze results:"
echo "  python src/main.py analyze results/*/results_*.json"
echo ""
echo "To view graphs:"
echo "  open results/*/error_vs_distance.png"
echo ""
echo -e "${BLUE}================================================================================${NC}"
