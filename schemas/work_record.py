#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List, Optional


class WorkRecordBase(BaseModel):    
    date: date
    crop_name: str
    crop_variety: Optional[str] = None
    field_number: str
    field_area: float = Field(..., ge=0)
    operation_name: str
    employee_name: str
    tractor_name: str
    license_plate: Optional[str] = None
    implement_name: Optional[str] = None
    area_worked: float = Field(..., gt=0)
    harvest_amount: Optional[float] = None
    fuel_start: float = Field(..., ge=0)
    fuel_refill: float = Field(default=0.0, ge=0)
    fuel_end: float = Field(..., ge=0)


class WorkRecordCreate(WorkRecordBase):
    pass


class WorkRecordResponse(WorkRecordBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    fuel_consumed: Optional[float] = None
    fuel_per_hectare: Optional[float] = None

    @model_validator(mode='after')
    def calculate_fuel(self):
        if self.fuel_consumed is None:
            self.fuel_consumed = round((self.fuel_start - self.fuel_end) + self.fuel_refill, 2)
        if self.fuel_per_hectare is None:
            self.fuel_per_hectare = round(self.fuel_consumed / self.area_worked, 2) if self.area_worked > 0 else 0
        return self
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "date": "2026-03-20",
                "crop_name": "Пшеница",
                "crop_variety": "Сорт 1",
                "field_number": "Поле №5",
                "field_area": 100.0,
                "operation_name": "Вспашка",
                "employee_name": "Иванов И.И.",
                "tractor_name": "John Deere",
                "license_plate": "А001АА",
                "implement_name": "Плуг ПЛН",
                "area_worked": 25.5,
                "harvest_amount": 0,
                "fuel_start": 100.0,
                "fuel_refill": 10.0,
                "fuel_end": 60.0,
                "fuel_consumed": 50.0,
                "fuel_per_hectare": 1.96
            }
        }
    )


class WorkRecordListResponse(BaseModel):
    results: List[WorkRecordResponse]
    total: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [],
                "total": 0
            }
        }
    )
