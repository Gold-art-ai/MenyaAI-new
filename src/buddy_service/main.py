import asyncio
import time
from buddy_ai import BuddyAI

def run_interactive_mode():
    """Simple interactive testing loop for BuddyAI"""
    print("\n" + "="*40)
    print("          BUDDY AI - INTERACTIVE MODE")
    print("="*40)
    
    buddy = BuddyAI()
    
    # Default test values
    student_name = input("\nEnter student name [Amaury]: ").strip() or "Amaury"
    language = input("Language preference (RW-EN / RW / FR / EN) [RW-EN]: ").strip().upper() or "RW-EN"
    
    print(f"\nBuddy is ready to help {student_name}!\n")
    
    activities = ["Lines", "Shapes", "Letters", "Numbers", "Words", "MathBasics", "ReadSimple"]
    current_idx = 0

    while True:
        current_act = activities[current_idx]
        next_idx = (current_idx + 1) % len(activities)
        next_task = activities[next_idx]
        
        print(f"\n--- {student_name} is practicing: {current_act} ---")
        
        # How well did the child draw?
        print("How close was the child's drawing?")
        print("1. Great try (Excellent precision)")
        print("2. Good try (Moderate precision)")
        print("3. Needs more practice (Low precision)")
        precision_choice = input("Choose one [2]: ").strip() or "2"
        precision = 0.94 if precision_choice == "1" else (0.80 if precision_choice == "2" else 0.55)
        
        # How steady was the hand?
        print("\nHow steady was the child's hand?")
        print("1. Calm and steady")
        print("2. A little shaky")
        print("3. Needs slow gentle guidance")
        hand_choice = input("Choose one [1]: ").strip() or "1"
        jerk_index = 2.0 if hand_choice == "1" else (5.5 if hand_choice == "2" else 8.0)
        
        # Session duration
        print("\nHow long has the child been learning today?")
        print("1. Just started (about 5 minutes)")
        print("2. Learning for a little while (about 15 minutes)")
        print("3. Learning for a long time (about 25 minutes)")
        print("4. Looks tired today (about 35 minutes)")
        session_choice = input("Choose one [2]: ").strip() or "2"
        session_minutes = 5 if session_choice == "1" else (15 if session_choice == "2" else (25 if session_choice == "3" else 35))
        
        # Determine the best next moment (wellbeing recommendation)
        if session_minutes >= 30:
            next_moment = "Rest and story time"
            next_moment_note = "Take a tiny rest, then enjoy a short story connected to learning."
        elif session_minutes >= 20:
            next_moment = "Story time"
            next_moment_note = f"Use a short story that gently prepares the child for {next_task}."
        elif session_minutes >= 12:
            next_moment = "Learning game"
            next_moment_note = f"Play a quick game before moving into {next_task}."
        else:
            next_moment = "Next learning activity"
            next_moment_note = f"Continue softly with {next_task}."
            
        print(f"\n[BUDDY] Speaking to {student_name} about {current_act}...")
        
        buddy.give_praise(
            student_name=student_name,
            precision=precision,
            current_act=current_act,
            next_task=next_task,
            language_preference=language,
            jerk_index=jerk_index,
            session_minutes=session_minutes,
            next_moment=next_moment,
            next_moment_note=next_moment_note
        )
        
        current_idx = next_idx
        
        choice = input("\nContinue? (y/n) [y]: ").strip().lower() or "y"
        if choice == 'n':
            print("Goodbye! 👋")
            break


async def run_live_demo():
    """Future placeholder for live voice mode (similar to your Mindora live mode)"""
    print("\n--- Live Voice Mode (Coming Soon) ---")
    print("This would integrate real-time mic + BuddyAI + TTS")
    # You can expand this later with pyaudio + VoiceEngine


def main():
    while True:
        print("\n" + "="*40)
        print("          BUDDY AI MAIN MENU")
        print("="*40)
        print("1. Interactive Test Mode (Text)")
        print("2. Live Voice Demo (Placeholder)")
        print("3. Exit")
        
        choice = input("\nSelection: ").strip()
        
        if choice == "1":
            run_interactive_mode()
        elif choice == "2":
            asyncio.run(run_live_demo())
        elif choice == "3":
            print("Thank you for using BuddyAI! 👋")
            break
        else:
            print("Invalid selection. Please try again.")


if __name__ == "__main__":
    main()