"""
Test script for the HTTP endpoint - /diagnostic/{prediagnostic_id}
Corrected version for HU5 implementation
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
from datetime import datetime, timezone

async def create_test_prediagnostic():
    """Create a test prediagnostic case directly in MongoDB"""
    try:
        await mongo_manager.connect()
        test_prediagnostic_id = str(uuid.uuid4())
        test_case = {
            "user_id": "test_doctor_endpoint",
            "prediagnostico_id": test_prediagnostic_id,  # Nombre corregido
            "radiografia_url": "https://example.com/xrays/doctor_test.jpg",
            "resultado_modelo": {
                "probabilidad_neumonia": 0.85,
                "etiqueta": "Viral Pneumonia"
            },
            "estado": "Procesado",  # Estado corregido (con mayúscula)
            "fecha_procesamiento": datetime.now(timezone.utc),
            "fecha_subida": datetime.now(timezone.utc)
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
        
        # Prepare diagnostic payload - CORREGIDO
        diagnostic_payload = {
            "aprobacion": True,  # Cambiado de "approval" a "aprobacion"
            "comentario": "Confirmo diagnóstico de neumonía viral. Infiltrados bilaterales presentes. Recomiendo tratamiento antiviral y seguimiento en 48 horas."  # Cambiado de "comments" a "comentario" y comentario más largo
        }
        
        # Test the endpoint - URL CORREGIDA
        print(f"🌐 Testing endpoint with ID: {test_id}")
        async with httpx.AsyncClient() as client:
            # URL corregida: removido "/prediagnostic" del path
            response = await client.post(f"{base_url}/prediagnostic/diagnostic/{test_id}", json=diagnostic_payload)
            
            if response.status_code == 200:
                print("✅ Diagnostic POST Test PASSED!")
                data = response.json()
                print("📋 Response data:")
                print(json.dumps(data, indent=2, default=str))
                
                # Check required fields - CAMPOS CORREGIDOS
                required_fields = ["_id", "prediagnostico_id", "aprobacion", "comentarios", "fecha_revision"]  # Campos corregidos
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("✅ All required fields present!")
                    
                    # Verificar valores específicos
                    if data["aprobacion"] == diagnostic_payload["aprobacion"]:
                        print("✅ Aprobacion field matches!")
                    else:
                        print(f"⚠️  Aprobacion mismatch: expected {diagnostic_payload['aprobacion']}, got {data['aprobacion']}")
                    
                    if data["comentarios"] == diagnostic_payload["comentario"]:
                        print("✅ Comentarios field matches!")
                    else:
                        print(f"⚠️  Comentarios mismatch")
                        
                    if data["prediagnostico_id"] == test_id:
                        print("✅ Prediagnostico ID matches!")
                    else:
                        print(f"⚠️  Prediagnostico ID mismatch")
                        
                else:
                    print(f"⚠️  Missing fields: {missing_fields}")
                    
            else:
                print(f"❌ Diagnostic POST Test FAILED - Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                # Intentar parsear el error
                try:
                    error_data = response.json()
                    print("📋 Error details:")
                    print(json.dumps(error_data, indent=2, default=str))
                except:
                    print("Could not parse error response as JSON")
                    
    except Exception as e:
        print(f"❌ Error during diagnostic endpoint test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mongo_manager.disconnect()

async def test_diagnostic_rejection():
    """Test diagnostic rejection scenario"""
    base_url = "http://localhost:8000"
    print("\n🧪 Testing Diagnostic REJECTION scenario")
    print("=" * 50)
    
    try:
        await mongo_manager.connect()
        
        # Create another test case
        test_prediagnostic_id = str(uuid.uuid4())
        test_case = {
            "user_id": "test_doctor_rejection",
            "prediagnostico_id": test_prediagnostic_id,
            "radiografia_url": "https://example.com/xrays/normal_test.jpg",
            "resultado_modelo": {
                "probabilidad_neumonia": 0.75,
                "etiqueta": "Possible Pneumonia"
            },
            "estado": "Procesado",
            "fecha_procesamiento": datetime.now(timezone.utc),
            "fecha_subida": datetime.now(timezone.utc)
        }
        await mongo_manager.prediagnosticos_collection.insert_one(test_case)
        
        # Test rejection payload
        rejection_payload = {
            "aprobacion": False,
            "comentario": "Después de revisar la radiografía, no se observan signos claros de neumonía. Los hallazgos son compatibles con patrón pulmonar normal. Recomiendo reevaluar síntomas clínicos."
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/prediagnostic/diagnostic/{test_prediagnostic_id}", json=rejection_payload)
            
            if response.status_code == 200:
                print("✅ Rejection Test PASSED!")
                data = response.json()
                
                if data["aprobacion"] == False:
                    print("✅ Rejection properly recorded!")
                else:
                    print("⚠️  Rejection not properly recorded")
            else:
                print(f"❌ Rejection Test FAILED - Status: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error during rejection test: {e}")
    finally:
        await mongo_manager.disconnect()

async def test_validation_errors():
    """Test validation error scenarios"""
    base_url = "http://localhost:8000"
    print("\n🧪 Testing VALIDATION errors")
    print("=" * 40)
    
    try:
        # Test with short comment (should fail)
        print("Testing short comment validation...")
        short_comment_payload = {
            "aprobacion": True,
            "comentario": "OK"  # Muy corto, debe fallar
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/prediagnostic/diagnostic/TEST_ID", json=short_comment_payload)
            
            if response.status_code == 422:
                print("✅ Short comment validation PASSED (correctly rejected)")
            else:
                print(f"⚠️  Short comment validation unexpected result: {response.status_code}")
                
        # Test with non-existent prediagnostic ID
        print("Testing non-existent ID...")
        valid_payload = {
            "aprobacion": True,
            "comentario": "Este prediagnóstico no debería existir en la base de datos"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/prediagnostic/diagnostic/NONEXISTENT_ID", json=valid_payload)
            
            if response.status_code == 404:
                print("✅ Non-existent ID validation PASSED (correctly returned 404)")
            else:
                print(f"⚠️  Non-existent ID unexpected result: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error during validation tests: {e}")

if __name__ == "__main__":
    print("🏥 HU5 - Doctor Diagnostic Endpoint Test Suite")
    print("=" * 60)
    
    # Run all tests
    asyncio.run(test_diagnostic_endpoint())
    asyncio.run(test_diagnostic_rejection())
    asyncio.run(test_validation_errors())
    
    print("\n✨ Test suite completed!")
    print("💡 Make sure your FastAPI server is running on localhost:8000")
    print("💡 Command: python -m uvicorn src.main:app --reload --port 8000")