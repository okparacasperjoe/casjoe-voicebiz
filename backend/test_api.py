import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"

# Generate a fake token for testing auth bypass locally, 
# but auth is enforced. Let's create a helper script that generates a valid token.
import jwt
import time

SECRET = "change_this_to_a_random_64_char_string_in_production"

def generate_test_token():
    payload = {
        "user_id": "test-user-123",
        "business_id": "test-business-456",
        "exp": int(time.time()) + 3600
    }
    # Note: In config, CASJOE_JWT_SECRET is empty string by default unless set in .env.
    # In .env.example it is "your_casjoe_jwt_secret_here"
    return jwt.encode(payload, "your_casjoe_jwt_secret_here", algorithm="HS256")


async def test_pipeline():
    token = generate_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("1. Testing Health...")
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/health")
        print(f"Health: {r.status_code}\n{json.dumps(r.json(), indent=2)}")
        
    print("\n2. Testing Intent (Needs N-ATLAS)...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            f"{BASE_URL}/intent", 
            headers=headers,
            data={"transcript": "How much did I sell today?", "language": "eng"}
        )
        print(f"Intent: {r.status_code}")
        if r.status_code == 200:
            print(json.dumps(r.json(), indent=2))
        else:
            print(r.text)

if __name__ == "__main__":
    asyncio.run(test_pipeline())
