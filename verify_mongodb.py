"""
Script para verificar conexión y operaciones básicas de MongoDB.
Ejecutar: python verify_mongodb.py
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Configuración MongoDB (ajustar según tu .env)
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "prediagnosticdb")

async def verify_mongodb_connection():
    """Verificar conexión y operaciones básicas de MongoDB"""
    try:
        print("🔄 Conectando a MongoDB...")
        
        # Crear cliente MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DATABASE_NAME]
        
        # Test 1: Ping servidor
        await client.admin.command('ping')
        print("✅ Conexión a MongoDB exitosa")
        
        # Test 2: Listar colecciones
        collections = await db.list_collection_names()
        print(f"📁 Colecciones disponibles: {collections}")
        

        # Test 3: Acceder a colecciones necesarias
        prediagnosticos_collection = db.prediagnosticos
        diagnosticos_collection = db.diagnosticos

        # Test 4: Contar documentos existentes
        pred_count = await prediagnosticos_collection.count_documents({})
        diag_count = await diagnosticos_collection.count_documents({})

        print(f"📊 Documentos en prediagnosticos: {pred_count}")
        print(f"📊 Documentos en diagnosticos: {diag_count}")

        # Test 5: Insertar documento de prueba (y eliminarlo)
        test_diagnostic = {
            "_id": "TEST_DIAGNOSTIC_123",
            "prediagnostic_id": "TEST_PRED_123",
            "approval": True,
            "comments": "Test de conectividad",
            "review_date": "2025-01-01T00:00:00"
        }

        # Insertar
        result = await diagnosticos_collection.insert_one(test_diagnostic)
        print(f"✅ Test insert exitoso: {result.inserted_id}")

        # Consultar
        found = await diagnosticos_collection.find_one({"_id": "TEST_DIAGNOSTIC_123"})
        if found:
            print("✅ Test query exitoso")

        # Eliminar documento de prueba
        delete_result = await diagnosticos_collection.delete_one({"_id": "TEST_DIAGNOSTIC_123"})
        print(f"✅ Test delete exitoso: {delete_result.deleted_count} documento eliminado")
        
        print("\n🎉 Todas las operaciones MongoDB funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión MongoDB: {str(e)}")
        print(f"🔧 Verificar que MongoDB esté ejecutándose en: {MONGO_URL}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()

async def create_sample_prediagnostico():
    """Crear un prediagnóstico de ejemplo para testing"""
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DATABASE_NAME]
        prediagnosticos_collection = db.prediagnosticos
        
        sample_prediagnostico = {
            "prediagnostic_id": "P20250927123456",
            "radiografia_id": "RAD20250927123456",
            "user_id": "U456",
            "resultado_modelo": {
                "probabilidad_neumonia": 0.87,
                "etiqueta": "posible_neumonia",
                "fecha_procesamiento": "2025-09-27T10:00:00Z"
            },
            "estado": "Procesado",
            "fecha_subida": "2025-09-27T09:00:00Z",
            "paciente_nombre": "Juan Pérez Test"
        }
        
        # Verificar si ya existe
        existing = await prediagnosticos_collection.find_one(
            {"prediagnostic_id": sample_prediagnostico["prediagnostic_id"]}
        )
        
        if not existing:
            result = await prediagnosticos_collection.insert_one(sample_prediagnostico)
            print(f"✅ Prediagnóstico de prueba creado: {sample_prediagnostico['prediagnostic_id']}")
        else:
            print(f"ℹ️  Prediagnóstico de prueba ya existe: {sample_prediagnostico['prediagnostic_id']}")
            
        return sample_prediagnostico["prediagnostic_id"]
        
    except Exception as e:
        print(f"❌ Error creando prediagnóstico de prueba: {str(e)}")
        return None
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    print("🧪 Verificación de MongoDB para HU5")
    print("=" * 50)
    
    # Test básico de conexión
    connection_ok = asyncio.run(verify_mongodb_connection())
    
    if connection_ok:
        print("\n📝 Creando datos de prueba...")
        test_id = asyncio.run(create_sample_prediagnostico())
        if test_id:
            print(f"\n🔬 Puedes probar tu endpoint con prediagnostic_id: {test_id}")
    else:
        print("\n❌ Conexión fallida. Revisar configuración de MongoDB.")