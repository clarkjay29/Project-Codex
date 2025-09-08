#!/usr/bin/env python3
"""
Series Codex - A command-line Series management tool
Run with Pydroid 3 or any Python 3 environment.

Saves data to 'series_codex_data.json' in the same directory.
"""

import json
import os
import textwrap
from datetime import datetime
from typing import Dict, List, Optional

DATA_FILE = "series_codex_data.json"
WRAP = 80


# ---------------------------
# Utilities
# ---------------------------
def pretty(text: str, indent: int = 0):
    print(textwrap.fill(text, WRAP, initial_indent=" " * indent, subsequent_indent=" " * indent))


def input_prompt(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        # default structure
        data = {
            "meta": {"created_at": datetime.utcnow().isoformat()},
            "series": None,
            "books": [],
            "master": {"characters": [], "locations": [], "lore": []},
            "timeline": []  # entries: {when, book_id(optional), desc}
        }
        save_data(data)
        return data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def choose_from_list(items: List[str], prompt: str = "Choose: ") -> Optional[int]:
    if not items:
        print("  (none)")
        return None
    for i, it in enumerate(items, 1):
        print(f"  [{i}] {it}")
    s = input_prompt(prompt).strip()
    if not s:
        return None
    try:
        idx = int(s) - 1
        if 0 <= idx < len(items):
            return idx
    except ValueError:
        return None
    return None


# ---------------------------
# Personality & Analysis helpers
# ---------------------------
def analyze_personality_text(personality_text: str) -> str:
    """Simple heuristic personality analyzer (expandable)."""
    t = personality_text.lower()
    traits = []
    if "conscientious" in t or "conscientiousness" in t or "organized" in t:
        traits.append("High conscientiousness — likely reliable, structured, and plan-driven.")
    if "agreeable" in t or "kind" in t or "friendly" in t:
        traits.append("High agreeableness — likely cooperative and empathetic.")
    if "low agree" in t or "not agreeable" in t or "blunt" in t:
        traits.append("Low agreeableness — may be blunt or confrontational.")
    if "open" in t or "curious" in t or "creative" in t:
        traits.append("High openness — imaginative and curious; likely to pursue novel choices.")
    if "neurotic" in t or "anxious" in t or "sensitive" in t:
        traits.append("Emotional sensitivity — may react strongly under stress.")
    if "extro" in t or "outgoing" in t or "social" in t:
        traits.append("Outgoing — gains energy from others, socially proactive.")
    if "intro" in t or "quiet" in t or "reserved" in t:
        traits.append("Reserved — internal processing, may prefer solitude or a small circle.")
    if not traits:
        return "No strong signals detected from input; personality summary unavailable."
    return " ".join(traits)


# ---------------------------
# Core App Functions
# ---------------------------
def show_welcome():
    print("=" * 80)
    print("SERIES CODEX — Your multi-book series manager (CLI)")
    print("I am Series Codex. Type the number of a menu option to proceed.")
    print("=" * 80)


def main_menu() -> None:
    print("\nMain Menu")
    print("[1] Series Overview")
    print("[2] Manage Books")
    print("[3] Master Codex")
    print("[4] Master Timeline")
    print("[5] Series Analysis")
    print("[6] The Oracle's Advice")
    print("[7] Save & Exit")


# ---------------------------
# Module: Series Overview
# ---------------------------
def edit_series_overview(data: dict):
    print("\n--- Series Overview ---")
    current = data.get("series")
    if current:
        print("Current series info:")
        pretty(json.dumps(current, indent=2), indent=2)
    else:
        print("No series defined yet.")

    print("\nOptions:")
    print("[1] Create / Edit Series")
    print("[2] Back to Main Menu")
    choice = input_prompt("> ").strip()
    if choice == "1":
        # gather series-level info
        title = input_prompt("Series Title: ").strip()
        genre = input_prompt("Overall Genre: ").strip()
        logline = input_prompt("Series Logline (one sentence): ").strip()
        num_books = input_prompt("Planned number of books (or leave blank): ").strip()
        num_books = int(num_books) if num_books.isdigit() else None
        inter = input_prompt(
            "Interconnection Style (e.g., 'Standalone novels with shared world', 'Sequential saga'): "
        ).strip()
        protagonist_arc = input_prompt("Protagonist's Overall Arc (1-2 sentences): ").strip()
        data["series"] = {
            "title": title,
            "genre": genre,
            "logline": logline,
            "planned_books": num_books,
            "interconnection_style": inter,
            "protagonist_overall_arc": protagonist_arc,
            "updated_at": datetime.utcnow().isoformat(),
        }
        save_data(data)
        print("\n[Reactive Comment] Series overview saved. Great — you just created the spine for your saga.")
    else:
        return

# ---------------------------
# Module: Manage Books
# ---------------------------
def create_book(data: dict):
    print("\n--- Create New Book ---")
    title = input_prompt("Book Title: ").strip()
    number = input_prompt("Book Number (1-based, optional): ").strip()
    number = int(number) if number.isdigit() else None
    brief = input_prompt("Short description / logline: ").strip()
    planned_length = input_prompt("Estimated word count (optional): ").strip()
    planned_length = int(planned_length) if planned_length.isdigit() else None
    book = {
        "id": f"book_{len(data['books']) + 1}_{int(datetime.utcnow().timestamp())}",
        "title": title,
        "number": number,
        "logline": brief,
        "planned_length": planned_length,
        "plot_outline": [],
        "characters": [],  # list of character IDs (master)
        "book_char_profiles": {},  # book-specific profiles per character id
        "timeline": [],  # events local to the book
        "themes": [],
        "created_at": datetime.utcnow().isoformat(),
    }
    data["books"].append(book)
    save_data(data)
    print("\n[Reactive Comment] Book created. Think about the inciting incident next.")


def select_book_index(data: dict) -> Optional[int]:
    if not data["books"]:
        print("\nNo books created yet.")
        return None
    names = [f"{b.get('title') or '<untitled>'} (num:{b.get('number')})" for b in data["books"]]
    idx = choose_from_list(names, "Select a book number (or press Enter to cancel): ")
    return idx


def manage_book(data: dict):
    print("\n--- Manage Books ---")
    print("[A] Create New Book")
    print("[B] Select Existing Book")
    print("[C] Back")
    choice = input_prompt("> ").strip().lower()
    if choice == "a":
        create_book(data)
        return
    elif choice == "b":
        idx = select_book_index(data)
        if idx is None:
            return
        book = data["books"][idx]
        book_submenu(data, book)
    else:
        return


def book_submenu(data: dict, book: dict):
    while True:
        print(f"\n--- Book: {book.get('title')} ---")
        print("[a] Book Plot Outline")
        print("[b] Book Characters")
        print("[c] Book Timeline")
        print("[d] Book-Specific Analysis")
        print("[e] Edit Basic Info")
        print("[f] Back")
        ch = input_prompt("> ").strip().lower()
        if ch == "a":
            manage_book_plot(data, book)
        elif ch == "b":
            manage_book_characters(data, book)
        elif ch == "c":
            manage_book_timeline(data, book)
        elif ch == "d":
            book_specific_analysis(data, book)
        elif ch == "e":
            edit_book_basic_info(data, book)
        elif ch == "f":
            save_data(data)
            break
        else:
            print("Unknown option.")

def manage_book_plot(data: dict, book: dict):
    print("\nBook Plot Outline (major beats).")
    if book["plot_outline"]:
        for i, beat in enumerate(book["plot_outline"], 1):
            print(f"[{i}] {beat}")
    print("[1] Add Beat")
    print("[2] Remove Beat")
    print("[3] Back")
    c = input_prompt("> ").strip()
    if c == "1":
        beat = input_prompt("Describe the plot beat (short): ")
        book["plot_outline"].append(beat)
        save_data(data)
        print("[Reactive Comment] Added plot beat. Nice — what's the emotional core here?")
    elif c == "2":
        i = choose_from_list(book["plot_outline"], "Select beat to remove: ")
        if i is not None:
            removed = book["plot_outline"].pop(i)
            save_data(data)
            print(f"Removed: {removed}")
    else:
        return


def edit_book_basic_info(data: dict, book: dict):
    print("\nCurrent basic info:")
    pretty(json.dumps({"title": book["title"], "number": book["number"], "logline": book["logline"]}, indent=2), indent=2)
    book["title"] = input_prompt(f"Title [{book['title']}]: ") or book["title"]
    num = input_prompt(f"Number [{book['number']}]: ")
    book["number"] = int(num) if num.isdigit() else book["number"]
    book["logline"] = input_prompt(f"Logline [{book['logline']}]: ") or book["logline"]
    save_data(data)
    print("[Reactive Comment] Book basic info updated.")


# ---------------------------
# Module: Book Characters
# ---------------------------
def manage_book_characters(data: dict, book: dict):
    while True:
        print("\nBook Characters Menu")
        print("[1] List book characters")
        print("[2] Add master character to this book")
        print("[3] Create new master character and add it")
        print("[4] Edit book-specific character profile")
        print("[5] Remove character from book")
        print("[6] Back")
        ch = input_prompt("> ").strip()
        if ch == "1":
            if not book["characters"]:
                print("No characters assigned to this book.")
            else:
                for cid in book["characters"]:
                    m = find_master_character(data, cid)
                    if m:
                        print(f"- {m['name']} (id:{m['id']})")
        elif ch == "2":
            idx = choose_from_list([c["name"] for c in data["master"]["characters"]], "Choose master character to add: ")
            if idx is not None:
                cid = data["master"]["characters"][idx]["id"]
                if cid not in book["characters"]:
                    book["characters"].append(cid)
                    # initialize book-specific profile
                    book["book_char_profiles"].setdefault(cid, {"role_in_book": "", "notes": ""})
                    save_data(data)
                    print("[Reactive Comment] Character added to book.")
                else:
                    print("Character already in book.")
        elif ch == "3":
            create_master_character(data)
            save_data(data)
        elif ch == "4":
            if not book["characters"]:
                print("No characters to edit.")
                continue
            names = []
            for cid in book["characters"]:
                m = find_master_character(data, cid)
                names.append(m["name"] if m else f"(missing:{cid})")
            sel = choose_from_list(names, "Select character to edit: ")
            if sel is None:
                continue
            cid = book["characters"][sel]
            profile = book["book_char_profiles"].get(cid, {"role_in_book": "", "notes": ""})
            print("Edit book-specific profile (leave blank to keep):")
            profile["role_in_book"] = input_prompt(f"Role in this book [{profile.get('role_in_book','')}]: ") or profile.get("role_in_book", "")
            profile["notes"] = input_prompt(f"Notes [{profile.get('notes','')}]: ") or profile.get("notes", "")
            book["book_char_profiles"][cid] = profile
            save_data(data)
            print("[Reactive Comment] Book-specific character profile updated.")
        elif ch == "5":
            if not book["characters"]:
                print("No characters to remove.")
                continue
            names = []
            for cid in book["characters"]:
                m = find_master_character(data, cid)
                names.append(m["name"] if m else f"(missing:{cid})")
            sel = choose_from_list(names, "Select character to remove: ")
            if sel is None:
                continue
            cid = book["characters"].pop(sel)
            book["book_char_profiles"].pop(cid, None)
            save_data(data)
            print("[Reactive Comment] Character removed from book.")
        elif ch == "6":
            break
        else:
            print("Unknown option.")


# ---------------------------
# Module: Master Codex (Characters / Locations / Lore)
# ---------------------------
def view_master_codex(data: dict):
    while True:
        print("\n--- Master Codex ---")
        print("[A] Characters")
        print("[B] Locations")
        print("[C] Lore/Magic System")
        print("[D] Back")
        ch = input_prompt("> ").strip().lower()
        if ch == "a":
            manage_master_characters(data)
        elif ch == "b":
            manage_master_locations(data)
        elif ch == "c":
            manage_master_lore(data)
        elif ch == "d":
            break
        else:
            print("Unknown option.")


def create_master_character(data: dict):
    print("\n--- Create Master Character ---")
    name = input_prompt("Character Name: ").strip()
    role = input_prompt("Role in series (short): ").strip()
    personality = input_prompt("Personality summary (keywords or short sentence): ").strip()
    series_arc = input_prompt("Series-wide arc (summary of character growth across books): ").strip()
    notes = input_prompt("Additional notes (optional): ").strip()
    cid = f"char_{len(data['master']['characters']) + 1}_{int(datetime.utcnow().timestamp())}"
    character = {
        "id": cid,
        "name": name,
        "role": role,
        "personality": personality,
        "personality_analysis": analyze_personality_text(personality),
        "series_arc": series_arc,
        "notes": notes,
        "created_at": datetime.utcnow().isoformat(),
    }
    data["master"]["characters"].append(character)
    save_data(data)
    print(f"[Reactive Comment] Master character '{name}' created and saved.")


def find_master_character(data: dict, cid: str) -> Optional[dict]:
    for c in data["master"]["characters"]:
        if c["id"] == cid:
            return c
    return None
    
    
def manage_master_characters(data: dict):
    while True:
        print("\nMaster Characters")
        print("[1] List characters")
        print("[2] Create character")
        print("[3] Edit character")
        print("[4] Delete character")
        print("[5] Back")
        ch = input_prompt("> ").strip()
        if ch == "1":
            if not data["master"]["characters"]:
                print("No characters yet.")
            else:
                for c in data["master"]["characters"]:
                    print(f"- {c['name']} (id:{c['id']}) - {c['role']}")
        elif ch == "2":
            create_master_character(data)
        elif ch == "3":
            names = [f"{c['name']} ({c['role']})" for c in data["master"]["characters"]]
            idx = choose_from_list(names, "Select character to edit: ")
            if idx is None:
                continue
            char = data["master"]["characters"][idx]
            char["name"] = input_prompt(f"Name [{char['name']}]: ") or char["name"]
            char["role"] = input_prompt(f"Role [{char['role']}]: ") or char["role"]
            char["personality"] = input_prompt(f"Personality [{char['personality']}]: ") or char["personality"]
            char["personality_analysis"] = analyze_personality_text(char["personality"])
            char["series_arc"] = input_prompt(f"Series Arc [{char.get('series_arc','')}]: ") or char.get("series_arc","")
            char["notes"] = input_prompt(f"Notes [{char.get('notes','')}]: ") or char.get("notes","")
            save_data(data)
            print("[Reactive Comment] Master character updated. I will reflect changes across book references when possible.")
        elif ch == "4":
            names = [f"{c['name']} ({c['role']})" for c in data["master"]["characters"]]
            idx = choose_from_list(names, "Select character to delete: ")
            if idx is None:
                continue
            c = data["master"]["characters"].pop(idx)
            # remove references in books
            for b in data["books"]:
                if c["id"] in b["characters"]:
                    b["characters"].remove(c["id"])
                    b["book_char_profiles"].pop(c["id"], None)
            save_data(data)
            print(f"Deleted {c['name']} and removed references from books.")
        elif ch == "5":
            break
        else:
            print("Unknown option.")


def manage_master_locations(data: dict):
    while True:
        print("\nMaster Locations")
        print("[1] List locations")
        print("[2] Create location")
        print("[3] Edit location")
        print("[4] Delete location")
        print("[5] Back")
        ch = input_prompt("> ").strip()
        if ch == "1":
            if not data["master"]["locations"]:
                print("No locations yet.")
            else:
                for loc in data["master"]["locations"]:
                    print(f"- {loc['name']} (id:{loc['id']}) - {loc.get('brief','')}")
        elif ch == "2":
            name = input_prompt("Location name: ").strip()
            brief = input_prompt("Brief description: ").strip()
            evolution = input_prompt("How it changes across the series (short): ").strip()
            lid = f"loc_{len(data['master']['locations']) + 1}_{int(datetime.utcnow().timestamp())}"
            data["master"]["locations"].append({
                "id": lid,
                "name": name,
                "brief": brief,
                "evolution": evolution,
                "created_at": datetime.utcnow().isoformat(),
            })
            save_data(data)
            print("[Reactive Comment] Location added.")
        elif ch == "3":
            names = [f"{l['name']}" for l in data["master"]["locations"]]
            idx = choose_from_list(names, "Select location to edit: ")
            if idx is None:
                continue
            loc = data["master"]["locations"][idx]
            loc["name"] = input_prompt(f"Name [{loc['name']}]: ") or loc["name"]
            loc["brief"] = input_prompt(f"Brief [{loc.get('brief','')}]: ") or loc.get("brief","")
            loc["evolution"] = input_prompt(f"Evolution [{loc.get('evolution','')}]: ") or loc.get("evolution","")
            save_data(data)
            print("[Reactive Comment] Location updated.")
        elif ch == "4":
            names = [f"{l['name']}" for l in data["master"]["locations"]]
            idx = choose_from_list(names, "Select location to delete: ")
            if idx is None:
                continue
            removed = data["master"]["locations"].pop(idx)
            save_data(data)
            print(f"Deleted {removed['name']}.")
        elif ch == "5":
            break
        else:
            print("Unknown option.")


def manage_master_lore(data: dict):
    while True:
        print("\nLore / Magic System")
        print("[1] List lore entries")
        print("[2] Add lore entry")
        print("[3] Edit entry")
        print("[4] Delete entry")
        print("[5] Back")
        ch = input_prompt("> ").strip()
        if ch == "1":
            if not data["master"]["lore"]:
                print("No lore entries yet.")
            else:
                for l in data["master"]["lore"]:
                    print(f"- {l['title']} (id:{l['id']})")
                    pretty(l.get("summary",""), indent=4)
        elif ch == "2":
            title = input_prompt("Title (rule or piece of lore): ").strip()
            summary = input_prompt("Summary / rules: ").strip()
            lid = f"lore_{len(data['master']['lore']) + 1}_{int(datetime.utcnow().timestamp())}"
            data["master"]["lore"].append({"id": lid, "title": title, "summary": summary, "created_at": datetime.utcnow().isoformat()})
            save_data(data)
            print("[Reactive Comment] Lore entry added.")
        elif ch == "3":
            names = [f"{l['title']}" for l in data["master"]["lore"]]
            idx = choose_from_list(names, "Select lore entry to edit: ")
            if idx is None:
                continue
            l = data["master"]["lore"][idx]
            l["title"] = input_prompt(f"Title [{l['title']}]: ") or l["title"]
            l["summary"] = input_prompt(f"Summary [{l.get('summary','')}]: ") or l.get("summary","")
            save_data(data)
            print("[Reactive Comment] Lore updated.")
        elif ch == "4":
            names = [f"{l['title']}" for l in data["master"]["lore"]]
            idx = choose_from_list(names, "Select lore to delete: ")
            if idx is None:
                continue
            removed = data["master"]["lore"].pop(idx)
            save_data(data)
            print(f"Deleted {removed['title']}.")
        elif ch == "5":
            break
        else:
            print("Unknown option.")
            
            
            # ---------------------------
# Module: Book Timeline
# ---------------------------
def manage_book_timeline(data: dict, book: dict):
    print(f"\nTimeline for Book: {book['title']}")
    if book["timeline"]:
        for i, ev in enumerate(book["timeline"], 1):
            print(f"[{i}] {ev['when']}: {ev['desc']}")
    print("[1] Add event")
    print("[2] Remove event")
    print("[3] Back")
    c = input_prompt("> ").strip()
    if c == "1":
        when = input_prompt("When (e.g., Day 1 / Year / precise date): ").strip()
        desc = input_prompt("Event description: ").strip()
        book["timeline"].append({"when": when, "desc": desc})
        save_data(data)
        print("[Reactive Comment] Timeline event added.")
    elif c == "2":
        if not book["timeline"]:
            print("No events.")
            return
        idx = choose_from_list([f"{e['when']}: {e['desc']}" for e in book["timeline"]], "Select event to remove: ")
        if idx is not None:
            book["timeline"].pop(idx)
            save_data(data)
            print("Event removed.")
    else:
        return


# ---------------------------
# Module: Master Timeline
# ---------------------------
def manage_master_timeline(data: dict):
    while True:
        print("\n--- Master Timeline ---")
        if data["timeline"]:
            for i, ev in enumerate(data["timeline"], 1):
                print(f"[{i}] {ev.get('when')} - {ev.get('desc')} (book_id: {ev.get('book_id')})")
        else:
            print("(No master timeline events yet)")
        print("[1] Add timeline event")
        print("[2] Edit event")
        print("[3] Remove event")
        print("[4] Back")
        ch = input_prompt("> ").strip()
        if ch == "1":
            when = input_prompt("When (absolute or relative): ").strip()
            desc = input_prompt("Description: ").strip()
            book_id = input_prompt("Related book id (optional): ").strip() or None
            data["timeline"].append({"when": when, "desc": desc, "book_id": book_id})
            save_data(data)
            print("[Reactive Comment] Master timeline updated.")
        elif ch == "2":
            if not data["timeline"]:
                continue
            idx = choose_from_list([f"{e['when']} - {e['desc']}" for e in data["timeline"]], "Select event to edit: ")
            if idx is None:
                continue
            e = data["timeline"][idx]
            e["when"] = input_prompt(f"When [{e['when']}]: ") or e["when"]
            e["desc"] = input_prompt(f"Desc [{e['desc']}]: ") or e["desc"]
            e["book_id"] = input_prompt(f"Book ID [{e.get('book_id', '')}]: ") or e.get("book_id")
            save_data(data)
            print("[Reactive Comment] Master timeline event updated.")
        elif ch == "3":
            idx = choose_from_list([f"{e['when']} - {e['desc']}" for e in data["timeline"]], "Select event to remove: ")
            if idx is None:
                continue
            removed = data["timeline"].pop(idx)
            save_data(data)
            print(f"Removed timeline event: {removed['desc']}")
        elif ch == "4":
            break
        else:
            print("Unknown option.")


# ---------------------------
# Module: Series Analysis
# ---------------------------
def continuity_check(data: dict):
    """
    Very basic continuity checks:
    - Characters referenced in books but missing in master codex
    - Conflicting basic attributes (example: different roles) — minimal heuristic
    """
    print("\n--- Continuity Check ---")
    issues = []
    # check character references
    master_ids = {c["id"]: c for c in data["master"]["characters"]}
    for b in data["books"]:
        for cid in b["characters"]:
            if cid not in master_ids:
                issues.append(f"Book '{b['title']}' references missing master character id {cid}")
    # rudimentary conflict: same name but different id
    name_to_ids = {}
    for c in data["master"]["characters"]:
        name_to_ids.setdefault(c["name"].lower(), []).append(c["id"])
    for name, ids in name_to_ids.items():
        if len(ids) > 1:
            issues.append(f"Multiple master characters share name '{name}' with ids {ids} — possible duplication.")
    if issues:
        print("Potential continuity issues found:")
        for it in issues:
            print(f"- {it}")
    else:
        print("No obvious continuity issues found. (This is a lightweight scan.)")


def character_arc_report(data: dict):
    print("\n--- Character Arc Report ---")
    names = [c["name"] for c in data["master"]["characters"]]
    idx = choose_from_list(names, "Select character for arc report: ")
    if idx is None:
        return
    c = data["master"]["characters"][idx]
    print(f"\nCharacter: {c['name']}")
    print(f"Master role: {c.get('role')}")
    print(f"Series arc: {c.get('series_arc')}")
    print(f"Personality analysis: {c.get('personality_analysis')}")
    # show appearances across books
    appearances = []
    for b in data["books"]:
        if c["id"] in b["characters"]:
            prof = b["book_char_profiles"].get(c["id"], {})
            appearances.append({"book": b["title"], "role_in_book": prof.get("role_in_book", ""), "notes": prof.get("notes", "")})
    if not appearances:
        print("(Character not assigned to any book yet.)")
    else:
        print("Appearances by book:")
        for a in appearances:
            print(f"- {a['book']}: role: {a['role_in_book']}; notes: {a['notes']}")


def thematic_cohesion(data: dict):
    print("\n--- Thematic Cohesion Analysis ---")
    # collect themes from books
    theme_counts = {}
    for b in data["books"]:
        for t in b.get("themes", []):
            theme_counts[t.lower()] = theme_counts.get(t.lower(), 0) + 1
    if not theme_counts:
        print("No themes recorded across books. Consider tagging themes for each book.")
        return
    print("Themes and coverage across books:")
    for t, cnt in theme_counts.items():
        print(f"- {t}: appears in {cnt} book(s)")
    # suggest under/over-represented
    total_books = max(1, len(data["books"]))
    missing = [t for t, cnt in theme_counts.items() if cnt < total_books / 2]
    if missing:
        print("\nObservations:")
        pretty("Some themes are not strong across the series; consider reinforcing themes that define your series identity.", indent=2)
    else:
        print("\nObservations: Themes appear consistently across books (as far as recorded).")


def series_analysis_menu(data: dict):
    while True:
        print("\n--- Series Analysis ---")
        print("[1] Continuity Check")
        print("[2] Character Arc Report")
        print("[3] Thematic Cohesion")
        print("[4] Back")
        ch = input_prompt("> ").strip()
        if ch == "1":
            continuity_check(data)
        elif ch == "2":
            character_arc_report(data)
        elif ch == "3":
            thematic_cohesion(data)
        elif ch == "4":
            break
        else:
            print("Unknown option.")
            
            
            # ---------------------------
# Module: Oracle's Advice
# ---------------------------
def oracles_advice(data: dict):
    print("\n--- The Oracle's Advice ---")
    print("Type a focused query like:")
    print("  - 'What conflicts could arise between [Character A] and [Character B]?'")
    print("  - 'How can I escalate stakes in Book 2?'")
    print("Or type 'examples' to see quick prompts.")
    q = input_prompt("> ").strip()
    if not q:
        print("No query entered.")
        return
    qlower = q.lower()
    # simple heuristics based on keywords and existing data
    if "conflict" in qlower and "between" in qlower:
        # try to extract character names
        words = q.replace("?", "").split()
        # naive: find master character names that appear in the question
        char_names = [c["name"] for c in data["master"]["characters"]]
        mentioned = [name for name in char_names if name.lower() in qlower]
        if len(mentioned) >= 2:
            a, b = mentioned[0], mentioned[1]
            print(f"\nPossible conflicts between {a} and {b}:")
            pretty(f"1) Clashing motivations: {a} wants X while {b} needs Y, forcing them to collide.", indent=2)
            pretty("2) Past secret revealed: one holds a secret that undermines trust.", indent=2)
            pretty("3) Resource/goal competition: both pursue the same scarce resource or position.", indent=2)
            pretty("Consider aligning conflict to your series themes for stronger cohesion.", indent=2)
        else:
            print("I couldn't identify two character names from the master codex in your query. Try writing both character names exactly as they are in Master Characters.")
    elif "escalate" in qlower or "escalation" in qlower or "stakes" in qlower:
        print("\nWays to escalate stakes:")
        pretty("- Personal stakes: threaten what the protagonist values most (relationships, reputation, self-image).", indent=2)
        pretty("- Societal stakes: push the world toward a tipping point (war, famine, collapse).", indent=2)
        pretty("- Moral stakes: force character to choose between two bad options, revealing values.", indent=2)
        pretty("- Reveal a costly secret that changes goals and alliances.", indent=2)
    else:
        print("\nGeneral advice:")
        pretty("Use contrasts: pair proactive characters with reactive ones. Use consequences: each choice should change the world irreversibly. If unsure, describe a scene and I can offer targeted edits.", indent=2)


# ---------------------------
# Book-specific analysis (example)
# ---------------------------
def book_specific_analysis(data: dict, book: dict):
    print(f"\n--- Book Analysis: {book['title']} ---")
    # quick checks
    issues = []
    if not book["plot_outline"]:
        issues.append("No plot outline recorded.")
    if not book["characters"]:
        issues.append("No characters assigned to this book.")
    if issues:
        print("Observations:")
        for it in issues:
            print(f"- {it}")
    else:
        print("This book has a skeleton outline and characters. Quick suggestions:")
        print("- Ensure each major plot beat affects at least one character's arc.")
        print("- Check that book-specific timeline events align with series timeline (Master Timeline).")


# ---------------------------
# Main app loop
# ---------------------------
def run_cli():
    data = load_data()
    show_welcome()
    while True:
        main_menu()
        choice = input_prompt("> ").strip()
        if choice == "1":
            edit_series_overview(data)
        elif choice == "2":
            manage_book(data)
        elif choice == "3":
            view_master_codex(data)
        elif choice == "4":
            manage_master_timeline(data)
        elif choice == "5":
            series_analysis_menu(data)
        elif choice == "6":
            oracles_advice(data)
        elif choice == "7":
            save_data(data)
            print("Data saved. Goodbye — keep writing.")
            break
        else:
            print("Unknown option. Please choose 1-7.")


if __name__ == "__main__":
    run_cli()