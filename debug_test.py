"""
Debug test to check what's happening with the MongoDB query
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.database.mongodb import mongo_manager
import uuid
from datetime import datetime


async def debug_test():
    """Debug the MongoDB issue"""
    
    try:
        await mongo_manager.connect()
        print("✅ Connected to MongoDB")
        
        # Create a test case
        test_id = str(uuid.uuid4())
        print(f"📝 Creating test case with ID: {test_id}")
        
        test_case = {
            "user_id": "debug_test",
            "prediagnostico_id": test_id,
            "radiografia_url": "https://example.com/debug.jpg",
            "resultado_modelo": {
                "probabilidad_neumonia": 0.95,
                "etiqueta": "Test Case"
            },
            "estado": "procesado",
            "fecha_procesamiento": datetime.utcnow(),
            "fecha_subida": datetime.utcnow()
        }
        
        # Insert
        result = await mongo_manager.prediagnosticos_collection.insert_one(test_case)
        print(f"✅ Inserted with MongoDB _id: {result.inserted_id}")
        
        # Try to find it
        print(f"🔍 Searching for prediagnostico_id: {test_id}")
        found = await mongo_manager.prediagnosticos_collection.find_one(
            {"prediagnostico_id": test_id}
        )
        
        if found:
            print("✅ Found it!")
            print(f"   _id: {found['_id']}")
            print(f"   prediagnostico_id: {found['prediagnostico_id']}")
            print(f"   user_id: {found['user_id']}")
        else:
            print("❌ Not found!")
            
        # List all records to see what's in the collection
        print(f"\n📋 All records in collection:")
        cursor = mongo_manager.prediagnosticos_collection.find({})
        count = 0
        async for doc in cursor:
            count += 1
            print(f"   Record {count}: prediagnostico_id = {doc.get('prediagnostico_id', 'MISSING')}")
            if count > 5:  # Limit output
                print("   ... (truncated)")
                break
                
        if count == 0:
            print("   (No records found)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await mongo_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(debug_test())