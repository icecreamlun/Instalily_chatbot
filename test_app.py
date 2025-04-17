import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint():
    test_messages = [
        {
            "role": "user",
            "content": "How can I install part number PS11752778?"
        }
    ]
    
    response = client.post(
        "/api/chat",
        json={
            "messages": test_messages,
            "model_name": "deepseek"
        }
    )
    
    assert response.status_code == 200
    assert "message" in response.json()
    assert "role" in response.json()["message"]
    assert "content" in response.json()["message"]
    assert response.json()["message"]["role"] == "assistant"

def test_chat_endpoint_compatibility():
    test_messages = [
        {
            "role": "user",
            "content": "Is this part compatible with my WDT780SAEM1 model?"
        }
    ]
    
    response = client.post(
        "/api/chat",
        json={
            "messages": test_messages,
            "model_name": "deepseek"
        }
    )
    
    assert response.status_code == 200
    assert "message" in response.json()

if __name__ == "__main__":
    pytest.main(["-v"]) 