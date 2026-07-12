#!/bin/bash

# ==========================================
# CYBERPUNK THEME COLORS & STYLES
# ==========================================
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

clear

# ==========================================
# ASCII ART BANNER
# ==========================================
echo -e "${RED}${BOLD}"
cat << "EOF"
  ____ _   _ _____    _  _____       ___ ___ _____ 
 / ___| | | | ____|  / \|_   _|     / __|_ _|_   _|
| |   | |_| |  _|   / _ \ | | _____ \__ \| |  | |  
| |___|  _  | |___ / ___ \| | |_____|___/| |  | |  
 \____|_| |_|_____/_/   \_\_|       |___/___| |_|  

              U N I N S T A L L
EOF
echo -e "${NC}"

echo -e "${MAGENTA}[ SYS_INIT ]${NC} Booting removal sequence..."
sleep 0.5

# Variables
BIN_DIR="$HOME/.local/bin"
COMMAND_NAME="cheat-sit"
BIN_PATH="$BIN_DIR/$COMMAND_NAME"
DATA_DIR="$HOME/.cheatsheet"

# ==========================================
# STEP 1: REMOVE THE EXECUTABLE
# ==========================================
echo -e "${CYAN}[ SCAN ]${NC} Looking for executable at: ${YELLOW}$BIN_PATH${NC}"
sleep 0.4

if [ -f "$BIN_PATH" ]; then
    rm -f "$BIN_PATH"
    echo -e "  ${GREEN}[+]${NC} Executable purged from the grid."
else
    echo -e "  ${YELLOW}[!]${NC} No executable found there. Already clean, or installed elsewhere."
fi
sleep 0.3

# ==========================================
# STEP 2: OPTIONALLY REMOVE THE DATA / GIT REPO
# ==========================================
echo ""
echo -e "${CYAN}[ SCAN ]${NC} Data directory located at: ${YELLOW}$DATA_DIR${NC}"

if [ -d "$DATA_DIR" ]; then
    echo -e "${RED}${BOLD}[ WARNING ]${NC} This folder holds your cheat sheet data (${YELLOW}data.json${NC}) and the"
    echo -e "            git repository. Deleting it is ${BOLD}permanent${NC} unless it's already pushed"
    echo -e "            and safely stored on GitHub."
    echo ""
    read -r -p "$(echo -e "${MAGENTA}[ CONFIRM ]${NC} Delete $DATA_DIR too? (y/N): ")" confirm_delete
    case "$confirm_delete" in
        [yY][eE][sS]|[yY])
            rm -rf "$DATA_DIR"
            echo -e "  ${GREEN}[+]${NC} Data sector wiped."
            ;;
        *)
            echo -e "  ${CYAN}[i]${NC} Data directory left intact. Nothing was touched."
            ;;
    esac
else
    echo -e "  ${YELLOW}[!]${NC} No data directory found there."
fi

# ==========================================
# STEP 3: REMIND ABOUT THE PATH LINE
# ==========================================
echo ""
echo -e "${CYAN}[ NOTICE ]${NC} If you added a PATH line for this tool in your shell config"
echo -e "           (${BOLD}~/.bashrc${NC} or ${BOLD}~/.zshrc${NC}), e.g.:"
echo -e "             ${YELLOW}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
echo -e "           it's safe to leave it (other tools may use that folder too), but"
echo -e "           remove it by hand if you no longer need it."

# ==========================================
# OUTRO
# ==========================================
echo ""
echo -e "${GREEN}${BOLD}[ REMOVAL COMPLETE ]${NC} ${CYAN}$COMMAND_NAME${NC} has been disconnected from the grid."
echo ""
