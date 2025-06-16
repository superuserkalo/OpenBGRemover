# test_gateway.py
"""
Test script for your local Go gateway running on port 8080
"""

import requests
import base64
import json
import time
from pathlib import Path

# Configuration
GATEWAY_URL = "https://openbgremover-762235720907.europe-west4.run.app"
TEST_IMAGE = "goresh.png"  # Your test image

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")

    try:
        response = requests.get(f"{GATEWAY_URL}/health")
        response.raise_for_status()

        data = response.json()
        print("✅ Health check passed!")
        print(f"   Service: {data.get('service')}")
        print(f"   Version: {data.get('version')}")
        print(f"   Environment: {data.get('environment')}")
        print(f"   Beam configured: {data.get('beam_endpoint_configured')}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_api_info():
    """Test the API info endpoint"""
    print("\n📋 Testing API info endpoint...")

    try:
        response = requests.get(f"{GATEWAY_URL}/api/info")
        response.raise_for_status()

        data = response.json()
        print("✅ API info retrieved!")
        print(f"   Service: {data.get('service_name')}")
        print(f"   Endpoints: {list(data.get('endpoints', {}).keys())}")
        print(f"   Supported formats: {data.get('supported_formats')}")
        print(f"   Quality presets: {data.get('quality_presets')}")
        return True
    except Exception as e:
        print(f"❌ API info failed: {e}")
        return False

def test_remove_background():
    """Test the main background removal endpoint"""
    print(f"\n🖼️  Testing background removal with {TEST_IMAGE}...")

    # Check if test image exists
    if not Path(TEST_IMAGE).exists():
        print(f"❌ Test image '{TEST_IMAGE}' not found!")
        return False

    # Read and encode image
    print("📁 Reading and encoding image...")
    try:
        with open(TEST_IMAGE, "rb") as f:
            image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode('utf-8')
        print(f"✅ Image encoded ({len(image_b64)} characters)")
    except Exception as e:
        print(f"❌ Failed to read image: {e}")
        return False

    # Prepare request
    payload = {
        "image_data": image_b64,
        "quality": "auto",
        "format": "png",
        "return_mask": False
    }

    print("📤 Sending request to gateway...")
    start_time = time.time()

    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/remove-background",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=200  # Long timeout for processing
        )

        end_time = time.time()
        total_time = (end_time - start_time) * 1000

        print(f"📥 Response received (status: {response.status_code})")
        print(f"⏱️  Total request time: {total_time:.0f}ms")

        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                print("✅ Background removal successful!")

                # Print processing info
                proc_time = data.get("processing_time_ms", 0)
                print(f"   Gateway processing time: {proc_time}ms")

                if "metadata" in data:
                    metadata = data["metadata"]
                    if "beam_processing_time_ms" in metadata:
                        beam_time = metadata["beam_processing_time_ms"]
                        print(f"   Beam processing time: {beam_time}ms")
                    if "original_size" in metadata:
                        print(f"   Original size: {metadata['original_size']}")
                    if "output_size" in metadata:
                        print(f"   Output size: {metadata['output_size']}")

                # Save result
                if "result_image" in data:
                    output_path = "gateway_test_output.png"
                    try:
                        # Handle data URL or plain base64
                        result_b64 = data["result_image"]
                        if result_b64.startswith("data:"):
                            result_b64 = result_b64.split(",")[1]

                        result_data = base64.b64decode(result_b64)
                        with open(output_path, "wb") as f:
                            f.write(result_data)
                        print(f"💾 Result saved to: {output_path}")
                    except Exception as e:
                        print(f"❌ Failed to save result: {e}")

                return True
            else:
                print(f"❌ Processing failed: {data.get('error', 'Unknown error')}")
                if "error_code" in data:
                    print(f"   Error code: {data['error_code']}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the gateway running on port 8080?")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_invalid_requests():
    """Test error handling"""
    print("\n🧪 Testing error handling...")

    # Test 1: Missing image data
    print("Testing missing image data...")
    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/remove-background",
            json={"quality": "auto"},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ Correctly rejected missing image data")
        else:
            print(f"❌ Should have rejected missing image data (got {response.status_code})")
    except Exception as e:
        print(f"❌ Error testing missing image data: {e}")

    # Test 2: Invalid quality
    print("Testing invalid quality...")
    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/remove-background",
            json={"image_data": "dGVzdA==", "quality": "invalid"},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ Correctly rejected invalid quality")
        else:
            print(f"❌ Should have rejected invalid quality (got {response.status_code})")
    except Exception as e:
        print(f"❌ Error testing invalid quality: {e}")

    # Test 3: Invalid image data
    print("Testing invalid base64...")
    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/remove-background",
            json={"image_data": "not-base64!"},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ Correctly rejected invalid base64")
        else:
            print(f"❌ Should have rejected invalid base64 (got {response.status_code})")
    except Exception as e:
        print(f"❌ Error testing invalid base64: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing Go Gateway at localhost:8080")
    print("=" * 50)

    # Check if test image exists
    if not Path(TEST_IMAGE).exists():
        print(f"❌ Test image '{TEST_IMAGE}' not found!")
        print("   Please add a test image to the current directory")
        return

    # Test health endpoint
    if not test_health():
        print("\n❌ Gateway health check failed!")
        return

    # Test API info
    if not test_api_info():
        print("\n❌ API info test failed!")
        return

    # Test main functionality
    if test_remove_background():
        print("\n✅ Background removal test passed!")
    else:
        print("\n❌ Background removal test failed!")
        return

    # Test error handling
    test_invalid_requests()

    print("\n🎉 All tests completed!")
    print("\nYour Go gateway is working correctly!")
    print("Ready for deployment to Sevala! 🚀")

if __name__ == "__main__":
    main()
