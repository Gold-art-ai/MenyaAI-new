import sys
from pathlib import Path

# Add buddy_service to system path
PROJECT_ROOT = Path(__file__).resolve().parent
BUDDY_SERVICE_DIR = PROJECT_ROOT / "src" / "buddy_service"
if str(BUDDY_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(BUDDY_SERVICE_DIR))

from buddy_ai import BuddyAI

print("Testing BuddyAI...")
buddy = BuddyAI()

# Test with simple data
print("Calling give_praise...")
buddy.give_praise(
    student_name="Gloria",
    precision=0.94,
    current_act="Letters",
    next_task="Numbers",
    language_preference="EN",
    jerk_index=3.0,
    session_minutes=15,
    next_moment="Learning game",
    next_moment_note="Play a quick game before moving into Numbers."
)

print("Done!")
