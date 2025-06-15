# test_image.py
"""
Robust test script for Beam, focused on static image background removal.
This version handles both synchronous (immediate result) and asynchronous (polling)
responses from the API. It reads the full URL and credentials from a .env file.
"""

import requests
import base64
import os
import sys
import time
from dotenv import load_dotenv

# This line finds and loads the .env file from the current directory
load_dotenv()

# --- Configuration ---
# Securely load the full URL and API key from the environment
BEAM_ENDPOINT_URL = os.getenv("BEAM_ENDPOINT_URL")
BEAM_API_KEY = os.getenv("BEAM_API_KEY")

# --- IMPORTANT: Change this to your input image file ---
INPUT_IMAGE_PATH = "goresh.png"  # Or "test.jpg", etc.

# The output will be a transparent PNG
OUTPUT_IMAGE_PATH = "test_output.png"


# --- Main Script ---
def main():
    print("🚀 Starting Robust STATIC IMAGE background removal test...")

    # 1. Pre-flight checks
    if not BEAM_ENDPOINT_URL or not BEAM_API_KEY:
        print("❌ Error: BEAM_ENDPOINT_URL and BEAM_API_KEY must be set in your .env file.")
        sys.exit(1)

    if not os.path.exists(INPUT_IMAGE_PATH):
        print(f"❌ Error: Test file not found at '{INPUT_IMAGE_PATH}'")
        print("    Please make sure you have an image file named 'test.png' (or matching your INPUT_IMAGE_PATH) in the same directory.")
        sys.exit(1)

    # 2. Read and encode the input image
    with open(INPUT_IMAGE_PATH, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")
        print(f"✅ Read and encoded '{INPUT_IMAGE_PATH}'")

    # 3. Prepare request payload and headers
    headers = {
        "Authorization": f"Bearer {BEAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "image": image_b64,
        "quality": "quality",  # Using a high-quality setting
        "format": "png"       # Requesting a PNG output for transparency
    }

    # 4. Submit the initial job request
    print(f"📡 Submitting job to {BEAM_ENDPOINT_URL}...")
    try:
        response = requests.post(BEAM_ENDPOINT_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
        response_data = response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ Network or request error during submission: {e}")
        sys.exit(1)
    except requests.exceptions.JSONDecodeError:
        print(f"❌ Error: Failed to decode JSON from response. Response text: {response.text}")
        sys.exit(1)

    # 5. Handle the response: could be synchronous or asynchronous
    final_image_b64 = None

    if "task_id" in response_data:
        # --- ASYNCHRONOUS WORKFLOW ---
        task_id = response_data["task_id"]
        print(f"✅ Job submitted asynchronously! Task ID: {task_id}")
        print("⏳ Polling for results...")

        status_url = f"{BEAM_ENDPOINT_URL}/{task_id}"
        start_time = time.time()
        timeout_seconds = 180  # 3 minutes for static images

        while time.time() - start_time < timeout_seconds:
            try:
                poll_response = requests.get(status_url, headers=headers)
                poll_response.raise_for_status()
                status_data = poll_response.json()
                status = status_data.get("status")

                if status == "COMPLETE":
                    print("✅ Task complete!")
                    final_image_b64 = status_data.get("outputs", {}).get("image")
                    if not final_image_b64:
                        print(f"❌ Error: Task completed but no image was returned. Full output: {status_data}")
                    break
                elif status == "FAILED":
                    print(f"❌ Task failed. Reason: {status_data.get('outputs')}")
                    break
                else:
                    print(f"   Current status: {status}... waiting")
                    time.sleep(2)  # Poll more frequently for static images

            except requests.exceptions.RequestException as e:
                print(f"❌ Network or request error during polling: {e}")
                break
        else:
            print("❌ Polling timed out after 3 minutes.")

    elif "image" in response_data and response_data.get("success"):
        # --- SYNCHRONOUS WORKFLOW ---
        print("✅ Job completed synchronously!")
        final_image_b64 = response_data["image"]

    else:
        # --- UNKNOWN RESPONSE ---
        print(f"❌ Error: The API returned an unknown response format. Response: {response_data}")

    # 6. Save the final image if we have it
    if final_image_b64:
        try:
            output_image_data = base64.b64decode(final_image_b64)
            with open(OUTPUT_IMAGE_PATH, "wb") as f:
                f.write(output_image_data)
            print(f"🎉 Success! Output saved to '{OUTPUT_IMAGE_PATH}'")
        except Exception as e:
            print(f"❌ Error decoding or saving the final image: {e}")
    else:
        print("😔 No final image was retrieved.")


if __name__ == "__main__":
    main()
