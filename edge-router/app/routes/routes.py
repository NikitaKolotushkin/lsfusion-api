#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import app.schemas.work_record as schemas_work_record
import app.schemas.field as schemas_field

from httpx import HTTPStatusError
from fastapi import APIRouter, HTTPException, Request, Response

from app.services.router_service import RouterService


router = APIRouter()
router_service = RouterService()


# WORK RECORDS

@router.post('/work-records/', response_model=schemas_work_record.WorkRecordResponse, status_code=201, tags=["Work Records"])
async def create_work_record(request: Request, work_record: schemas_work_record.WorkRecordCreate):
    try:
        record_data = await router_service.create_work_record(work_record)
        return record_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/work-records/', response_model=schemas_work_record.WorkRecordListResponse, tags=["Work Records"])
async def get_work_records(request: Request):
    try:
        records_data = await router_service.get_all_work_records()
        return records_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/work-records/{record_id}', response_model=schemas_work_record.WorkRecordResponse, tags=["Work Records"])
async def get_work_record(request: Request, record_id: int):
    try:
        record_data = await router_service.get_work_record(record_id)
        return record_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/work-records/{record_id}', response_model=schemas_work_record.WorkRecordResponse, tags=["Work Records"])
async def update_work_record(request: Request, record_id: int, work_record: schemas_work_record.WorkRecordCreate):
    try:
        record_data = await router_service.update_work_record(record_id, work_record)
        return record_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/work-records/{record_id}', status_code=204, tags=["Work Records"])
async def delete_work_record(request: Request, record_id: int):
    try:
        await router_service.delete_work_record(record_id)
        return Response(status_code=204)
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# FIELDS

@router.post('/fields/', response_model=schemas_field.FieldResponse, status_code=201, tags=["Fields"])
async def create_field(request: Request, field: schemas_field.FieldCreate):
    try:
        field_data = await router_service.create_field(field)
        return field_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/fields/', response_model=schemas_field.FieldListResponse, tags=["Fields"])
async def get_fields(request: Request):
    try:
        fields_data = await router_service.get_all_fields()
        return fields_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/fields/{field_id}', response_model=schemas_field.FieldResponse, tags=["Fields"])
async def get_field(request: Request, field_id: int):
    try:
        field_data = await router_service.get_field(field_id)
        return field_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/fields/{field_id}', response_model=schemas_field.FieldResponse, tags=["Fields"])
async def update_field(request: Request, field_id: int, field: schemas_field.FieldCreate):
    try:
        field_data = await router_service.update_field(field_id, field)
        return field_data
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/fields/{field_id}', status_code=204, tags=["Fields"])
async def delete_field(request: Request, field_id: int):
    try:
        await router_service.delete_field(field_id)
        return Response(status_code=204)
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
