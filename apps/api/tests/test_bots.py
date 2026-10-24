"""
Test script for WhatsApp and Telegram bot webhooks in Grievance360
"""

import sys
import os

# Set UTF-8 encoding for standard output on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure apps/api is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_whatsapp_status_check():
    print("\n--- Testing WhatsApp STATUS check ---")
    response = client.post(
        "/api/v1/bot/whatsapp",
        data={
            "Body": "STATUS GRV-2026-00001",
            "From": "whatsapp:+919876543210",
        },
    )
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Response Body:\n{response.text[:300]}...")
    assert response.status_code == 200
    assert "<Response>" in response.text
    assert "<Message>" in response.text
    assert "AICTE Grievance360" in response.text
    print("WhatsApp STATUS check PASSED.")


def test_whatsapp_file_complaint():
    print("\n--- Testing WhatsApp FILE complaint ---")
    response = client.post(
        "/api/v1/bot/whatsapp",
        data={
            "Body": "FILE Ragging incident in freshman dormitory hostel block C with physical intimidation and threats",
            "From": "whatsapp:+919876543210",
        },
    )
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Response Body:\n{response.text[:300]}...")
    assert response.status_code == 200
    assert "<Response>" in response.text
    assert "Grievance Registered Successfully" in response.text
    assert "Anti-Ragging" in response.text or "Bureau" in response.text
    assert "CRITICAL" in response.text
    print("WhatsApp FILE complaint PASSED.")


def test_telegram_status_check():
    print("\n--- Testing Telegram /status command ---")
    payload = {
        "update_id": 10001,
        "message": {
            "message_id": 42,
            "from": {
                "id": 987654321,
                "first_name": "TestCitizen",
                "username": "test_citizen",
            },
            "chat": {
                "id": 987654321,
                "type": "private",
            },
            "date": 1698060000,
            "text": "/status GRV-2026-00001",
        },
    }
    response = client.post("/api/v1/bot/telegram", json=payload)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Telegram Action: {data.get('action')}")
    print(f"Telegram Text Snippet: {data.get('text', '')[:200]}...")
    assert response.status_code == 200
    assert data.get("ok") is True
    assert data.get("action") == "STATUS_CHECK_SUCCESS"
    print("Telegram /status PASSED.")


def test_telegram_file_complaint():
    print("\n--- Testing Telegram /file command ---")
    payload = {
        "update_id": 10002,
        "message": {
            "message_id": 43,
            "from": {
                "id": 987654321,
                "first_name": "TestCitizen",
                "username": "test_citizen",
            },
            "chat": {
                "id": 987654321,
                "type": "private",
            },
            "date": 1698060000,
            "text": "/file College demanding unauthorized bribe for semester exam hall ticket issuance",
        },
    }
    response = client.post("/api/v1/bot/telegram", json=payload)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Telegram Action: {data.get('action')}")
    print(f"Tracking ID: {data.get('tracking_id')}")
    print(f"Assigned Bureau: {data.get('bureau')}")
    print(f"Assigned Priority: {data.get('priority')}")
    assert response.status_code == 200
    assert data.get("ok") is True
    assert data.get("action") == "FILE_COMPLAINT_SUCCESS"
    assert data.get("tracking_id") is not None
    print("Telegram /file PASSED.")


if __name__ == "__main__":
    test_whatsapp_status_check()
    test_whatsapp_file_complaint()
    test_telegram_status_check()
    test_telegram_file_complaint()
    print("\n==========================================")
    print("ALL WHATSAPP & TELEGRAM TESTS PASSED 100%!")
    print("==========================================")
