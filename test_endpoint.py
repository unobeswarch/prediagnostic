"""
Test script for the HTTP endpoint - /prediagnostic/case/{prediagnostico_id}
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


async def create_test_case():
    """Create a test case directly in MongoDB"""
    try:
        await mongo_manager.connect()
        
        # Create test data
        test_prediagnostico_id = str(uuid.uuid4())
        test_case = {
            "user_id": "test_patient_endpoint",
            "prediagnostico_id": test_prediagnostico_id,
            "radiografia_url": "https://example.com/xrays/endpoint_test.jpg",
            "resultado_modelo": {
                "probabilidad_neumonia": 0.92,
                "etiqueta": "Bacterial Pneumonia"
            },
            "estado": "procesado",
            "fecha_procesamiento": datetime.utcnow(),
            "fecha_subida": datetime.utcnow()
        }
        
        # Insert directly into MongoDB
        await mongo_manager.prediagnosticos_collection.insert_one(test_case)
        
        print(f"✅ Test case created with ID: {test_prediagnostico_id}")
        return test_prediagnostico_id
        
    except Exception as e:
        print(f"❌ Error creating test case: {e}")
        raise


async def test_endpoint():
    """Test the HTTP endpoint /prediagnostic/case/{prediagnostico_id}"""
    
    base_url = "http://localhost:8000"  # Default FastAPI port
    
    print("🧪 Testing HTTP Endpoint: /prediagnostic/case/{prediagnostico_id}")
    print("=" * 65)
    
    try:
        # Create test case
        print("📝 Creating test case...")
        test_id = await create_test_case()
        
        # Test the endpoint
        print(f"🌐 Testing endpoint with ID: {test_id}")
        
        async with httpx.AsyncClient() as client:
            # Test with valid ID
            response = await client.get(f"{base_url}/prediagnostic/case/{test_id}")
            
            if response.status_code == 200:
                print("✅ HTTP Test PASSED!")
                data = response.json()
                print("📋 Response data:")
                print(json.dumps(data, indent=2, default=str))
                
                # Verify required fields
                required_fields = ["user_id", "prediagnostico_id", "radiografia_url", "resultado_modelo", "estado"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("✅ All required fields present!")
                else:
                    print(f"⚠️  Missing fields: {missing_fields}")
                    
            else:
                print(f"❌ HTTP Test FAILED - Status: {response.status_code}")
                print(f"Response: {response.text}")
            
            # Test with non-existent ID
            print(f"\n🔍 Testing with non-existent ID...")
            response = await client.get(f"{base_url}/prediagnostic/case/non-existent-id")
            
            if response.status_code == 404:
                print("✅ Correctly returned 404 for non-existent case")
            else:
                print(f"❌ Expected 404, got {response.status_code}")
                
            # Test health endpoint
            print(f"\n🏥 Testing health endpoint...")
            response = await client.get(f"{base_url}/prediagnostic/health")
            
            if response.status_code == 200:
                print("✅ Health endpoint working!")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
        
    except httpx.ConnectError:
        print("❌ Connection failed!")
        print("💡 Make sure the server is running:")
        print("   python cmd/server.py")
        print("   or")
        print("   uvicorn cmd.server:app --host 0.0.0.0 --port 8000")
        
    except Exception as e:
        print(f"❌ Error during endpoint test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await mongo_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(test_endpoint())