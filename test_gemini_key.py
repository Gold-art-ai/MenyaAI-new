import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import find_dotenv, load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
DOTENV_PATH = find_dotenv(usecwd=True) or str(PROJECT_ROOT / ".env")
load_dotenv(DOTENV_PATH)


def mask_key(api_key):
    if len(api_key) <= 8:
        return "****"
    return f"{api_key[:4]}...{api_key[-4:]}"


def parse_http_error(error):
    try:
        body = error.read().decode("utf-8", errors="replace")
        data = json.loads(body)
        return data.get("error", {}).get("message", body)
    except Exception:
        return getattr(error, "reason", "") or str(error)


def test_gemini_key(api_key):
    print(f"Testing Gemini API key {mask_key(api_key)}...")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Say hello!"}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 128,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            text = res_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            print("OK: API key is valid. Response:", text or "<empty response>")
            return True
    except urllib.error.HTTPError as error:
        print(f"FAIL: API key test failed: HTTP {error.code}: {parse_http_error(error)}")
        return False
    except Exception as error:
        print("FAIL: API key test failed:", error)
        return False


if __name__ == "__main__":
    api_keys = []
    for env_name in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GOOGLE_API_KEY"):
        api_key = os.environ.get(env_name, "").strip()
        if api_key and api_key not in api_keys:
            api_keys.append(api_key)

    if not api_keys:
        print("Please set GEMINI_API_KEY first, or create a .env file in the project root.")
        print('PowerShell: $env:GEMINI_API_KEY="your-key-here"')
        print("Command Prompt: set GEMINI_API_KEY=your-key-here")
    else:
        for api_key in api_keys:
            test_gemini_key(api_key)
