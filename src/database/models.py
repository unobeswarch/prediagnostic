"""
Database models for MongoDB collections matching the real schema.
"""
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod 
    def validate(cls, v: Any, _: Any = None) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        """Pydantic v2 JSON schema method."""
        return {"type": "string", "format": "objectid"}


class ResultadoModelo(BaseModel):
    """Resultado del modelo de IA."""
    probabilidad_neumonia: float = Field(..., ge=0.0, le=1.0)
    etiqueta: str  # "No Pneumonia", "Viral Pneumonia", "Bacterial Pneumonia"


class Prediagnostico(BaseModel):
    """Modelo para la colección prediagnosticos."""
    user_id: str  # unique username
    prediagnostico_id: str
    radiografia_url: str
    resultado_modelo: ResultadoModelo
    fecha_procesamiento: datetime = Field(default_factory=datetime.utcnow)
    estado: str = "procesado"  # "procesado" o "validado"
    fecha_subida: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class Diagnostico(BaseModel):
    """Modelo para la colección diagnosticos."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    prediagnostico_id: str  # FK to prediagnosticos
    etiqueta: str  # "aprobo" o "no aprobo"
    comentario: str
    fecha_revision: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class DiagnosticoCreate(BaseModel):
    """Modelo para crear un diagnóstico."""
    prediagnostico_id: str
    etiqueta: str  # "aprobo" o "no aprobo"
    comentario: str


class PrediagnosticoCreate(BaseModel):
    """Modelo para crear un prediagnóstico."""
    user_id: str
    radiografia_url: str
    resultado_modelo: ResultadoModelo