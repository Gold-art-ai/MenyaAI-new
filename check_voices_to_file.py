import asyncio
import edge_tts

async def main():
    try:
        voices = await edge_tts.VoicesManager.create()
        with open("voices_list.txt", "w", encoding="utf-8") as f:
            for voice in voices.voices:
                f.write(f"{voice['ShortName']} | {voice['Gender']} | {voice['Locale']}\n")
        print("Done writing to voices_list.txt")
    except Exception as e:
        with open("voices_list.txt", "w", encoding="utf-8") as f:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
