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
except ImportError:
    print("prompt_toolkit not installed. Run: pip install prompt_toolkit --break-system-packages")
    sys.exit(1)

BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


# ---------- data path ----------

def data_path():
    if os.environ.get("CHEAT_DATA"):
        return os.environ["CHEAT_DATA"]
    home_path = os.path.expanduser("~/.cheatsheet/data.json")
    if os.path.exists(home_path):
        return home_path
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


def load_data(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(path, data):
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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


# ---------- add / edit / delete ----------

def ask(label, default=""):
    suffix = f" [{default}]" if default else ""
    val = input(f"{label}{suffix}: ").strip()
    return val if val else default


def add_entry(data):
    print(f"\n{BOLD}Add new entry{RESET}")
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
    print(f"\n{BOLD}Edit entry{RESET} ({DIM}press enter to keep current value{RESET})")
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
    print(f"\n{CYAN}[{entry['tool']}]{RESET} {BOLD}{entry['command']}{RESET}")
    if entry.get("desc"):
        print(f"  {DIM}{entry['desc']}{RESET}")
    if entry.get("keywords"):
        print(f"  {DIM}keywords: {', '.join(entry['keywords'])}{RESET}")


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
        print(f"{DIM}No matching command found.{RESET}")
        return
    for i, item in enumerate(results, 1):
        print(f"{YELLOW}{i}.{RESET} {CYAN}[{item['tool']}]{RESET} {item['command']}")
        kw = matched_keyword_for(item, query)
        if kw:
            print(f"   {DIM}matched \"{kw}\"  -  {item.get('desc','')}{RESET}")
        else:
            print(f"   {DIM}{item.get('desc','')}{RESET}")


def detail_menu(data, entry, path):
    while True:
        print_entry(entry)
        print(f"{DIM}[e] edit  [d] delete  [b] back{RESET}")
        choice = input(f"{YELLOW}> {RESET}").strip().lower()
        if choice == "e":
            edit_entry(entry)
            save_data(path, data)
            offer_git_sync(path)
        elif choice == "d":
            if delete_entry(data, entry):
                save_data(path, data)
                offer_git_sync(path)
            return
        elif choice == "b" or choice == "":
            return


def interactive(data, path):
    print(f"{DIM}Type to search (suggestions appear as you type). Tab/Enter to pick a suggestion.{RESET}")
    print(f"{DIM}Commands: type a query and press enter | :add | :import <file> | :quit{RESET}\n")

    while True:
        completer = build_completer(data)
        try:
            query = prompt(
                "cheat> ",
                completer=completer,
                complete_while_typing=True,
                complete_style=CompleteStyle.COLUMN,
            ).strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not query:
            continue
        if query in (":quit", ":q"):
            break
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
            pick = input(f"{DIM}Open a result number, or press enter to search again: {RESET}").strip()
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
        interactive(data, path)
        return

    query = " ".join(args)
    results = search(data, query)
    print_results(results, query)


if __name__ == "__main__":
    main()
