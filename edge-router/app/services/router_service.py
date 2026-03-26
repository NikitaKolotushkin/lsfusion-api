#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import httpx
import base64
import logging
from typing import Any, Optional

import app.schemas.work_record as schemas_work_record
import app.schemas.field as schemas_field
import app.schemas.machinery as schemas_machinery  # Новый импорт
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class RouterService:
    def __init__(self):
        self.lsf_server_url = os.getenv("LSF_SERVER_URL", "http://server:7651").rstrip("/")
        self.lsf_username = os.getenv("LSF_USERNAME", "admin")
        self.lsf_password = os.getenv("LSF_PASSWORD", "")
        
        self.agro_module = os.getenv("LSF_AGRO_MODULE", "Agro")
        self.fields_module = os.getenv("LSF_FIELDS_MODULE", "Fields")
        self.machinery_module = os.getenv("LSF_MACHINERY_MODULE", "Machinery")
        
        self._timeout = 30.0
        self._auth_headers = self._get_auth_headers()
        
        logger.info(f"LSFusion Server: {self.lsf_server_url}")

    def _get_auth_headers(self) -> dict:
        credentials = f"{self.lsf_username}:{self.lsf_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def _map_lsfusion_to_work_schema(self, item: dict) -> dict:
        return {
            "id": item.get("recordId"),
            "date": item.get("date"),
            "crop_name": item.get("cropName"),
            "crop_variety": item.get("cropSort"),
            "field_number": item.get("fieldNumber"),
            "field_area": item.get("fieldArea"),
            "operation_name": item.get("operationName"),
            "employee_name": item.get("employeeName"),
            "tractor_name": item.get("tractorBrand"),
            "license_plate": item.get("tractorNumber"),
            "implement_name": item.get("implementBrand"),
            "area_worked": item.get("hectares"),
            "harvest_amount": item.get("kgT"),
            "fuel_start": item.get("remainingOnDeparture"),
            "fuel_refill": item.get("refueling"),
            "fuel_end": item.get("remainingOnReturn"),
            "fuel_consumed": item.get("fuelConsumption"),
            "fuel_per_hectare": item.get("fuelConsumptionPerHectare"),
        }

    def _map_lsfusion_to_field_schema(self, item: dict) -> dict:
        return {
            "id": item.get("fieldId"),
            "name": item.get("name"),
            "geometry": item.get("geometry"),
            "area_ha": item.get("areaHa"),
            "crop_name": item.get("cropName"),
            "soil_type": item.get("soilType"),
            "current_moisture": item.get("currentMoisture"),
            "status": item.get("status"),
            "created_at": item.get("createdAt"),
            "updated_at": item.get("updatedAt"),
        }

    def _map_lsfusion_to_machinery_schema(self, item: dict) -> dict:
        return {
            "id": item.get("id"),
            "inventory_number": item.get("inventoryNumber"),
            "model_name": item.get("modelName"),
            "manufacturer": item.get("manufacturer"),
            "f_class": item.get("functionalClassName"),
            "t_type": item.get("techTypeName"),
            "traction_class_ts": item.get("tractionClassTs"),
            "engine_power_hp": item.get("enginePowerHp"),
            "operating_weight_t": item.get("operatingWeightT"),
            "working_width_m": item.get("workingWidthM"),
            "hopper_volume_m3": item.get("hopperVolumeM3"),
            "max_throughput_kg_s": item.get("maxThroughputKgS"),
            "payload_capacity_t": item.get("payloadCapacityT"),
            
            "current_status": item.get("currentStatus") or "ready",
            "total_operating_hours": item.get("totalOperatingHours") or 0.0,
            "current_fuel_level_percent": item.get("currentFuelLevelPercent") or 0.0,
            "isobus_enabled": True if item.get("isobusEnabled") else False,
            
            "current_lat": item.get("currentLat"),
            "current_lon": item.get("currentLon"),
            "vibration_threshold_ms2": item.get("vibrationThresholdMs2") or 40.0,
            "predicted_failure_prob": item.get("predictedFailureProb") or 0.0,
            "last_telemetry_sync": item.get("lastTelemetrySync"),
            "updated_at": item.get("updatedAt"),
            "lsf_id": item.get("machineryInternalId") 
        }

    def _calculate_fuel(self, data: dict) -> dict:
        if data.get("fuel_consumed") is None:
            f_start = data.get("fuel_start") or 0
            f_end = data.get("fuel_end") or 0
            f_refill = data.get("fuel_refill") or 0
            data["fuel_consumed"] = round((f_start - f_end) + f_refill, 2)
        
        if data.get("fuel_per_hectare") is None or data.get("fuel_per_hectare") == 0:
            worked = data.get("area_worked") or 1
            if worked > 0:
                data["fuel_per_hectare"] = round(data["fuel_consumed"] / worked, 2)
        return data

    async def _request(self, action: str, params: dict | None = None, module: str = None) -> Any:
        target_module = module or self.agro_module
        url = f"{self.lsf_server_url}/exec"
        query_params = {"action": f"{target_module}.{action}"}
        
        if params:
            query_params.update(params)
        
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, params=query_params, headers=self._auth_headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"LSF Error: {response.text}")
            return response.json() if response.text.strip() else {}

    # WORK RECORDS

    async def create_work_record(self, work_record: schemas_work_record.WorkRecordCreate) -> dict:
        params = {
            "p_date": work_record.date.strftime("%d.%m.%Y"),
            "p_crop_name": work_record.crop_name,
            "p_crop_variety": work_record.crop_variety or "",
            "p_field_number": work_record.field_number,
            "p_field_area": str(work_record.field_area),
            "p_operation_name": work_record.operation_name,
            "p_employee_name": work_record.employee_name,
            "p_tractor_name": work_record.tractor_name,
            "p_license_plate": work_record.license_plate or "",
            "p_implement_name": work_record.implement_name or "",
            "p_area_worked": str(work_record.area_worked),
            "p_harvest_amount": str(work_record.harvest_amount or 0),
            "p_fuel_start": str(work_record.fuel_start),
            "p_fuel_refill": str(work_record.fuel_refill),
            "p_fuel_end": str(work_record.fuel_end),
        }
        result = await self._request("createWorkRecord", params, module=self.agro_module)
        response_data = {"id": result.get("id", 0), **work_record.model_dump()}
        return self._calculate_fuel(response_data)

    async def get_all_work_records(self) -> dict:
        result = await self._request("getWorkRecords", module=self.agro_module)
        items_raw = result.get("r", [])
        items = [self._calculate_fuel(self._map_lsfusion_to_work_schema(item)) for item in items_raw if item.get("recordId")]
        return {"results": items, "total": len(items)}

    async def get_work_record(self, record_id: int) -> dict:
        result = await self._request("getWorkRecord", {"p_id": record_id}, module=self.agro_module)
        items = result.get("r", [])
        if not items:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        return self._calculate_fuel(self._map_lsfusion_to_work_schema(items[0]))

    async def delete_work_record(self, record_id: int) -> dict:
        await self._request("deleteWorkRecord", {"r": record_id}, module=self.agro_module)
        return {"status": "deleted", "id": record_id}

    async def update_work_record(self, record_id: int, work_record: schemas_work_record.WorkRecordCreate) -> dict:
        return await self.create_work_record(work_record)

    # FIELDS

    async def create_field(self, field: schemas_field.FieldCreate) -> dict:
        params = {
            "p_name": field.name,
            "p_area": str(field.area_ha),
            "p_geometry": field.geometry or "",
            "p_crop": field.crop_name or "",
            "p_soil": field.soil_type or "",
            "p_moisture": str(field.current_moisture),
        }
        result = await self._request("createField", params, module=self.fields_module)
        return {"id": result.get("id", 0), **field.model_dump()}

    async def get_all_fields(self) -> dict:
        result = await self._request("getFields", module=self.fields_module)
        items_raw = result.get("f", [])
        items = [self._map_lsfusion_to_field_schema(item) for item in items_raw if item.get("fieldId")]
        return {"results": items, "total": len(items)}

    async def get_field(self, field_id: int) -> dict:
        result = await self._request("getField", {"p_id": field_id}, module=self.fields_module)
        items = result.get("f", [])
        if not items:
            raise HTTPException(status_code=404, detail="Поле не найдено")
        return self._map_lsfusion_to_field_schema(items[0])

    async def delete_field(self, field_id: int) -> dict:
        await self._request("deleteField", {"f": field_id}, module=self.fields_module)
        return {"status": "deleted", "id": field_id}

    async def update_field(self, field_id: int, field: schemas_field.FieldCreate) -> dict:
        return await self.create_field(field)

    # MACHINERY

    async def create_machinery(self, machinery: schemas_machinery.MachineryCreate) -> dict:
        params = {
            "p_id": machinery.id,
            "p_inv": machinery.inventory_number or "",
            "p_model": machinery.model_name,
            "p_f_class": machinery.f_class.value if machinery.f_class else "",
            "p_t_type": machinery.t_type.value if machinery.t_type else ""
        }

        result = await self._request("createMachinery", params, module=self.machinery_module)
        
        return {
            "lsf_id": result.get("lsf_id", 0),
            **machinery.model_dump()
        }

    async def get_all_machinery(self) -> dict:
        result = await self._request("getMachineries", module=self.machinery_module) # Предполагаем имя действия в LSF
        items_raw = result.get("m", [])
        items = [self._map_lsfusion_to_machinery_schema(item) for item in items_raw if item.get("id")]
        return {"results": items, "total": len(items)}

    async def get_machinery(self, machinery_id: str) -> dict:
        result = await self._request("getMachinery", {"p_id": machinery_id}, module=self.machinery_module)
        items = result.get("m", [])
        if not items:
            raise HTTPException(status_code=404, detail="Техника не найдена")
        return self._map_lsfusion_to_machinery_schema(items[0])

    async def delete_machinery(self, machinery_id: str) -> dict:
        await self._request("deleteMachinery", {"p_id": machinery_id}, module=self.machinery_module)
        return {"status": "deleted", "id": machinery_id}

    async def update_machinery(self, machinery_id: str, machinery: schemas_machinery.MachineryCreate) -> dict:
        return await self.create_machinery(machinery)
