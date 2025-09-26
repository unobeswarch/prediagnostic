"""
Test script for the HU implementation - get case by prediagnostico_id
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from src.database.mongodb import mongo_manager
from src.services.prediagnostic_service import prediagnostic_service
from src.database.models import ResultadoModelo
import uuid
from datetime import datetime


async def test_hu_implementation():
    """Test the HU: Get case by prediagnostico_id"""
    
    try:
        print("🔌 Connecting to MongoDB...")
        await mongo_manager.connect()
        print("✅ MongoDB connected!")
        
        # Create a test prediagnostico directly in MongoDB (simulating existing data)
        test_prediagnostico_id = str(uuid.uuid4())
        
        print(f"📝 Creating test case with ID: {test_prediagnostico_id}")
        
        # Create test case directly in MongoDB
        test_case = {
            "user_id": "test_patient_001",
            "prediagnostico_id": test_prediagnostico_id,
            "radiografia_url": "https://example.com/xrays/test_123.jpg",
            "resultado_modelo": {
                "probabilidad_neumonia": 0.87,
                "etiqueta": "Viral Pneumonia"
            },
            "estado": "procesado",
            "fecha_procesamiento": datetime.utcnow(),
            "fecha_subida": datetime.utcnow()
        }
        
        # Insert directly into MongoDB
        await mongo_manager.prediagnosticos_collection.insert_one(test_case)
        print(f"✅ Test case created: {test_prediagnostico_id}")
        
        # Now test the HU functionality: Get case by ID
        print(f"🔍 Testing HU: Getting case by prediagnostico_id...")
        
        case = await prediagnostic_service.get_prediagnostico(test_prediagnostico_id)
        
        if case:
            print("✅ HU Test PASSED!")
            print("📋 Case details retrieved:")
            print(f"   - User ID: {case['user_id']}")
            print(f"   - Prediagnostico ID: {case['prediagnostico_id']}")
            print(f"   - Radiografia URL: {case['radiografia_url']}")
            print(f"   - AI Result: {case['resultado_modelo']['etiqueta']} ({case['resultado_modelo']['probabilidad_neumonia']:.2%})")
            print(f"   - Estado: {case['estado']}")
            
            # Handle datetime fields that might be in different formats
            fecha_key = 'fecha_procesamiento' if 'fecha_procesamiento' in case else 'created_at'
            if fecha_key in case:
                print(f"   - Fecha: {case[fecha_key]}")
            else:
                print("   - Fecha: Not available")
                print(f"   - Available fields: {list(case.keys())}")
        else:
            print("❌ HU Test FAILED - Case not found")
            
        # Test with non-existent ID
        print(f"\n🔍 Testing with non-existent ID...")
        fake_case = await prediagnostic_service.get_prediagnostico("non-existent-id")
        
        if fake_case is None:
            print("✅ Correctly handled non-existent case")
        else:
            print("❌ Should have returned None for non-existent case")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🔌 Disconnecting from MongoDB...")
        await mongo_manager.disconnect()
        print("✅ Disconnected!")


if __name__ == "__main__":
    print("🧪 Testing HU Implementation: Get Case by Prediagnostico ID")
    print("=" * 60)
    asyncio.run(test_hu_implementation())