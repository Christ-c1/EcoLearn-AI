import json
import logging
from typing import List, Optional

from datetime import datetime, date

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.user_stats import User_statsService
from dependencies.auth import get_current_user
from schemas.auth import UserResponse

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entities/user_stats", tags=["user_stats"])


# ---------- Pydantic Schemas ----------
class User_statsData(BaseModel):
    """Entity data schema (for create/update)"""
    total_learning_time: int = None
    total_carbon_footprint: float = None
    total_trees_planted: int = None
    total_carbon_offset: float = None
    paths_completed: int = None
    current_streak: int = None
    longest_streak: int = None
    level: int = None
    experience_points: int = None
    updated_at: Optional[datetime] = None


class User_statsUpdateData(BaseModel):
    """Update entity data (partial updates allowed)"""
    total_learning_time: Optional[int] = None
    total_carbon_footprint: Optional[float] = None
    total_trees_planted: Optional[int] = None
    total_carbon_offset: Optional[float] = None
    paths_completed: Optional[int] = None
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None
    level: Optional[int] = None
    experience_points: Optional[int] = None
    updated_at: Optional[datetime] = None


class User_statsResponse(BaseModel):
    """Entity response schema"""
    id: int
    user_id: int
    total_learning_time: Optional[int] = None
    total_carbon_footprint: Optional[float] = None
    total_trees_planted: Optional[int] = None
    total_carbon_offset: Optional[float] = None
    paths_completed: Optional[int] = None
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None
    level: Optional[int] = None
    experience_points: Optional[int] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User_statsListResponse(BaseModel):
    """List response schema"""
    items: List[User_statsResponse]
    total: int
    skip: int
    limit: int


class User_statsBatchCreateRequest(BaseModel):
    """Batch create request"""
    items: List[User_statsData]


class User_statsBatchUpdateItem(BaseModel):
    """Batch update item"""
    id: int
    updates: User_statsUpdateData


class User_statsBatchUpdateRequest(BaseModel):
    """Batch update request"""
    items: List[User_statsBatchUpdateItem]


class User_statsBatchDeleteRequest(BaseModel):
    """Batch delete request"""
    ids: List[int]


def get_user_id_as_int(current_user: UserResponse) -> int:
    """Convert user_id to int, handling both str and int types"""
    try:
        return int(current_user.id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid user ID format")


# ---------- Routes ----------
@router.get("", response_model=User_statsListResponse)
async def query_user_statss(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query user_statss with filtering, sorting, and pagination (user can only see their own records)"""
    logger.debug(f"Querying user_statss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")
    
    user_id = get_user_id_as_int(current_user)
    service = User_statsService(db)
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
        logger.debug(f"Found {result['total']} user_statss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying user_statss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=User_statsListResponse)
async def query_user_statss_all(
    query: str = Query(None, description="Query conditions (JSON string)"),
    sort: str = Query(None, description="Sort field (prefix with '-' for descending)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=2000, description="Max number of records to return"),
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    db: AsyncSession = Depends(get_db),
):
    # Query user_statss with filtering, sorting, and pagination without user limitation
    logger.debug(f"Querying user_statss: query={query}, sort={sort}, skip={skip}, limit={limit}, fields={fields}")

    service = User_statsService(db)
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
        logger.debug(f"Found {result['total']} user_statss")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying user_statss: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/me", response_model=User_statsResponse)
async def get_my_stats(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's stats, creating default stats if they don't exist"""
    logger.debug(f"Fetching stats for current user")
    
    user_id = get_user_id_as_int(current_user)
    service = User_statsService(db)
    try:
        result = await service.get_or_create_for_user(user_id)
        return result
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{id}", response_model=User_statsResponse)
async def get_user_stats(
    id: int,
    fields: str = Query(None, description="Comma-separated list of fields to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single user_stats by ID (user can only see their own records)"""
    logger.debug(f"Fetching user_stats with id: {id}, fields={fields}")
    
    user_id = get_user_id_as_int(current_user)
    service = User_statsService(db)
    try:
        result = await service.get_by_id(id, user_id=user_id)
        if not result:
            logger.warning(f"User_stats with id {id} not found")
            raise HTTPException(status_code=404, detail="User_stats not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user_stats {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=User_statsResponse, status_code=201)
async def create_user_stats(
    data: User_statsData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new user_stats"""
    logger.debug(f"Creating new user_stats with data: {data}")
    
    user_id = get_user_id_as_int(current_user)
    service = User_statsService(db)
    try:
        result = await service.create(data.model_dump(), user_id=user_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create user_stats")
        
        logger.info(f"User_stats created successfully with id: {result.id}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating user_stats: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating user_stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch", response_model=List[User_statsResponse], status_code=201)
async def create_user_statss_batch(
    request: User_statsBatchCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create multiple user_statss in a single request"""
    logger.debug(f"Batch creating {len(request.items)} user_statss")
    
    user_id = get_user_id_as_int(current_user)
    service = User_statsService(db)
    results = []
    
    try:
        for item_data in request.items:
            result = await service.create(item_data.model_dump(), user_id=user_id)
            if result:
                results.append(result)
        
        logger.info(f"Batch created {len(results)} user_statss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch create failed: {str(e)}")


@router.put("/batch", response_model=List[User_statsResponse])
async def update_user_statss_batch(
    request: User_statsBatchUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update multiple user_statss in a single request (requires ownership)"""
    logger.debug(f"Batch updating {len(request.items)} user_statss")
    
    user_id = get_user_id_as_int(current_user)
    service = User_statsService(db)
    results = []
    
    try:
        for item in request.items:
            # Only include non-None values for partial updates
            update_dict = {k: v for k, v in item.updates.model_dump().items() if v is not None}
            result = await service.update(item.id, update_dict, user_id=user_id)
            if result:
                results.append(result)
        
        logger.info(f"Batch updated {len(results)} user_statss successfully")
        return results
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")


@router.put("/{id}", response_model=User_statsResponse)
async def update_user_stats(
    id: int,
    data: User_statsUpdateData,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing user_stats (requires ownership)"""
    logger.debug(f"Updating user_stats {id} with data: {data}")

    user_id = get_user_id_as_int(current_user)
    service = User_statsService(db)
    try:
        # Only include non-None values for partial updates
        update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await service.update(id, update_dict, user_id=user_id)
        if not result:
            logger.warning(f"User_stats with id {id} not found for update")
            raise HTTPException(status_code=404, detail="User_stats not found")
        
        logger.info(f"User_stats {id} updated successfully")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating user_stats {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user_stats {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/batch")
async def delete_user_statss_batch(
    request: User_statsBatchDeleteRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple user_statss by their IDs (requires ownership)"""
    logger.debug(f"Batch deleting {len(request.ids)} user_statss")
    
    user_id = get_user_id_as_int(current_user)
    service = User_statsService(db)
    deleted_count = 0
    
    try:
        for item_id in request.ids:
            success = await service.delete(item_id, user_id=user_id)
            if success:
                deleted_count += 1
        
        logger.info(f"Batch deleted {deleted_count} user_statss successfully")
        return {"message": f"Successfully deleted {deleted_count} user_statss", "deleted_count": deleted_count}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch delete failed: {str(e)}")


@router.delete("/{id}")
async def delete_user_stats(
    id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single user_stats by ID (requires ownership)"""
    logger.debug(f"Deleting user_stats with id: {id}")
    
    user_id = get_user_id_as_int(current_user)
    service = User_statsService(db)
    try:
        success = await service.delete(id, user_id=user_id)
        if not success:
            logger.warning(f"User_stats with id {id} not found for deletion")
            raise HTTPException(status_code=404, detail="User_stats not found")
        
        logger.info(f"User_stats {id} deleted successfully")
        return {"message": "User_stats deleted successfully", "id": id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user_stats {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")