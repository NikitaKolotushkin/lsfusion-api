#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import httpx
import base64
import logging
from typing import Any

import app.schemas.work_record as schemas_work_record
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class RouterService:
    def __init__(self):
        self.lsf_server_url = os.getenv("LSF_SERVER_URL", "http://server:7651").rstrip("/")
        self.lsf_username = os.getenv("LSF_USERNAME", "admin")
        self.lsf_password = os.getenv("LSF_PASSWORD", "")
        
        self.lsf_module = os.getenv("LSF_MODULE", "Agro")
        self._timeout = 30.0
        self._auth_headers = self._get_auth_headers()
        
        logger.info(f"LSFusion Server: {self.lsf_server_url} (Module: {self.lsf_module})")

    def _get_auth_headers(self) -> dict:
        credentials = f"{self.lsf_username}:{self.lsf_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def _map_lsfusion_to_schema(self, item: dict) -> dict:
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

    async def _request(self, action: str, params: dict | None = None) -> Any:
        url = f"{self.lsf_server_url}/exec"
        query_params = {"action": f"{self.lsf_module}.{action}"}
        if params:
            query_params.update(params)
        
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, params=query_params, headers=self._auth_headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"LSF Error: {response.text}")
            return response.json() if response.text.strip() else {}

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
        result = await self._request("createWorkRecord", params)

        response_data = {
            "id": result.get("id", 0),
            **work_record.model_dump(),
        }
        return self._calculate_fuel(response_data)

    async def get_all_work_records(self) -> dict:
        result = await self._request("getWorkRecords")
        items_raw = result.get("r", [])
        items = [self._calculate_fuel(self._map_lsfusion_to_schema(item)) for item in items_raw if item.get("recordId")]
        return {"results": items, "total": len(items)}

    async def get_work_record(self, record_id: int) -> dict:
        result = await self._request("getWorkRecord", {"p_id": record_id})
        items = result.get("r", [])
        if not items:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        
        return self._calculate_fuel(self._map_lsfusion_to_schema(items[0]))

    async def delete_work_record(self, record_id: int) -> dict:
        await self._request("deleteWorkRecord", {"p_id": record_id})
        return {"status": "deleted", "id": record_id}
