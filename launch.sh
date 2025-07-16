#!/bin/bash

# Exit on error
set -e

# Activate virtual environment
source venv/bin/activate || { echo "❌ Could not activate venv. Make sure it's set up."; exit 1; }
echo "✅ Virtual environment activated"

# Load .env variables correctly (exported)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_PATH="$SCRIPT_DIR/.env"

if [ -f "$ENV_PATH" ]; then
    set -a
    source "$ENV_PATH"
    set +a
    echo "✅ Loaded .env variables from .env"
else
    echo "⚠️ .env file not found at $ENV_PATH"
fi

# ----------- Handle CLI Options ----------
MODE="test"
RUN_ALL=false
CLI_BATCH_INDEX=""
SETUP=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --prod) MODE="prod" ;;
        --test) MODE="test" ;;
        --all) RUN_ALL=true ;;
        --batch=*) CLI_BATCH_INDEX="${1#*=}" ;;
        --setup) SETUP=true ;;
        *) echo "⚠️ Unknown option: $1" ;;
    esac
    shift
done

# ----------- Environment Mode ------------
if [ "$MODE" == "prod" ]; then
    export TEST_MODE=false
    echo "🚀 Running in PRODUCTION mode"
else
    export TEST_MODE=true
    echo "🧪 Running in TEST mode"
fi

# ---------- First-time Setup -------------
# after git clone, new venv, or first-time setup
# Command: `./launch.sh --setup` (note: it only installs dependencies & browsers, it will not continue to run spider)
if [ "$SETUP" = true ]; then
    # Install required packages
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt

    # Install Playwright browser binaries
    echo "🧭 Installing Playwright browsers..."
    playwright install

    echo "✅ Setup complete"
    echo "👉 To run the spider, use: ./launch.sh"
    exit 0
fi

# ---------Cleanup old logs-----------------
MAX_LOG_RUNS=1 # Keep only the latest n log runs

LOG_PARENT="logs"
if [ -d "$LOG_PARENT" ]; then
    LOG_DIRS=($(find "$LOG_PARENT" -mindepth 1 -maxdepth 1 -type d | sort -r))
    if [ "${#LOG_DIRS[@]}" -gt "$MAX_LOG_RUNS" ]; then
        echo "🧹 Cleaning up old logs..."
        for dir in "${LOG_DIRS[@]:$MAX_LOG_RUNS}"; do
            echo "🗑️ Removing $dir"
            rm -rf "$dir"
        done
    else
        echo "ℹ️ No old logs to clean up."
    fi
fi

# ----------- Log Directory ---------------
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
mkdir -p logs/$timestamp

# ----------- Batch Mode ------------------
# BATCH_INDEX Precedence order: Use CLI value > fallback to .env value > fallback to default (0)
if [ -n "$CLI_BATCH_INDEX" ]; then
    export BATCH_INDEX="$CLI_BATCH_INDEX"
elif [ -z "$BATCH_INDEX" ]; then
    export BATCH_INDEX=0
fi

if [ "$RUN_ALL" = true ]; then
    echo "🔁 Running all batches..."
    for i in {0..254}; do # adjust it for production mode based on data size
        export BATCH_INDEX=$i
        echo "▶️ Batch $BATCH_INDEX"
        LOG_FILE=logs/$timestamp/batch_$BATCH_INDEX.log
        scrapy crawl agoda_search_browser -s LOG_FILE=$LOG_FILE
    done
else
    echo "▶️ Running single batch (BATCH_INDEX=$BATCH_INDEX)"
    LOG_FILE=logs/$timestamp/batch_$BATCH_INDEX.log
    scrapy crawl agoda_search_browser -s LOG_FILE=$LOG_FILE
fi

echo "✅ Done"


# | Mode                    | Command Example                 |
# | ---------------         | ------------------------------- |
# | .env batch val, then 0  | `./launch.sh`                   |
# | Test batch 10           | `./launch.sh --batch=10`        |
# | All batches             | `./launch.sh --all`             |
# | Production mode         | `./launch.sh --prod`            |
# | Prod batch 20           | `./launch.sh --prod --batch=20` |
