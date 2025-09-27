"""
Test script for the HTTP endpoint - /diagnostic/{prediagnostic_id}
"""
import asyncio
import httpx
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from src.database.mongodb import mongo_manager
import uuid
from datetime import datetime

async def create_test_prediagnostic():
    """Create a test prediagnostic case directly in MongoDB"""
    try:
        await mongo_manager.connect()
        test_prediagnostic_id = str(uuid.uuid4())
        test_case = {
            "user_id": "test_doctor_endpoint",
            "prediagnostic_id": test_prediagnostic_id,
            "radiografia_url": "https://example.com/xrays/doctor_test.jpg",
            "resultado_modelo": {
                "probabilidad_neumonia": 0.85,
                "etiqueta": "Viral Pneumonia"
            },
            "estado": "procesado",
            "fecha_procesamiento": datetime.utcnow(),
            "fecha_subida": datetime.utcnow()
        }
        await mongo_manager.prediagnosticos_collection.insert_one(test_case)
        print(f"✅ Prediagnostic case created with ID: {test_prediagnostic_id}")
        return test_prediagnostic_id
    except Exception as e:
        print(f"❌ Error creating prediagnostic case: {e}")
        raise

async def test_diagnostic_endpoint():
    """Test the HTTP endpoint /diagnostic/{prediagnostic_id}"""
    base_url = "http://localhost:8000"
    print("🧪 Testing HTTP Endpoint: /diagnostic/{prediagnostic_id}")
    print("=" * 65)
    try:
        # Create test prediagnostic
        print("📝 Creating prediagnostic case...")
        test_id = await create_test_prediagnostic()
        # Prepare diagnostic payload
        diagnostic_payload = {
            "approval": True,
            "comments": "Aprobado por el doctor para pruebas automáticas"
        }
        # Test the endpoint
        print(f"🌐 Testing endpoint with ID: {test_id}")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/prediagnostic/diagnostic/{test_id}", json=diagnostic_payload)
            if response.status_code == 200:
                print("✅ Diagnostic POST Test PASSED!")
                data = response.json()
                print("📋 Response data:")
                print(json.dumps(data, indent=2, default=str))
                # Check required fields
                required_fields = ["_id", "prediagnostic_id", "approval", "comments", "review_date"]
                missing_fields = [field for field in required_fields if field not in data]
                if not missing_fields:
                    print("✅ All required fields present!")
                else:
                    print(f"⚠️  Missing fields: {missing_fields}")
            else:
                print(f"❌ Diagnostic POST Test FAILED - Status: {response.status_code}")
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error during diagnostic endpoint test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mongo_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(test_diagnostic_endpoint())
