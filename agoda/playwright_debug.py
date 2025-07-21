import os
import sys

TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"

async def debug_pause(page, context):
    if TEST_MODE:
        print("⚠️ Pausing browser for manual inspection...")
        await page.pause()
        print("🛑 Stopping after pause for manual inspection.")
        sys.exit(0)  # <-- Forcefully stops the spider after pause