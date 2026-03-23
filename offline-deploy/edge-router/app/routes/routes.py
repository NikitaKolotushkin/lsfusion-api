#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import app.schemas.work_record as schemas_work_record

from httpx import HTTPStatusError
from fastapi import APIRouter, HTTPException, Request, Response

from app.services.router_service import RouterService


router = APIRouter()
router_service = RouterService()


@router.post('/work-records/', response_model=schemas_work_record.WorkRecordResponse, status_code=201)
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


@router.get('/work-records/', response_model=schemas_work_record.WorkRecordListResponse)
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


@router.get('/work-records/{record_id}', response_model=schemas_work_record.WorkRecordResponse)
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


@router.put('/work-records/{record_id}', response_model=schemas_work_record.WorkRecordResponse)
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


@router.delete('/work-records/{record_id}', status_code=204)
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
