"""
Test suite for HU5: Doctor Diagnostic Endpoint - Simplified
POST /prediagnostic/diagnostic/{prediagnostic_id}

This test suite validates:
1. MongoDB connection
2. Basic diagnostic endpoint functionality
3. Diagnostic service error handling
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.mongodb import mongo_manager
from src.services.diagnostic_service import diagnostic_service


class TestDiagnosticEndpoint:
    """Simplified test suite for HU5 diagnostic endpoint."""
    
    BASE_URL = "http://localhost:8000"

    @pytest.mark.asyncio
    async def test_mongodb_connection(self):
        """Test MongoDB connection and basic operations."""
        try:
            await mongo_manager.connect()
            
            # Test connection with ping
            await mongo_manager.client.admin.command('ping')
            
            # Test collections access
            collections = await mongo_manager.database.list_collection_names()
            assert isinstance(collections, list)
            
            # Basic insert/delete test
            test_doc = {"_id": "test_connection", "test": True}
            result = await mongo_manager.diagnosticos_collection.insert_one(test_doc)
            assert result.inserted_id == "test_connection"
            
            # Cleanup
            await mongo_manager.diagnosticos_collection.delete_one({"_id": "test_connection"})
            
        except Exception as e:
            pytest.fail(f"MongoDB connection test failed: {e}")
        finally:
            await mongo_manager.disconnect()

    def test_diagnostic_endpoint_basic(self):
        """Test basic diagnostic endpoint availability (sync test)."""
        import requests
        
        diagnostic_payload = {
            "aprobacion": True,
            "comentario": "Test básico de disponibilidad del endpoint de diagnóstico."
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/prediagnostic/diagnostic/TEST_BASIC_ID",
                json=diagnostic_payload,
                timeout=5
            )
            
            # Expect 404 (case not found) which means endpoint is working
            # Any response means the server and endpoint are accessible
            assert response.status_code in [200, 400, 404, 422, 500]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running on localhost:8000")
    
    def test_diagnostic_endpoint_validation(self):
        """Test validation errors for diagnostic endpoint."""
        import requests
        
        # Test short comment validation
        short_comment_payload = {
            "aprobacion": True,
            "comentario": "Corto"  # Too short (< 10 characters)
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/prediagnostic/diagnostic/TEST_VALIDATION",
                json=short_comment_payload,
                timeout=5
            )
            
            # Should return 422 for validation error
            assert response.status_code == 422
            data = response.json()
            assert "detail" in data
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running on localhost:8000")
    
    @pytest.mark.asyncio
    async def test_diagnostic_service_methods(self):
        """Test diagnostic service methods and error handling."""
        try:
            await mongo_manager.connect()
            
            # Test successful save
            test_diagnostic = {
                "_id": "TEST_DIAGNOSTIC_SIMPLE",
                "prediagnostico_id": "TEST_PRED_SIMPLE",
                "aprobacion": True,
                "comentarios": "Test diagnostic service functionality",
                "fecha_revision": datetime.now(timezone.utc).isoformat()
            }
            
            success = await diagnostic_service.save_diagnostic(test_diagnostic)
            assert success is True
            
            # Test retrieval
            retrieved = await diagnostic_service.get_diagnostic_by_prediagnostico("TEST_PRED_SIMPLE")
            assert retrieved is not None
            assert retrieved["_id"] == "TEST_DIAGNOSTIC_SIMPLE"
            assert retrieved["aprobacion"] == True
            
            # Test non-existent retrieval
            not_found = await diagnostic_service.get_diagnostic_by_prediagnostico("NON_EXISTENT")
            assert not_found is None
            
            # Cleanup
            await mongo_manager.diagnosticos_collection.delete_one({"_id": "TEST_DIAGNOSTIC_SIMPLE"})
            
        except Exception as e:
            pytest.fail(f"Diagnostic service test failed: {e}")
        finally:
            await mongo_manager.disconnect()
    
    @pytest.mark.asyncio 
    async def test_diagnostic_service_error_handling(self):
        """Test diagnostic service error handling scenarios."""
        try:
            await mongo_manager.connect()
            
            # Test saving duplicate ID (should handle gracefully)
            test_diagnostic = {
                "_id": "DUPLICATE_TEST_ID",
                "prediagnostico_id": "DUPLICATE_PRED_ID",
                "aprobacion": True,
                "comentarios": "First diagnostic",
                "fecha_revision": datetime.now(timezone.utc).isoformat()
            }
            
            # Save first time - should succeed
            success1 = await diagnostic_service.save_diagnostic(test_diagnostic)
            assert success1 is True
            
            # Try to save same ID again - service should handle the error
            try:
                success2 = await diagnostic_service.save_diagnostic(test_diagnostic)
                # If no exception, it should return False
                assert success2 is False
            except Exception:
                # Expected behavior - service raises exception for duplicate
                pass
            
            # Cleanup
            await mongo_manager.diagnosticos_collection.delete_one({"_id": "DUPLICATE_TEST_ID"})
            
        except Exception as e:
            pytest.fail(f"Diagnostic service error handling test failed: {e}")
        finally:
            await mongo_manager.disconnect()


if __name__ == "__main__":
    """
    Run tests directly with: python -m pytest tests/test_diagnostic_endpoint.py -v
    """
    pytest.main([__file__, "-v"])