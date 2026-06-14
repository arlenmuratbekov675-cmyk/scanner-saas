"""
Call Tracker - Track cold calls and follow-ups.
"""
import json
import os
from datetime import datetime, timedelta

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "leads")
TRACKER_FILE = os.path.join(OUTPUT_DIR, "call_tracker.json")


def load_tracker() -> list:
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    return []


def save_tracker(data: list):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def log_call(
    clinic_name: str,
    phone: str,
    result: str,
    notes: str = "",
    follow_up_date: str = ""
):
    """Log a call result."""
    tracker = load_tracker()
    
    call = {
        "id": len(tracker) + 1,
        "clinic_name": clinic_name,
        "phone": phone,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "result": result,  # interested, not_interested, voicemail, no_answer, callback
        "notes": notes,
        "follow_up_date": follow_up_date,
        "follow_up_done": False,
        "demo_booked": False,
        "deal_closed": False
    }
    
    tracker.append(call)
    save_tracker(tracker)
    print(f"Logged: {clinic_name} - {result}")
    return call


def get_today_calls() -> list:
    """Get all calls made today."""
    tracker = load_tracker()
    today = datetime.now().strftime("%Y-%m-%d")
    return [c for c in tracker if c["date"] == today]


def get_follow_ups() -> list:
    """Get calls that need follow-up."""
    tracker = load_tracker()
    today = datetime.now().strftime("%Y-%m-%d")
    
    follow_ups = []
    for call in tracker:
        if call["follow_up_date"] and call["follow_up_date"] <= today and not call["follow_up_done"]:
            follow_ups.append(call)
    
    return follow_ups


def show_stats():
    """Show call statistics."""
    tracker = load_tracker()
    
    if not tracker:
        print("No calls logged yet.")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_calls = [c for c in tracker if c["date"] == today]
    
    total = len(tracker)
    today_count = len(today_calls)
    
    results = {}
    for call in tracker:
        r = call["result"]
        results[r] = results.get(r, 0) + 1
    
    demos = len([c for c in tracker if c["demo_booked"]])
    closed = len([c for c in tracker if c["deal_closed"]])
    
    print("\n=== Call Stats ===")
    print(f"Total calls: {total}")
    print(f"Today: {today_count}")
    print(f"\nBy result:")
    for r, count in results.items():
        print(f"  {r}: {count}")
    print(f"\nDemos booked: {demos}")
    print(f"Deals closed: {closed}")


def show_follow_ups():
    """Show pending follow-ups."""
    follow_ups = get_follow_ups()
    
    if not follow_ups:
        print("No follow-ups due today.")
        return
    
    print(f"\n=== Follow-ups Due ({len(follow_ups)}) ===\n")
    for call in follow_ups:
        print(f"{call['clinic_name']}")
        print(f"  Phone: {call['phone']}")
        print(f"  Last result: {call['result']}")
        print(f"  Notes: {call['notes']}")
        print()


def show_today():
    """Show today's calls."""
    calls = get_today_calls()
    
    if not calls:
        print("No calls today yet.")
        return
    
    print(f"\n=== Today's Calls ({len(calls)}) ===\n")
    for call in calls:
        print(f"{call['time']} - {call['clinic_name']}: {call['result']}")
        if call['notes']:
            print(f"  Notes: {call['notes']}")
    print()


def mark_follow_up_done(clinic_name: str):
    """Mark a follow-up as done."""
    tracker = load_tracker()
    today = datetime.now().strftime("%Y-%m-%d")
    
    for call in tracker:
        if call["clinic_name"] == clinic_name and call["follow_up_date"] <= today:
            call["follow_up_done"] = True
            print(f"Marked {clinic_name} follow-up as done")
            break
    
    save_tracker(tracker)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            show_stats()
        elif sys.argv[1] == "today":
            show_today()
        elif sys.argv[1] == "followups":
            show_follow_ups()
        elif sys.argv[1] == "done" and len(sys.argv) > 2:
            mark_follow_up_done(" ".join(sys.argv[2:]))
        else:
            print("Usage:")
            print("  python call_tracker.py stats      - Show statistics")
            print("  python call_tracker.py today      - Show today's calls")
            print("  python call_tracker.py followups  - Show pending follow-ups")
            print("  python call_tracker.py done <name> - Mark follow-up done")
    else:
        print("Call Tracker")
        print("=" * 40)
        print("\nQuick log:")
        print('  python -c "from call_tracker import log_call; log_call(\'Smile Dental\', \'555-0123\', \'interested\', \'wants demo\', \'2026-06-15\')"')
