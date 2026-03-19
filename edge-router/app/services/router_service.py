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
        self.lsf_server_url = os.getenv("LSF_SERVER_URL", "http://server:7651")
        self.lsf_username = os.getenv("LSF_USERNAME", "admin")
        self.lsf_password = os.getenv("LSF_PASSWORD", "")
        
        self.lsf_action_create = os.getenv("LSF_ACTION_CREATE", "createWorkRecord")
        self.lsf_action_get = os.getenv("LSF_ACTION_GET", "getWorkRecords")
        self.lsf_action_get_by_id = os.getenv("LSF_ACTION_GET_BY_ID", "getWorkRecord")
        self.lsf_action_delete = os.getenv("LSF_ACTION_DELETE", "deleteWorkRecord")
        
        self._timeout = 30.0
        self._auth_headers = self._get_auth_headers()
        
        logger.info(f"LSFusion Server: {self.lsf_server_url}")

    def _get_auth_headers(self) -> dict:
        credentials = f"{self.lsf_username}:{self.lsf_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }

    def _map_lsfusion_to_schema(self, lsf_data: dict) -> dict:
        return {
            "id": lsf_data.get("recordId", 0),
            "date": lsf_data.get("date"),
            "crop_name": lsf_data.get("cropName", ""),
            "crop_variety": lsf_data.get("cropSort"),
            "field_number": lsf_data.get("fieldNumber", ""),
            "field_area": lsf_data.get("fieldArea", 0),
            "operation_name": lsf_data.get("operationName", ""),
            "employee_name": lsf_data.get("employeeName", ""),
            "tractor_name": lsf_data.get("tractorBrand", ""),
            "license_plate": lsf_data.get("tractorNumber"),
            "implement_name": lsf_data.get("implementBrand"),
            "area_worked": lsf_data.get("hectares", 0),
            "harvest_amount": lsf_data.get("kgT"),
            "fuel_start": lsf_data.get("remainingOnDeparture", 0),
            "fuel_refill": lsf_data.get("refueling", 0),
            "fuel_end": lsf_data.get("remainingOnReturn", 0),
            "fuel_consumed": lsf_data.get("fuelConsumption"),
            "fuel_per_hectare": lsf_data.get("fuelConsumptionPerHectare"),
        }

    def _calculate_fuel(self, data: dict) -> dict:
        fuel_start = data.get("fuel_start", 0)
        fuel_end = data.get("fuel_end", 0)
        fuel_refill = data.get("fuel_refill", 0)
        area_worked = data.get("area_worked", 1)
        
        fuel_consumed = data.get("fuel_consumed")
        if fuel_consumed is None:
            fuel_consumed = round((fuel_start - fuel_end) + fuel_refill, 2)
            data["fuel_consumed"] = fuel_consumed
        
        fuel_per_hectare = data.get("fuel_per_hectare")
        if fuel_per_hectare is None and area_worked > 0:
            fuel_per_hectare = round(fuel_consumed / area_worked, 2)
            data["fuel_per_hectare"] = fuel_per_hectare
        
        return data

    async def _request(self, method: str, action: str, params: dict | None = None) -> Any:
        url = f"{self.lsf_server_url}/exec?action={action}"
        
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            if method == "GET":
                response = await client.get(url, headers=self._auth_headers)
            elif method == "POST":
                response = await client.post(url, json=params, headers=self._auth_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                logger.error("LSFusion authentication failed")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверные учётные данные LSFusion"
                )
            
            if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                logger.error(f"LSFusion error: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка LSFusion: {response.text}"
                )
            
            response.raise_for_status()
            
            try:
                return response.json()
            except Exception:
                return response.text

    async def create_work_record(self, work_record: schemas_work_record.WorkRecordCreate) -> dict:
        params = {
            "p_date": work_record.date.isoformat(),
            "p_crop_name": work_record.crop_name,
            "p_crop_variety": work_record.crop_variety or "",
            "p_field_number": work_record.field_number,
            "p_field_area": work_record.field_area,
            "p_operation_name": work_record.operation_name,
            "p_employee_name": work_record.employee_name,
            "p_tractor_name": work_record.tractor_name,
            "p_license_plate": work_record.license_plate or "",
            "p_implement_name": work_record.implement_name or "",
            "p_area_worked": work_record.area_worked,
            "p_harvest_amount": work_record.harvest_amount or 0,
            "p_fuel_start": work_record.fuel_start,
            "p_fuel_refill": work_record.fuel_refill,
            "p_fuel_end": work_record.fuel_end,
        }

        logger.debug(f"Creating work record: {params}")
        
        result = await self._request("POST", self.lsf_action_create, params)
        record_id = result.get("id", 0) if isinstance(result, dict) else 0
        
        response_data = {
            "id": record_id,
            **work_record.model_dump(),
            "created_at": None,
            "updated_at": None,
        }
        
        return self._calculate_fuel(response_data)

    async def get_all_work_records(self) -> dict:
        logger.debug("Fetching all work records")
        
        result = await self._request("GET", self.lsf_action_get)
        
        items_raw = result.get("r", []) if isinstance(result, dict) else result
        
        items = [self._map_lsfusion_to_schema(item) for item in items_raw]
        
        items = [self._calculate_fuel(item) for item in items]
        
        return {
            "items": items,
            "total": len(items)
        }

    async def get_work_record(self, record_id: int) -> dict:
        logger.debug(f"Fetching work record {record_id}")
        
        result = await self._request("GET", self.lsf_action_get_by_id, {"p_id": record_id})
        
        if isinstance(result, dict):
            data = result.get("r", result)
        else:
            data = result
        
        if not data or data.get("recordId") is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись не найдена"
            )
        
        mapped_data = self._map_lsfusion_to_schema(data)
        return self._calculate_fuel(mapped_data)
        
    async def update_work_record(self, record_id: int, work_record: schemas_work_record.WorkRecordCreate) -> dict:
        
        # пока не сделал

        logger.warning(f"Update not implemented for record {record_id}")
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Обновление не реализовано в LSFusion"
        )

    async def delete_work_record(self, record_id: int) -> dict:
        logger.debug(f"Deleting work record {record_id}")
        
        result = await self._request("GET", self.lsf_action_delete, {"p_id": record_id})
        
        if isinstance(result, dict) and result.get("status") != "Deleted":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись не найдена"
            )
        
        return {"status": "deleted", "id": record_id}
