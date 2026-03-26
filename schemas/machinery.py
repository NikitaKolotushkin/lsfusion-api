#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class VehicleFunctionalClass(str, Enum):
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"


class VehicleTechType(str, Enum):
    TES = "ТЭС"
    STK = "СТК"
    AMO = "АМО"
    RBS = "РБС"


class MachineryBase(BaseModel):
    id: str = Field(..., description="Уникальный строковый ID (строка 50)")
    inventory_number: Optional[str] = Field(None, description="Инвентарный номер")
    model_name: str = Field(..., description="Наименование модели")
    manufacturer: Optional[str] = None
    
    f_class: VehicleFunctionalClass = Field(..., description="Функциональный класс (M1, M2, M3)")
    t_type: VehicleTechType = Field(..., description="Технологический тип (ТЭС, СТК, АМО, РБС)")
    
    traction_class_ts: Optional[float] = Field(None, ge=0)
    engine_power_hp: Optional[int] = Field(None, ge=0)
    operating_weight_t: Optional[float] = Field(None, ge=0)
    working_width_m: Optional[float] = Field(None, ge=0)
    
    hopper_volume_m3: Optional[float] = Field(None, ge=0)
    max_throughput_kg_s: Optional[float] = Field(None, ge=0)
    payload_capacity_t: Optional[float] = Field(None, ge=0)

    current_status: Optional[str] = "ready"
    total_operating_hours: Optional[float] = Field(default=0.0, ge=0)
    current_lat: Optional[float] = None
    current_lon: Optional[float] = None
    current_fuel_level_percent: Optional[float] = Field(default=0.0, ge=0, le=100) 
    
    vibration_threshold_ms2: Optional[float] = 40.0
    predicted_failure_prob: Optional[float] = Field(default=0.0, ge=0, le=1.0)
    isobus_enabled: Optional[bool] = False 
    
    last_telemetry_sync: Optional[datetime] = None


class MachineryCreate(MachineryBase):
    pass


class MachineryResponse(MachineryBase):
    lsf_id: Optional[int] = Field(None, alias="lsf_id")
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "TRACTOR-001",
                "inventory_number": "ИНВ-7788",
                "model_name": "John Deere 8R",
                "manufacturer": "John Deere",
                "f_class": "M1",
                "t_type": "ТЭС",
                "traction_class_ts": 5.0,
                "engine_power_hp": 340,
                "operating_weight_t": 14.5,
                "working_width_m": 0.0,
                "current_status": "active",
                "total_operating_hours": 1250.5,
                "current_fuel_level_percent": 85.5,
                "predicted_failure_prob": 0.05,
                "isobus_enabled": True,
                "updated_at": "2026-03-26T15:00:00"
            }
        }
    )


class MachineryListResponse(BaseModel):
    results: List[MachineryResponse]
    total: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [],
                "total": 0
            }
        }
    )
