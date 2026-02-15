#!/bin/bash
#
# Auto-restart wrapper for Polymarket trading bot
#
# This script automatically restarts the bot when the market changes.
# Exit code 42 = market changed, restart requested
# Any other exit code = stop the loop
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Polymarket Bot - Auto-Restart Mode${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "The bot will automatically restart when the market changes."
echo "Press Ctrl+C to stop."
echo ""

# Counter for restarts
RESTART_COUNT=0

while true; do
    if [ $RESTART_COUNT -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}RESTARTING BOT (restart #$RESTART_COUNT)${NC}"
        echo -e "${YELLOW}========================================${NC}"
        echo ""
        sleep 2
    fi
    
    # Run the bot
    python3 apps/run_flash_crash.py
    EXIT_CODE=$?
    
    # Check exit code
    if [ $EXIT_CODE -eq 42 ]; then
        # Market changed - restart
        echo ""
        echo -e "${GREEN}Market changed detected. Restarting bot...${NC}"
        RESTART_COUNT=$((RESTART_COUNT + 1))
        continue
    elif [ $EXIT_CODE -eq 0 ]; then
        # Normal exit
        echo ""
        echo -e "${GREEN}Bot exited normally.${NC}"
        break
    else
        # Error exit
        echo ""
        echo -e "${RED}Bot exited with error code $EXIT_CODE${NC}"
        break
    fi
done

echo ""
echo -e "${GREEN}Total restarts: $RESTART_COUNT${NC}"
echo -e "${GREEN}Done.${NC}"

