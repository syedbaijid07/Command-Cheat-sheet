#!/usr/bin/env python3
"""
cheat-sit - terminal cheat sheet command finder with live suggestions.

Usage:
    cheat-sit                        interactive mode (live suggestions while typing)
    cheat-sit delete branch          direct search
    cheat-sit --import data_add.txt  bulk add entries from a text file
    cheat-sit --add                  add one new entry via prompts

Data file location (checked in order):
    1. $CHEAT_DATA env var
    2. ~/.cheatsheet/data.json   (recommended: keep this folder as a git repo)
    3. data.json next to this script (fallback, local testing)

Import file format (one entry per block, blocks separated by a blank line)
- see data_add.txt for a template:
    tool: nmap
    command: nmap -sV <target-ip>
    keywords: open port with version, scan open ports, service version scan
"""

import json
import os
import subprocess
import sys

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.shortcuts import CompleteStyle
    from prompt_toolkit.styles import Style
except ImportError:
    print("prompt_toolkit not installed. Run: pip install prompt_toolkit --break-system-packages")
    sys.exit(1)

VERSION = "2.0"

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
WHITE = "\033[37m"
BG_BLACK = "\033[40m"

THEMES = {
    "default": {
        "label": "Default (Normal)",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "primary": "\033[36m",
        "secondary": "\033[33m",
        "accent": "\033[35m",
        "success": "\033[32m",
        "error": "\033[31m",
        "muted": "\033[90m",
        "highlight": "\033[97m",
        "border": "\033[36m",
        "prompt": "cheat",
        "banner": (
            "  ____ _   _ _____    _  _____       ___ ___ _____ \n"
            " / ___| | | | ____|  / \\|_   _|     / __|_ _|_   _|\n"
            "| |   | |_| |  _|   / _ \\ | | _____ \\__ \\| |  | |  \n"
            "| |___|  _  | |___ / ___ \\| | |_____|___/| |  | |  \n"
            " \\____|_| |_|_____/_/   \\_\\_|       |___/___| |_|  "
        ),
        "prompt_style": Style.from_dict({
            "prompt": "bold fg:#00ffff",
            "completion-menu": "bg:#1e1e2e fg:#cdd6f4",
            "completion-menu.completion": "fg:#89b4fa",
            "completion-menu.completion.current": "bg:#45475a fg:#f9e2af bold",
            "completion-menu.meta": "fg:#6c7086",
            "completion-menu.meta.current": "fg:#a6adc8",
        }),
    },
    "light": {
        "label": "Light",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "primary": "\033[34m",
        "secondary": "\033[35m",
        "accent": "\033[36m",
        "success": "\033[32m",
        "error": "\033[31m",
        "muted": "\033[90m",
        "highlight": "\033[97m",
        "border": "\033[34m",
        "prompt": "cheat",
        "banner": (
            "  ╔══════════════════════════════════════╗\n"
            "  ║       CHEAT-SIT  ·  LIGHT MODE       ║\n"
            "  ╚══════════════════════════════════════╝"
        ),
        "prompt_style": Style.from_dict({
            "prompt": "bold fg:#1e66f5",
            "completion-menu": "bg:#eff1f5 fg:#4c4f69",
            "completion-menu.completion": "fg:#1e66f5",
            "completion-menu.completion.current": "bg:#ccd0da fg:#8839ef bold",
            "completion-menu.meta": "fg:#9ca0b0",
            "completion-menu.meta.current": "fg:#6c6f85",
        }),
    },
    "dark": {
        "label": "Dark",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "primary": "\033[90m",
        "secondary": "\033[37m",
        "accent": "\033[97m",
        "success": "\033[32m",
        "error": "\033[31m",
        "muted": "\033[2;37m",
        "highlight": "\033[1;37m",
        "border": "\033[90m",
        "prompt": "cheat",
        "banner": (
            "  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓\n"
            "  ▓  C H E A T - S I T  ·  D A R K  ▓\n"
            "  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
        ),
        "prompt_style": Style.from_dict({
            "prompt": "bold fg:#a6adc8",
            "completion-menu": "bg:#11111b fg:#bac2de",
            "completion-menu.completion": "fg:#89b4fa",
            "completion-menu.completion.current": "bg:#313244 fg:#cdd6f4 bold",
            "completion-menu.meta": "fg:#585b70",
            "completion-menu.meta.current": "fg:#7f849c",
        }),
    },
    "colorful": {
        "label": "Colorful",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "primary": "\033[96m",
        "secondary": "\033[93m",
        "accent": "\033[95m",
        "success": "\033[92m",
        "error": "\033[91m",
        "muted": "\033[2m",
        "highlight": "\033[1;97m",
        "border": "\033[95m",
        "prompt": "cheat",
        "banner": (
            "  \033[91m█\033[93m█\033[92m█\033[96m█\033[94m█\033[95m█  CHEAT-SIT  \033[91m█\033[93m█\033[92m█\033[96m█\033[94m█\033[95m█\n"
            "       \033[96m╭─────────────────────────────╮\033[0m\n"
            "       \033[93m│  \033[92mR\033[96mA\033[95mI\033[94mN\033[91mB\033[93mO\033[92mW\033[96m  \033[95mM\033[94mO\033[91mD\033[93mE\033[92m  \033[93m│\033[0m\n"
            "       \033[96m╰─────────────────────────────╯\033[0m"
        ),
        "prompt_style": Style.from_dict({
            "prompt": "bold fg:#f5c2e7",
            "completion-menu": "bg:#1e1e2e fg:#cdd6f4",
            "completion-menu.completion": "fg:#89dceb",
            "completion-menu.completion.current": "bg:#45475a fg:#f9e2af bold",
            "completion-menu.meta": "fg:#cba6f7",
            "completion-menu.meta.current": "fg:#fab387",
        }),
    },
    "hacker": {
        "label": "Hacker Vibe",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "primary": "\033[32m",
        "secondary": "\033[92m",
        "accent": "\033[1;32m",
        "success": "\033[92m",
        "error": "\033[31m",
        "muted": "\033[2;32m",
        "highlight": "\033[1;92m",
        "border": "\033[32m",
        "prompt": "root@cheat",
        "banner": (
            "\033[32m"
            "  ┌─────────────────────────────────────────┐\n"
            "  │  > ACCESS GRANTED                       │\n"
            "  │  > INITIALIZING COMMAND MATRIX...       │\n"
            "  │  > CHEAT-SIT v2.0 [HACKER MODE]         │\n"
            "  └─────────────────────────────────────────┘"
            "\033[0m"
        ),
        "prompt_style": Style.from_dict({
            "prompt": "bold fg:#00ff00",
            "completion-menu": "bg:#000000 fg:#00ff00",
            "completion-menu.completion": "fg:#00cc00",
            "completion-menu.completion.current": "bg:#003300 fg:#00ff00 bold",
            "completion-menu.meta": "fg:#006600",
            "completion-menu.meta.current": "fg:#00aa00",
        }),
    },
    "anonymous": {
        "label": "Anonymous",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "primary": "\033[97m",
        "secondary": "\033[92m",
        "accent": "\033[1;97m",
        "success": "\033[92m",
        "error": "\033[31m",
        "muted": "\033[2;37m",
        "highlight": "\033[1;97m",
        "border": "\033[90m",
        "prompt": "anon",
        "banner": (
            "\033[97m"
            "       █████╗ ███╗   ██╗ ██████╗ ███╗   ██╗\n"
            "      ██╔══██╗████╗  ██║██╔═══██╗████╗  ██║\n"
            "      ███████║██╔██╗ ██║██║   ██║██╔██╗ ██║\n"
            "      ██╔══██║██║╚██╗██║██║   ██║██║╚██╗██║\n"
            "      ██║  ██║██║ ╚████║╚██████╔╝██║ ╚████║\n"
            "      ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═══╝\n"
            "\033[92m      WE ARE ANONYMOUS · WE ARE CHEAT-SIT\033[0m"
        ),
        "prompt_style": Style.from_dict({
            "prompt": "bold fg:#ffffff",
            "completion-menu": "bg:#0a0a0a fg:#ffffff",
            "completion-menu.completion": "fg:#00ff41",
            "completion-menu.completion.current": "bg:#1a1a1a fg:#00ff41 bold",
            "completion-menu.meta": "fg:#555555",
            "completion-menu.meta.current": "fg:#888888",
        }),
    },
}

CURRENT_THEME = THEMES["default"]
PROMPT_STYLE = CURRENT_THEME["prompt_style"]


def apply_theme(theme_key):
    global CURRENT_THEME, PROMPT_STYLE, BOLD, DIM, CYAN, YELLOW, RED, GREEN, MAGENTA, BLUE, WHITE
    theme = THEMES.get(theme_key, THEMES["default"])
    CURRENT_THEME = theme
    PROMPT_STYLE = theme["prompt_style"]
    BOLD = theme["bold"]
    DIM = theme["dim"]
    CYAN = theme["primary"]
    YELLOW = theme["secondary"]
    MAGENTA = theme["accent"]
    GREEN = theme["success"]
    RED = theme["error"]
    BLUE = theme["border"]


# ---------- paths & settings ----------

def cheatsheet_dir():
    if os.environ.get("CHEAT_DATA"):
        return os.path.dirname(os.path.abspath(os.environ["CHEAT_DATA"]))
    home_path = os.path.expanduser("~/.cheatsheet/data.json")
    if os.path.exists(home_path):
        return os.path.dirname(home_path)
    return os.path.expanduser("~/.cheatsheet")


def bundled_data_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


def is_valid_data_file(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return isinstance(data, list)
    except (json.JSONDecodeError, OSError):
        return False


def data_path():
    if os.environ.get("CHEAT_DATA"):
        return os.environ["CHEAT_DATA"]
    home_path = os.path.expanduser("~/.cheatsheet/data.json")
    if os.path.isdir(os.path.dirname(home_path)):
        return home_path
    if is_valid_data_file(home_path):
        return home_path
    return bundled_data_path()


def settings_path():
    return os.path.join(cheatsheet_dir(), "settings.json")


def load_settings():
    path = settings_path()
    defaults = {"theme": "default"}
    if not os.path.exists(path):
        return defaults
    try:
        with open(path, "r", encoding="utf-8") as f:
            saved = json.load(f)
        if saved.get("theme") not in THEMES:
            saved["theme"] = "default"
        return {**defaults, **saved}
    except (json.JSONDecodeError, OSError):
        return defaults


def save_settings(settings):
    dirname = os.path.dirname(settings_path())
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(settings_path(), "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def init_theme():
    settings = load_settings()
    apply_theme(settings.get("theme", "default"))
    return settings


def load_data(path):
    if is_valid_data_file(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    bundled = bundled_data_path()
    if not is_valid_data_file(bundled):
        return []

    with open(bundled, "r", encoding="utf-8") as f:
        data = json.load(f)

    home_path = os.path.expanduser("~/.cheatsheet/data.json")
    if path == home_path or (os.path.exists(path) and os.path.getsize(path) == 0):
        save_data(home_path, data)
        print(f"{YELLOW}Repaired empty ~/.cheatsheet/data.json from bundled copy.{RESET}")
    return data


def save_data(path, data):
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------- UI helpers ----------

def hr(char="─", width=52):
    return f"{CURRENT_THEME['border']}{char * width}{RESET}"


def print_banner():
    banner = CURRENT_THEME["banner"]
    if CURRENT_THEME is THEMES["colorful"]:
        print(banner)
    else:
        print(f"{CURRENT_THEME['primary']}{BOLD}{banner}{RESET}")
    print(f"{DIM}  v{VERSION}  ·  {len(load_data(data_path()))} commands  ·  theme: {CURRENT_THEME['label']}{RESET}")
    print(hr())


def print_help():
    print(f"\n{BOLD}{CURRENT_THEME['accent']}Commands{RESET}")
    print(f"  {CURRENT_THEME['secondary']}:setting{RESET}  {DIM}open theme & settings menu{RESET}")
    print(f"  {CURRENT_THEME['secondary']}:add{RESET}     {DIM}add a new entry{RESET}")
    print(f"  {CURRENT_THEME['secondary']}:import <file>{RESET}  {DIM}bulk import{RESET}")
    print(f"  {CURRENT_THEME['secondary']}:help{RESET}    {DIM}show this help{RESET}")
    print(f"  {CURRENT_THEME['secondary']}:clear{RESET}   {DIM}clear screen{RESET}")
    print(f"  {CURRENT_THEME['secondary']}:quit{RESET}    {DIM}exit{RESET}")
    print(f"\n{DIM}Type any keyword to search. Tab/Enter picks a live suggestion.{RESET}\n")


def settings_menu(settings):
    theme_keys = list(THEMES.keys())
    while True:
        print(f"\n{BOLD}{CURRENT_THEME['accent']}═══ Settings ═══{RESET}")
        print(f"{DIM}Config file: {settings_path()}{RESET}")
        print(f"\n{BOLD}Theme{RESET}  {DIM}(current: {CURRENT_THEME['label']}){RESET}\n")
        for i, key in enumerate(theme_keys, 1):
            marker = f" {GREEN}◀ active{RESET}" if settings.get("theme") == key else ""
            print(f"  {CURRENT_THEME['secondary']}{i}.{RESET} {THEMES[key]['label']}{marker}")
        print(f"\n{DIM}[1-{len(theme_keys)}] pick theme  ·  [b] back  ·  [h] help{RESET}")
        choice = input(f"{CURRENT_THEME['secondary']}> {RESET}").strip().lower()
        if choice in ("b", "back", ""):
            return
        if choice == "h":
            print_help()
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(theme_keys):
            selected = theme_keys[int(choice) - 1]
            settings["theme"] = selected
            save_settings(settings)
            apply_theme(selected)
            print(f"\n{GREEN}Theme set to {CURRENT_THEME['label']}.{RESET}")
            print_banner()
            continue
        print(f"{RED}Invalid choice.{RESET}")


# ---------- search ----------

def search(data, query):
    q = query.strip().lower()
    if not q:
        return data
    results = []
    seen = set()
    for item in data:
        haystack = [item["tool"], item["command"], item.get("desc", "")]
        haystack += item.get("keywords", [])
        text = " ".join(haystack).lower()
        if q in text:
            key = (item["tool"].strip().lower(), item["command"].strip().lower())
            if key in seen:
                continue
            seen.add(key)
            results.append(item)
    return results


# ---------- completer: shows live suggestions while typing ----------

class CheatCompleter(Completer):
    def __init__(self, data):
        self.data = data

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lower()
        if not text:
            return
        seen = set()
        for item in self.data:
            dedupe_key = (item["tool"].lower(), item["command"].lower())

            matched_keyword = None
            for kw in item.get("keywords", []):
                if text in kw.lower():
                    matched_keyword = kw
                    break

            tool_match = text in item["tool"].lower()
            command_match = text in item["command"].lower()
            desc_match = text in item.get("desc", "").lower()

            if not (matched_keyword or tool_match or command_match or desc_match):
                continue
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            display = f"[{item['tool']}] {item['command']}"

            keywords = item.get("keywords", [])
            short_label = matched_keyword or (keywords[0] if keywords else item.get("desc", ""))
            if len(short_label) > 32:
                short_label = short_label[:29] + "..."

            yield Completion(
                item["command"],
                start_position=-len(document.text_before_cursor),
                display=display,
                display_meta=short_label,
            )


def build_completer(data):
    return CheatCompleter(data)


def prompt_message():
    return [
        ("class:prompt", f"{CURRENT_THEME['prompt']}> "),
    ]


# ---------- add / edit / delete ----------

def ask(label, default=""):
    suffix = f" [{default}]" if default else ""
    val = input(f"{CURRENT_THEME['primary']}{label}{RESET}{suffix}: ").strip()
    return val if val else default


def add_entry(data):
    print(f"\n{BOLD}{CURRENT_THEME['accent']}Add new entry{RESET}")
    tool = ask("Tool name (e.g. nmap)")
    if not tool:
        print(f"{DIM}Cancelled.{RESET}")
        return None
    command = ask("Command (e.g. nmap -sV <target-ip>)")
    main_keyword = ask("Main keyword (e.g. open port with version)")
    extra = ask("More keywords, comma separated (optional)")
    keywords = [main_keyword] if main_keyword else []
    if extra:
        keywords += [k.strip() for k in extra.split(",") if k.strip()]
    desc = ask("Short description (optional)")
    entry = {"tool": tool, "command": command, "desc": desc, "keywords": keywords}
    data.append(entry)
    print(f"{GREEN}Added.{RESET}")
    return entry


def edit_entry(entry):
    print(f"\n{BOLD}{CURRENT_THEME['accent']}Edit entry{RESET} ({DIM}press enter to keep current value{RESET})")
    entry["tool"] = ask("Tool name", entry["tool"])
    entry["command"] = ask("Command", entry["command"])
    entry["desc"] = ask("Description", entry.get("desc", ""))
    kw = ask("Keywords, comma separated", ", ".join(entry.get("keywords", [])))
    entry["keywords"] = [k.strip() for k in kw.split(",") if k.strip()]
    print(f"{GREEN}Updated.{RESET}")


def delete_entry(data, entry):
    confirm = input(f"{RED}Delete '{entry['command']}'? (y/n): {RESET}").strip().lower()
    if confirm == "y":
        data.remove(entry)
        print(f"{GREEN}Deleted.{RESET}")
        return True
    print(f"{DIM}Cancelled.{RESET}")
    return False


# ---------- import from file ----------

def parse_import_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
    entries = []
    for block in blocks:
        entry = {"tool": "", "command": "", "desc": "", "keywords": []}
        for line in block.splitlines():
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            if key == "tool":
                entry["tool"] = val
            elif key == "command":
                entry["command"] = val
            elif key == "desc":
                entry["desc"] = val
            elif key == "keywords":
                entry["keywords"] = [k.strip() for k in val.split(",") if k.strip()]
        if entry["tool"] and entry["command"]:
            entries.append(entry)
    return entries


def import_from_file(data, path):
    if not os.path.exists(path):
        print(f"{RED}File not found: {path}{RESET}")
        return 0
    new_entries = parse_import_file(path)
    data.extend(new_entries)
    print(f"{GREEN}Imported {len(new_entries)} entries from {path}{RESET}")
    return len(new_entries)


# ---------- git sync ----------

def offer_git_sync(path):
    repo_dir = os.path.dirname(path)
    if not os.path.isdir(os.path.join(repo_dir, ".git")):
        return
    choice = input(f"{DIM}Commit and push changes now? (y/n): {RESET}").strip().lower()
    if choice != "y":
        return
    try:
        subprocess.run(["git", "-C", repo_dir, "add", "data.json"], check=True)
        subprocess.run(["git", "-C", repo_dir, "commit", "-m", "update cheat sheet"], check=True)
        subprocess.run(["git", "-C", repo_dir, "push"], check=True)
        print(f"{GREEN}Pushed.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Git command failed: {e}{RESET}")


# ---------- detail / menu screens ----------

def print_entry(entry):
    print(f"\n{hr('═')}")
    print(f"{CYAN}[{entry['tool']}]{RESET} {BOLD}{CURRENT_THEME['highlight']}{entry['command']}{RESET}")
    if entry.get("desc"):
        print(f"  {DIM}{entry['desc']}{RESET}")
    if entry.get("keywords"):
        print(f"  {DIM}keywords: {', '.join(entry['keywords'])}{RESET}")
    print(hr("═"))


def matched_keyword_for(item, query):
    q = query.strip().lower()
    if not q:
        return None
    for kw in item.get("keywords", []):
        if q in kw.lower():
            return kw
    return None


def print_results(results, query=""):
    if not results:
        print(f"\n{DIM}No matching command found.{RESET}")
        return
    count_label = f"{len(results)} result{'s' if len(results) != 1 else ''}"
    print(f"\n{BOLD}{CURRENT_THEME['accent']}{count_label}{RESET} {DIM}for \"{query}\"{RESET}" if query else f"\n{BOLD}{count_label}{RESET}")
    print(hr())
    for i, item in enumerate(results, 1):
        num = f"{CURRENT_THEME['secondary']}{i:>2}.{RESET}"
        tool = f"{CYAN}[{item['tool']}]{RESET}"
        print(f" {num} {tool} {item['command']}")
        kw = matched_keyword_for(item, query)
        if kw:
            print(f"     {DIM}▸ matched \"{kw}\"  ·  {item.get('desc', '')}{RESET}")
        elif item.get("desc"):
            print(f"     {DIM}▸ {item['desc']}{RESET}")
    print(hr())


def detail_menu(data, entry, path):
    while True:
        print_entry(entry)
        print(f"{DIM}[e] edit  [d] delete  [c] copy command  [b] back{RESET}")
        choice = input(f"{CURRENT_THEME['secondary']}> {RESET}").strip().lower()
        if choice == "e":
            edit_entry(entry)
            save_data(path, data)
            offer_git_sync(path)
        elif choice == "d":
            if delete_entry(data, entry):
                save_data(path, data)
                offer_git_sync(path)
            return
        elif choice == "c":
            try:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=entry["command"].encode(),
                    check=True,
                    stdout=subprocess.DEVNULL,
                )
                print(f"{GREEN}Copied to clipboard.{RESET}")
            except (FileNotFoundError, subprocess.CalledProcessError):
                print(f"{DIM}Clipboard copy needs xclip. Command: {entry['command']}{RESET}")
        elif choice == "b" or choice == "":
            return


def interactive(data, path, settings):
    os.system("clear" if os.name != "nt" else "cls")
    print_banner()
    print_help()

    while True:
        completer = build_completer(data)
        try:
            query = prompt(
                prompt_message(),
                completer=completer,
                complete_while_typing=True,
                complete_style=CompleteStyle.COLUMN,
                style=PROMPT_STYLE,
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}Goodbye.{RESET}")
            break

        if not query:
            continue
        if query in (":quit", ":q"):
            print(f"{DIM}Goodbye.{RESET}")
            break
        if query in (":setting", ":settings"):
            settings_menu(settings)
            continue
        if query == ":help":
            print_help()
            continue
        if query == ":clear":
            os.system("clear" if os.name != "nt" else "cls")
            print_banner()
            continue
        if query == ":add":
            add_entry(data)
            save_data(path, data)
            offer_git_sync(path)
            continue
        if query.startswith(":import"):
            parts = query.split(maxsplit=1)
            if len(parts) == 2:
                import_from_file(data, parts[1].strip())
                save_data(path, data)
                offer_git_sync(path)
            else:
                print(f"{RED}Usage: :import <file path>{RESET}")
            continue

        results = search(data, query)
        print_results(results, query)
        if results:
            pick = input(f"{DIM}Open result #, or enter to search again: {RESET}").strip()
            if pick.isdigit() and 1 <= int(pick) <= len(results):
                detail_menu(data, results[int(pick) - 1], path)
        print()


# ---------- dedupe ----------

def dedupe_data(data):
    seen = {}
    result = []
    removed = 0
    for item in data:
        key = (item["tool"].strip().lower(), item["command"].strip().lower())
        if key in seen:
            existing = seen[key]
            merged_keywords = list(existing.get("keywords", []))
            for kw in item.get("keywords", []):
                if kw not in merged_keywords:
                    merged_keywords.append(kw)
            existing["keywords"] = merged_keywords
            removed += 1
            continue
        seen[key] = item
        result.append(item)
    return result, removed


def main():
    settings = init_theme()
    path = data_path()
    data = load_data(path)

    args = sys.argv[1:]
    if args and args[0] == "--import" and len(args) > 1:
        import_from_file(data, args[1])
        save_data(path, data)
        offer_git_sync(path)
        return
    if args and args[0] == "--add":
        add_entry(data)
        save_data(path, data)
        offer_git_sync(path)
        return
    if args and args[0] == "--dedupe":
        deduped, removed = dedupe_data(data)
        save_data(path, deduped)
        print(f"{GREEN}Removed {removed} duplicate entr{'y' if removed == 1 else 'ies'}. {len(deduped)} entries remain.{RESET}")
        offer_git_sync(path)
        return
    if not args:
        interactive(data, path, settings)
        return

    query = " ".join(args)
    results = search(data, query)
    print_results(results, query)


if __name__ == "__main__":
    main()
