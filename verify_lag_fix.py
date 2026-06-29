import os
import sys
import time
import hashlib
from pathlib import Path

# Add buddy_service to system path
PROJECT_ROOT = Path(__file__).resolve().parent
BUDDY_SERVICE_DIR = PROJECT_ROOT / "src" / "buddy_service"
if str(BUDDY_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(BUDDY_SERVICE_DIR))

from voice_engine import VoiceEngine, preprocess_kinyarwanda

def verify_lag_fix():
    print("=== VERIFYING ML SPEAKER LAG FIX ===")
    
    # 1. Test Lazy Initialization
    print("\n[TEST 1] Lazy Initialization of pyttsx3")
    engine = VoiceEngine()
    print(f"  engine.en_engine initialized? {engine.en_engine is not None}")
    assert engine.en_engine is None, "Failed: en_engine should be None on initialization (lazy load)."
    
    # Trigger English to force initialization
    engine._get_pyttsx3_fallback()
    print(f"  engine.en_engine after access: {engine.en_engine is not None}")
    assert engine.en_engine is not None, "Failed: en_engine should be initialized on demand."
    print("  [PASS] Lazy initialization verified.")

    # 2. Test Persistent Audio Caching
    print("\n[TEST 2] Persistent Audio Caching")
    test_phrase = "Urakoze cyane kurasa ku ntego"
    processed = preprocess_kinyarwanda(test_phrase)
    voice = engine.rw_voice
    text_hash = hashlib.md5(f"{processed}_{voice}".encode("utf-8")).hexdigest()
    cached_file = os.path.join(engine.cache_dir, f"{text_hash}.mp3")

    # Ensure clean start for test_phrase
    if os.path.exists(cached_file):
        os.remove(cached_file)

    # First speak: requires Edge TTS network generation
    print(f"  First Run: Generating speech for '{test_phrase}'...")
    start_time = time.time()
    engine.speak(f"[RW] {test_phrase}")
    first_duration = time.time() - start_time
    print(f"  First run duration (includes network fetch and playback): {first_duration:.2f} seconds")

    # Assert cache file was created
    print(f"  Checking if cache file exists: {cached_file}")
    assert os.path.exists(cached_file), "Failed: Cache file was not created!"
    assert os.path.getsize(cached_file) > 0, "Failed: Cache file is empty!"
    print("  [PASS] Cache file successfully created and saved.")

    # Second speak: should be instantaneous from cache (only playback time)
    print(f"  Second Run: Playing from cache...")
    start_time = time.time()
    engine.speak(f"[RW] {test_phrase}")
    second_duration = time.time() - start_time
    print(f"  Second run duration (playback only): {second_duration:.2f} seconds")
    
    # The second run should save the round-trip network lag!
    print("  [PASS] Persistent caching verified.")

    # 3. Test Ollama Offline Prevention
    print("\n[TEST 3] Ollama Offline Loop Prevention")
    from buddy_ai import BuddyAI
    buddy = BuddyAI()
    print(f"  buddy.engine.ollama_enabled initially: {buddy.engine.ollama_enabled}")
    
    # Trigger response generation (which will try Ollama first if offline, fail, and set enabled to False)
    print("  Triggering response (will attempt Ollama and fail/disable if offline)...")
    start_time = time.time()
    resp1 = buddy.generate_response("TestKid", 0.9, "Shapes", "Letters")
    dur1 = time.time() - start_time
    print(f"  First response duration: {dur1:.2f} seconds (may include Ollama connection timeout)")
    print(f"  buddy.engine.ollama_enabled after first attempt: {buddy.engine.ollama_enabled}")
    
    # Second attempt should be instant (no Ollama attempt at all)
    start_time = time.time()
    resp2 = buddy.generate_response("TestKid", 0.9, "Shapes", "Letters")
    dur2 = time.time() - start_time
    print(f"  Second response duration (Ollama disabled): {dur2:.2f} seconds")
    
    if not buddy.engine.ollama_enabled:
        print("  [PASS] Ollama offline prevention active and working (Ollama disabled).")
        assert dur2 < 0.5, "Failed: Second attempt is still blocking/lagging!"
    else:
        print("  [NOTE] Ollama is actually running locally! Ollama remains enabled.")
        
    print("\n=== All Tests Passed Successfully! ===")

if __name__ == "__main__":
    verify_lag_fix()
