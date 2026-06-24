from src.buddy_service.voice_engine import VoiceEngine, preprocess_kinyarwanda

def test_pronunciation():
    print("=== Testing Kinyarwanda Phonetic Rules and Voice Upgrades ===")
    
    # 1. Show the phonetic transformation
    test_phrases = [
        "Muraho neza cyane",
        "Uyu mwana akunda inyoni cyane",
        "Wabikoze neza ku gushushanya imirongo",
        "Umunyunyuzi wacu mwiza",
        "Komeza ugerageze ushobora gushushanya ishusho buhoro buhoro"
    ]
    
    print("\n[PHONETIC TRANSLATION SAMPLES]:")
    for phrase in test_phrases:
        translated = preprocess_kinyarwanda(phrase)
        print(f"  Original : '{phrase}'")
        print(f"  Phonetic : '{translated}'\n")

    # 2. Speak Kinyarwanda using Zuri (upgraded female voice)
    print("[TTS SPEAKING] Playing upgraded Kinyarwanda TTS (sw-KE-ZuriNeural)...")
    engine_zuri = VoiceEngine(rw_voice="sw-KE-ZuriNeural")
    
    # Let's speak a greeting and some praise
    praise_text = "[RW] Muraho Gloria! Wabikoze neza cyane kuri gushushanya ishusho! [EN] Let's try tracing numbers next!"
    print(f"  Speaking: {praise_text}")
    engine_zuri.speak(praise_text)

    # Let's speak a pure Kinyarwanda phrase with palatal nasals 'ny'
    ny_text = "[RW] Uyu mwana mwiza akunda inyoni n'umunyunyuzi cyane"
    print(f"  Speaking: {ny_text}")
    engine_zuri.speak(ny_text)

    print("\n=== Test Finished! ===")

if __name__ == "__main__":
    test_pronunciation()
