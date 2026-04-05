#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Buy Commodity — One-Command Setup Script
# Usage:  chmod +x setup.sh && ./setup.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e

ORANGE='\033[0;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}${ORANGE}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}${ORANGE}║   Buy Commodity — Setup Script       ║${NC}"
echo -e "${BOLD}${ORANGE}╚══════════════════════════════════════╝${NC}"
echo ""

# ── Check Python ──
echo -e "${CYAN}[1/6]${NC} Checking Python…"
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}✗ Python 3 not found. Please install Python 3.9+ and retry.${NC}"
  exit 1
fi
PYTHON=$(python3 --version)
echo -e "${GREEN}✓ Found ${PYTHON}${NC}"


# ── Install dependencies ──
echo -e "${CYAN}[3/6]${NC} Installing dependencies…"
pip install --quiet --upgrade pip
# pip install --quiet -r requirements.txt
echo -e "${GREEN}✓ All packages installed${NC}"

# ── Migrations ──
echo -e "${CYAN}[4/6]${NC} Running migrations…"
python manage.py makemigrations --no-input
python manage.py migrate --no-input
echo -e "${GREEN}✓ Database ready (db.sqlite3)${NC}"

# ── Seed data ──
echo -e "${CYAN}[5/6]${NC} Seeding product data…"
python manage.py seed_data
echo -e "${GREEN}✓ Categories and products seeded${NC}"

# ── Done ──
echo ""
echo -e "${CYAN}[6/6]${NC} Starting development server…"
echo ""
echo -e "${BOLD}${GREEN}══════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}  Setup complete! Open these in browser:  ${NC}"
echo -e "${BOLD}${GREEN}══════════════════════════════════════════${NC}"
echo ""
echo -e "  ${ORANGE}API:          ${NC}http://localhost:8000/api/"
echo -e "  ${ORANGE}Django Admin: ${NC}http://localhost:8000/admin/"
echo -e "  ${ORANGE}Customer Site:${NC} Open ../site1/index.html"
echo -e "  ${ORANGE}Admin Panel:  ${NC} Open ../site2/index.html"
echo ""
echo -e "${BOLD}  Press Ctrl+C to stop the server${NC}"
echo ""

python manage.py runserver