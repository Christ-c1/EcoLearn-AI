import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.carbon_metrics import Carbon_metricsService
from dependencies.auth import get_current_user
from schemas.auth import UserResponse

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/carbon_metrics", tags=["carbon_metrics"])


# ---------- Pydantic Schemas ----------
class Carbon_metricsData(BaseModel):
    """Entity data schema (for create/update)"""
    learning_path_id: int = None
    session_duration: int = None
    carbon_footprint: float = None
    device_type: str = None
    energy_consumed: float = None
    trees_contribution: float = None
    session_date: Optional[datetime] = None
    created_at: Optional[datetime] = None


class Carbon_metricsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    learning_path_id: Optional[int] = None
    session_duration: Optional[int] = None
    carbon_footprint: Optional[float] = None
    device_type: Optional[str] = None
    energy_consumed: Optional[float] = None
    trees_contribution: Optional[float] = None
    session_date: Optional[datetime] = None
    created_at: Optional[datetime] = None


class Carbon_metricsResponse(BaseModel):
    """Entity response schema"""
    id: int
    user_id: int
    learning_path_id: Optional[int] = None
    session_duration: Optional[int] = None
    carbon_footprint: Optional[float] = None
    device_type: Optional[str] = None
    energy_consumed: Optional[float] = None
    trees_contribution: Optional[float] = None
    session_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Carbon_metricsListResponse(BaseModel):
    """List response schema"""
    items: List[Carbon_metricsResponse]
    total: int
    skip: int
    limit: int


class Carbon_metricsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[Carbon_metricsData]


class Carbon_metricsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: Carbon_metricsUpdateData


class Carbon_metricsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[Carbon_metricsBatchUpdateItem]


class Carbon_metricsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


def get_user_id_as_int(current_user: UserResponse) -> int:
    """Convert user_id to int, handling both str and int types"""
    try:
        return int(current_user.id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid user ID format")


# ---------- Routes ----------
@router.get("", response_model=Carbon_metricsListResponse)
async def query_carbon_metricss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query carbon_metricss with filtering, sorting, and pagination (user can only see their own records)"""
    logger.debug(f"Querying carbon_metricss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    user_id = get_user_id_as_int(current_user)
    service = Carbon_metricsService(db)
    try:
        # Parse query JSON if provided
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")
        
        result = await service.get_list(
            skip=skip, 
            limit=limit,
            query_dict=query_dict,
            sort=sort,
            user_id=user_id,
        )
        logger.debug(f"Found {result['total']} carbon_metricss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying carbon_metricss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=Carbon_metricsListResponse)
async def query_carbon_metricss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query carbon_metricss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying carbon_metricss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = Carbon_metricsService(db)
    try:
        # Parse query JSON if provided
        query_dict = None
        if query:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid query JSON format")

        result = await service.get_list(
            skip=skip,
            limit=limit,
            query_dict=query_dict,
            sort=sort
        )
        logger.debug(f"Found {result['total']} carbon_metricss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying carbon_metricss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=Carbon_metricsResponse)
async def get_carbon_metrics(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single carbon_metrics by ID (user can only see their own records)"""
    logger.debug(f"Fetching carbon_metrics with id: {id}, fields={fields}")
    
    user_id = get_user_id_as_int(current_user)
    service = Carbon_metricsService(db)
    try:
        result = await service.get_by_id(id, user_id=user_id)
        if not result:
            logger.warning(f"Carbon_metrics with id {id} not found")
            raise HTTPException(status_code=404, detail="Carbon_metrics not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching carbon_metrics {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=Carbon_metricsResponse, status_code=201)
async def create_carbon_metrics(
    data: Carbon_metricsData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new carbon_metrics"""
    logger.debug(f"Creating new carbon_metrics with data: {data}")
    
    user_id = get_user_id_as_int(current_user)
    service = Carbon_metricsService(db)
    try:
        result = await service.create(data.model_dump(), user_id=user_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create carbon_metrics")
        
        logger.info(f"Carbon_metrics created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating carbon_metrics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating carbon_metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[Carbon_metricsResponse], status_code=201)
async def create_carbon_metricss_batch(
    request: Carbon_metricsBatchCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create multiple carbon_metricss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} carbon_metricss")
    
    user_id = get_user_id_as_int(current_user)
    service = Carbon_metricsService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump(), user_id=user_id)
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} carbon_metricss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[Carbon_metricsResponse])
async def update_carbon_metricss_batch(
    request: Carbon_metricsBatchUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update multiple carbon_metricss in a single request (requires ownership)"""
    logger.debug(f"Batch updating {len(request.items)} carbon_metricss")
    
    user_id = get_user_id_as_int(current_user)
    service = Carbon_metricsService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict, user_id=user_id)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} carbon_metricss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=Carbon_metricsResponse)
async def update_carbon_metrics(
    id: int,
    data: Carbon_metricsUpdateData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing carbon_metrics (requires ownership)"""
    logger.debug(f"Updating carbon_metrics {id} with data: {data}")

    user_id = get_user_id_as_int(current_user)
    service = Carbon_metricsService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict, user_id=user_id)
        if not result:
            logger.warning(f"Carbon_metrics with id {id} not found for update")
            raise HTTPException(status_code=404, detail="Carbon_metrics not found")
        
        logger.info(f"Carbon_metrics {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating carbon_metrics {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating carbon_metrics {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_carbon_metricss_batch(
    request: Carbon_metricsBatchDeleteRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple carbon_metricss by their IDs (requires ownership)"""
    logger.debug(f"Batch deleting {len(request.ids)} carbon_metricss")
    
    user_id = get_user_id_as_int(current_user)
    service = Carbon_metricsService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id, user_id=user_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} carbon_metricss successfully")
        return {"message": f"Successfully deleted {deleted_count} carbon_metricss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_carbon_metrics(
    id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single carbon_metrics by ID (requires ownership)"""
    logger.debug(f"Deleting carbon_metrics with id: {id}")
    
    user_id = get_user_id_as_int(current_user)
    service = Carbon_metricsService(db)
    try:
        success = await service.delete(id, user_id=user_id)
        if not success:
            logger.warning(f"Carbon_metrics with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="Carbon_metrics not found")
        
        logger.info(f"Carbon_metrics {id} deleted successfully")
        return {"message": "Carbon_metrics deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting carbon_metrics {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")