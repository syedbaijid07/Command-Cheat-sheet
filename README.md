# cheat-sit

A fast terminal-based command-line cheat sheet with live search, interactive suggestions, and built-in command management.

Search any command by keyword, add/edit/delete entries directly from the terminal, and keep every device synchronized automatically through Git.

---

# Features

- 🔍 Fast keyword search
- ⚡ Live search suggestions while typing
- ➕ Add new commands
- ✏️ Edit existing commands
- 🗑 Delete commands
- 📥 Bulk import from a text file
- 🔄 Automatic Git pull on every launch
- ☁️ Git-based synchronization across devices
- 🐍 Built with Python

---

# Repository Structure

| File | Description |
|------|-------------|
| `cheat-sit.py` | Main application |
| `data.json` | Cheat sheet database |
| `data_add.txt` | Bulk import template |
| `install.sh` | Automatic installer |

---

# Requirements

- Python 3.8+
- pip
- Git

Verify Python:

```bash
python3 --version
```

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/syedbaijid07/Command-Cheat-sheet.git

cd Command-Cheat-sheet
```

---

## 2. Install Dependency

```bash
pip install prompt_toolkit --break-system-packages
```

If you're using a virtual environment:

```bash
pip install prompt_toolkit
```

---

## 3. Run Installer

```bash
chmod +x install.sh

./install.sh
```

The installer automatically:

- Creates the `cheat-sit` terminal command
- Places it inside `~/.local/bin`
- Enables automatic Git updates every time the tool starts

---

## 4. Add ~/.local/bin to PATH

If running

```bash
cheat-sit
```

returns

```text
command not found
```

add this to your shell configuration:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Reload your shell:

```bash
source ~/.bashrc
```

or

```bash
source ~/.zshrc
```

---

## 5. Launch

```bash
cheat-sit
```

If the interactive interface appears, installation is complete.

---

# Usage

## Search

```bash
cheat-sit open port

cheat-sit delete branch

cheat-sit sql injection
```

---

## Interactive Mode

```bash
cheat-sit
```

Start typing and matching commands appear instantly.

Available commands:

| Command | Description |
|---------|-------------|
| `:add` | Add a new command |
| `:import data_add.txt` | Bulk import commands |
| `:quit` or `:q` | Exit |

---

## Opening Results

Choose the result number.

Inside the details page:

| Key | Action |
|-----|--------|
| `e` | Edit |
| `d` | Delete |
| `b` | Back |

---

# Adding Commands

## Option 1 — Interactive

```bash
cheat-sit --add
```

You'll be asked for:

1. Tool name
2. Command
3. Main keyword
4. Additional keywords
5. Description

Example

```
Tool:
nmap

Command:
nmap -sV <target>

Keyword:
open port

Extra keywords:
version detection, service scan

Description:
Detect services running on open ports.
```

---

## Option 2 — Bulk Import

Edit `data_add.txt`

Example:

```text
tool: nmap
command: nmap -sV <target-ip>
desc: Detect service versions
keywords: open port, service version, scan ports

tool: sqlmap
command: sqlmap -u <url> --dbs
desc: Enumerate databases
keywords: sql injection, database enumeration, sqli
```

Import:

```bash
cheat-sit --import data_add.txt
```

or inside interactive mode:

```text
:import data_add.txt
```

---

# Editing & Deleting

Search for the command.

Example:

```bash
cheat-sit nmap
```

Choose the result.

Press:

- `e` to edit
- `d` to delete

---

# Git Synchronization

Every launch automatically executes:

```bash
git pull origin main
```

to fetch the newest commands.

Whenever you add, edit, or delete an entry you'll be asked:

```text
Commit and push changes now? (y/n)
```

Selecting **y** automatically runs:

```bash
git add data.json

git commit -m "update commands"

git push
```

You can also push manually:

```bash
cd Command-Cheat-sheet

git add data.json

git commit -m "update"

git push
```

---

# data.json Format

Each record looks like:

```json
{
  "tool": "nmap",
  "command": "nmap -sV <target-ip>",
  "desc": "Detect service versions",
  "keywords": [
    "open port",
    "service version",
    "scan ports"
  ]
}
```

Normally you should use:

- `--add`
- `--import`
- Edit menu

instead of editing JSON manually.

---

# Troubleshooting

| Problem | Solution |
|----------|----------|
| `command not found: cheat-sit` | Add `~/.local/bin` to PATH |
| `prompt_toolkit not installed` | Install with `pip install prompt_toolkit` |
| Permission denied | Run `chmod +x install.sh` |
| Git update failed | Check internet connection and Git authentication |

---

# License

This project is open source.

---

Made with ❤️ for developers, students, and cybersecurity enthusiasts.
