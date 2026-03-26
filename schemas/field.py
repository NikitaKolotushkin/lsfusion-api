#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class FieldBase(BaseModel):
    name: str = Field(..., description="Наименование поля")
    geometry: Optional[str] = Field(None, description="Геометрия поля в формате WKT или GeoJSON")
    area_ha: float = Field(..., ge=0, description="Площадь поля в гектарах")
    crop_name: Optional[str] = Field(None, description="Текущая культура")
    soil_type: Optional[str] = Field(None, description="Тип почвы")
    current_moisture: float = Field(default=15.0, ge=0, le=100, description="Влажность почвы (%)")
    status: str = Field(default="idle", description="Текущий статус поля")


class FieldCreate(FieldBase):
    pass


class FieldResponse(FieldBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": 101,
                "name": "Северный участок 2",
                "geometry": "POLYGON((30.1 50.1, 30.2 50.1, 30.2 50.2, 30.1 50.2, 30.1 50.1))",
                "area_ha": 45.50,
                "crop_name": "Подсолнечник",
                "soil_type": "Чернозем",
                "current_moisture": 18.5,
                "status": "active",
                "created_at": "2026-03-26T12:00:00",
                "updated_at": "2026-03-26T15:30:00"
            }
        }
    )


class FieldListResponse(BaseModel):
    results: List[FieldResponse]
    total: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [],
                "total": 0
            }
        }
    )
