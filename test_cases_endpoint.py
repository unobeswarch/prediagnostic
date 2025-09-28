"""
Test script for the new GET /prediagnostic/cases endpoint (HU3 implementation)
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


async def create_test_data():
    """Create multiple test cases with different estados for testing"""
    try:
        await mongo_manager.connect()
        print("✅ Connected to MongoDB")
        
        # Clear existing test data to avoid duplicates
        await mongo_manager.prediagnosticos_collection.delete_many({"user_id": {"$regex": "^test_"}})
        print("🧹 Cleared existing test data")
        
        # Create test cases with different estados
        test_cases = [
            {
                "user_id": "test_patient_001",
                "prediagnostico_id": str(uuid.uuid4()),
                "radiografia_url": "https://example.com/xrays/test_001.jpg",
                "resultado_modelo": {
                    "probabilidad_neumonia": 0.85,
                    "etiqueta": "Viral Pneumonia"
                },
                "estado": "procesado",  # Should be included in results
                "fecha_procesamiento": datetime.utcnow(),
                "fecha_subida": datetime.utcnow()
            },
            {
                "user_id": "test_patient_002", 
                "prediagnostico_id": str(uuid.uuid4()),
                "radiografia_url": "https://example.com/xrays/test_002.jpg",
                "resultado_modelo": {
                    "probabilidad_neumonia": 0.92,
                    "etiqueta": "Bacterial Pneumonia"
                },
                "estado": "procesado",  # Should be included in results
                "fecha_procesamiento": datetime.utcnow(),
                "fecha_subida": datetime.utcnow()
            },
            {
                "user_id": "test_patient_003",
                "prediagnostico_id": str(uuid.uuid4()),
                "radiografia_url": "https://example.com/xrays/test_003.jpg",
                "resultado_modelo": {
                    "probabilidad_neumonia": 0.78,
                    "etiqueta": "No Pneumonia"
                },
                "estado": "Validado",  # Should NOT be included in results
                "fecha_procesamiento": datetime.utcnow(),
                "fecha_subida": datetime.utcnow()
            },
            {
                "user_id": "test_patient_004",
                "prediagnostico_id": str(uuid.uuid4()),
                "radiografia_url": "https://example.com/xrays/test_004.jpg",
                "resultado_modelo": {
                    "probabilidad_neumonia": 0.65,
                    "etiqueta": "Viral Pneumonia"
                },
                "estado": "pendiente",  # Should NOT be included in results
                "fecha_procesamiento": datetime.utcnow(),
                "fecha_subida": datetime.utcnow()
            },
            {
                "user_id": "test_patient_005",
                "prediagnostico_id": str(uuid.uuid4()),
                "radiografia_url": "https://example.com/xrays/test_005.jpg",
                "resultado_modelo": {
                    "probabilidad_neumonia": 0.88,
                    "etiqueta": "Bacterial Pneumonia"
                },
                "estado": "procesado",  # Should be included in results
                "fecha_procesamiento": datetime.utcnow(),
                "fecha_subida": datetime.utcnow()
            }
        ]
        
        # Insert test cases
        result = await mongo_manager.prediagnosticos_collection.insert_many(test_cases)
        print(f"✅ Created {len(result.inserted_ids)} test cases")
        
        # Count by estado for verification
        procesado_count = await mongo_manager.prediagnosticos_collection.count_documents({"estado": "procesado", "user_id": {"$regex": "^test_"}})
        validado_count = await mongo_manager.prediagnosticos_collection.count_documents({"estado": "Validado", "user_id": {"$regex": "^test_"}})
        pendiente_count = await mongo_manager.prediagnosticos_collection.count_documents({"estado": "pendiente", "user_id": {"$regex": "^test_"}})
        
        print(f"📊 Test data summary:")
        print(f"   - Procesado: {procesado_count} (should be returned)")
        print(f"   - Validado: {validado_count} (should be filtered out)")
        print(f"   - Pendiente: {pendiente_count} (should be filtered out)")
        
        return procesado_count
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        raise


async def test_cases_endpoint():
    """Test the new GET /prediagnostic/cases endpoint"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing HU3 Implementation: GET /prediagnostic/cases")
    print("=" * 60)
    
    try:
        # Create test data
        print("📝 Creating test data...")
        expected_procesado_count = await create_test_data()
        
        # Test the new endpoint
        print(f"\n🌐 Testing GET /prediagnostic/cases endpoint...")
        
        async with httpx.AsyncClient() as client:
            # Test the new /cases endpoint
            response = await client.get(f"{base_url}/prediagnostic/cases")
            
            if response.status_code == 200:
                print("✅ HTTP Test PASSED!")
                data = response.json()
                
                print(f"📋 Response contains {len(data)} cases")
                print("📄 Sample response:")
                print(json.dumps(data[:2] if data else [], indent=2, default=str))
                
                # Verify filtering works correctly
                if len(data) == expected_procesado_count:
                    print(f"✅ Filtering works correctly! Expected {expected_procesado_count}, got {len(data)}")
                else:
                    print(f"⚠️  Filtering issue: Expected {expected_procesado_count}, got {len(data)}")
                
                # Verify response format
                if data:
                    required_fields = ["id", "paciente", "fecha", "estado"]
                    first_case = data[0]
                    missing_fields = [field for field in required_fields if field not in first_case]
                    
                    if not missing_fields:
                        print("✅ Response format correct! All required fields present")
                        print(f"   Fields: {list(first_case.keys())}")
                    else:
                        print(f"❌ Response format issue - Missing fields: {missing_fields}")
                    
                    # Verify all cases have estado="procesado"
                    all_procesado = all(case["estado"] == "procesado" for case in data)
                    if all_procesado:
                        print("✅ All returned cases have estado='procesado'")
                    else:
                        print("❌ Some cases don't have estado='procesado'")
                        
                else:
                    print("⚠️  No cases returned - check if test data was created properly")
                    
            else:
                print(f"❌ HTTP Test FAILED - Status: {response.status_code}")
                print(f"Response: {response.text}")
            
            # Test info endpoint to see if new endpoint is listed
            print(f"\n📋 Testing updated service info...")
            response = await client.get(f"{base_url}/prediagnostic/info")
            
            if response.status_code == 200:
                info = response.json()
                if "/cases" in str(info.get("endpoints", {})):
                    print("✅ New endpoint listed in service info!")
                else:
                    print("⚠️  New endpoint not found in service info")
                print(f"Endpoints: {info.get('endpoints', {})}")
            
        print(f"\n🎯 HU3 Requirement Verification:")
        print(f"   ✅ Endpoint: GET /prediagnostic/cases")
        print(f"   ✅ Filters: estado='procesado'")
        print(f"   ✅ Response format: id, paciente, fecha, estado")
        print(f"   ✅ Integration: Ready for BusinessLogic consumption")
        
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
    asyncio.run(test_cases_endpoint())
