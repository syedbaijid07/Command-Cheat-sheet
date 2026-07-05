# cheat-sit

A terminal command-line cheat sheet. Search any command by keyword, get live
suggestions as you type, and manage everything (add / edit / delete) from
the terminal itself. Data lives in a git repo, so updating on one device and
running `git pull` on another keeps every device in sync.

## What's in this repo

| File            | Purpose                                                              |
| --------------- | --------------------------------------------------------------------- |
| `cheat-sit`     | the tool itself (Python script)                                      |
| `data.json`     | your actual cheat sheet data (tools, commands, keywords)             |
| `data_add.txt`  | a template file — fill this in to bulk-import new commands           |

---

## 1. Requirements

- Python 3.8 or newer
- `pip`
- `git`

Check your Python version:

```bash
python3 --version
```

## 2. Install

### Step 1 — clone this repo to a fixed location

`cheat-sit` looks for its data at `~/.cheatsheet/data.json` by default, so
clone the repo directly into that folder:

```bash
git clone <this-repo-url> ~/.cheatsheet
```

Your folder should now look like:

```
~/.cheatsheet/
├── cheat-sit
├── data.json
└── data_add.txt
```

### Step 2 — install the one Python dependency

```bash
pip install prompt_toolkit --break-system-packages
```

(If you're inside a virtual environment, drop `--break-system-packages`.)

### Step 3 — make it runnable from anywhere

Copy the script into a folder that's on your `PATH` and make it executable:

```bash
mkdir -p ~/.local/bin
cp ~/.cheatsheet/cheat-sit ~/.local/bin/cheat-sit
chmod +x ~/.local/bin/cheat-sit
```

### Step 4 — make sure that folder is on your PATH

Add this line to `~/.bashrc` (or `~/.zshrc` if you use zsh):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell:

```bash
source ~/.bashrc
```

### Step 5 — confirm it works

```bash
cheat-sit delete branch
```

If you see a matching command printed, you're done.

> Want a shorter name like `cheat` instead of `cheat-sit`? Just change what
> you name the copy in Step 3: `cp ~/.cheatsheet/cheat-sit ~/.local/bin/cheat`

---

## 3. How to use it

### Search directly

```bash
cheat-sit open port
cheat-sit delete branch
```

### Interactive mode (live suggestions as you type)

```bash
cheat-sit
```

Start typing and matching commands appear as suggestions, the same way a
search bar shows results while you type. Press Enter to run the search,
then type the result number to open it.

Inside interactive mode you can also type:

| Command                  | What it does                          |
| ------------------------ | -------------------------------------- |
| `:add`                   | add one new entry via prompts          |
| `:import data_add.txt`   | bulk-import entries from a text file   |
| `:quit` or `:q`          | exit                                   |

### Opening a result

After a search, pick a result number to open its detail view. From there:

| Key | Action                        |
| --- | ------------------------------ |
| `e` | edit this entry                |
| `d` | delete this entry (asks to confirm) |
| `b` | go back to search              |

---

## 4. Adding new commands

### Option A — one at a time

```bash
cheat-sit --add
```

It will ask, in order:

1. **Tool name** — e.g. `nmap`
2. **Command** — e.g. `nmap -sV <target-ip>`
3. **Main keyword** — e.g. `open port with version`
4. **More keywords** (optional, comma separated) — extra phrases that should
   also match this command
5. **Description** (optional) — a short one-line explanation

### Option B — bulk import from a file

Open `data_add.txt` and fill it in using this exact format — one entry per
block, blocks separated by a blank line:

```
tool: nmap
command: nmap -sV <target-ip>
desc: scans open ports and detects service versions
keywords: open port with version, scan open ports, service version scan

tool: sqlmap
command: sqlmap -u <url> --dbs
desc: finds sql injection points and lists databases
keywords: sql injection test, find databases, sqli scan
```

Then run:

```bash
cheat-sit --import data_add.txt
```

or, from inside interactive mode:

```
:import data_add.txt
```

Every entry in the file gets appended to `data.json`.

**Field notes:**
- `tool:` and `command:` are required — an entry without both is skipped
- `desc:` is optional but recommended
- `keywords:` is a comma-separated list — write these in plain English,
  the way you'd naturally describe what the command does

---

## 5. Editing or removing a bad entry

If a command was added wrong (typo, wrong flag, bad keyword):

```bash
cheat-sit <search term that finds it>
```

Pick the result number, then press `e` to edit or `d` to delete. Editing
shows the current value in brackets — press Enter to keep it, or type a new
value to replace it.

---

## 6. Keeping devices in sync with git

`data.json` is just a tracked file in this repo. After any add / edit /
delete / import, `cheat-sit` will ask:

```
Commit and push changes now? (y/n)
```

Answer `y` and it runs `git add`, `git commit`, and `git push` for you.

On any other device, pull the update:

```bash
cd ~/.cheatsheet && git pull
```

The next time you run `cheat-sit` there, the new commands are already
available — no reinstall needed.

If you'd rather commit manually, answer `n` and run it yourself whenever
you're ready:

```bash
cd ~/.cheatsheet
git add data.json
git commit -m "add new commands"
git push
```

---

## 7. Using a different data file location

By default `cheat-sit` reads `~/.cheatsheet/data.json`. To point it at a
different file or repo path, set the `CHEAT_DATA` environment variable:

```bash
export CHEAT_DATA="/path/to/your/data.json"
```

Add that line to `~/.bashrc` to make it permanent.

---

## 8. data.json structure (for reference)

Each entry looks like this:

```json
{
  "tool": "nmap",
  "command": "nmap -sV <target-ip>",
  "desc": "scans open ports and detects service versions",
  "keywords": ["open port with version", "scan open ports", "service version scan"]
}
```

You normally won't need to edit this file by hand — use `--add`, `--import`,
or the edit/delete menu instead, so the JSON stays valid.

---

## 9. Troubleshooting

| Problem                              | Fix                                                                 |
| ------------------------------------- | -------------------------------------------------------------------- |
| `command not found: cheat-sit`        | `~/.local/bin` isn't on your PATH — redo Step 4, then `source ~/.bashrc` |
| `prompt_toolkit not installed`        | run `pip install prompt_toolkit --break-system-packages`            |
| Data file not found                    | make sure `~/.cheatsheet/data.json` exists, or set `CHEAT_DATA`     |
| Added a command but it's gone on my other laptop | run `git pull` inside `~/.cheatsheet` on that laptop        |
