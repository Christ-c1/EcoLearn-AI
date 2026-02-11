import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dependencies.auth import get_current_user
from schemas.auth import UserResponse
from services.ai_learning import AILearningService, CarbonCalculatorService
from services.learning_paths import Learning_pathsService
from services.carbon_metrics import Carbon_metricsService
from services.user_stats import User_statsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/learning", tags=["learning"])

class GenerateLearningPathRequest(BaseModel):
    topic: str
    difficulty: str = "beginner"

class GenerateLearningPathResponse(BaseModel):
    success: bool
    learning_path_id: Optional[int] = None
    content: dict

class RecordSessionRequest(BaseModel):
    learning_path_id: int
    duration_minutes: int
    device_type: str = "laptop"

class RecordSessionResponse(BaseModel):
    success: bool
    carbon_metrics: dict
    message: str

class CarbonStatsResponse(BaseModel):
    total_carbon_kg: float
    total_trees_planted: int
    carbon_offset_kg: float
    net_carbon_kg: float
    is_carbon_positive: bool


def get_user_id_as_int(current_user: UserResponse) -> int:
    """Convert user_id to int, handling both str and int types"""
    try:
        return int(current_user.id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid user ID format")


@router.post("/generate-path", response_model=GenerateLearningPathResponse)
async def generate_learning_path(
    request: GenerateLearningPathRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a new AI-powered learning path"""
    try:
        user_id = get_user_id_as_int(current_user)
        
        ai_service = AILearningService()
        content = await ai_service.generate_learning_path(
            topic=request.topic,
            difficulty=request.difficulty
        )
        
        # Save to database
        learning_paths_service = Learning_pathsService(db)
        import json
        learning_path = await learning_paths_service.create(
            data={
                "title": content.get("title", request.topic),
                "description": content.get("description", ""),
                "topic": request.topic,
                "difficulty": request.difficulty,
                "content": json.dumps(content),
                "progress": 0,
                "total_sessions": len(content.get("modules", [])),
                "completed_sessions": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            user_id=user_id
        )
        
        return GenerateLearningPathResponse(
            success=True,
            learning_path_id=learning_path.id if learning_path else None,
            content=content
        )
    except Exception as e:
        logger.error(f"Error generating learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/record-session", response_model=RecordSessionResponse)
async def record_learning_session(
    request: RecordSessionRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record a learning session and calculate carbon footprint"""
    try:
        user_id = get_user_id_as_int(current_user)
        
        carbon_service = CarbonCalculatorService()
        carbon_data = carbon_service.calculate_session_carbon(
            duration_minutes=request.duration_minutes,
            device_type=request.device_type
        )
        
        # Save carbon metrics
        carbon_metrics_service = Carbon_metricsService(db)
        await carbon_metrics_service.create(
            data={
                "learning_path_id": request.learning_path_id,
                "session_duration": request.duration_minutes,
                "carbon_footprint": carbon_data["carbon_footprint_grams"],
                "device_type": request.device_type,
                "energy_consumed": carbon_data["energy_consumed_wh"],
                "trees_contribution": carbon_data["trees_contribution"],
                "session_date": datetime.now(),
                "created_at": datetime.now()
            },
            user_id=user_id
        )
        
        # Update user stats
        user_stats_service = User_statsService(db)
        stats_result = await user_stats_service.get_list(user_id=user_id, limit=1)
        
        if stats_result["items"]:
            user_stats = stats_result["items"][0]
            await user_stats_service.update(
                obj_id=user_stats.id,
                update_data={
                    "total_learning_time": (user_stats.total_learning_time or 0) + request.duration_minutes,
                    "total_carbon_footprint": (user_stats.total_carbon_footprint or 0) + carbon_data["carbon_footprint_kg"],
                    "updated_at": datetime.now()
                },
                user_id=user_id
            )
        else:
            await user_stats_service.create(
                data={
                    "total_learning_time": request.duration_minutes,
                    "total_carbon_footprint": carbon_data["carbon_footprint_kg"],
                    "total_trees_planted": 0,
                    "total_carbon_offset": 0,
                    "paths_completed": 0,
                    "current_streak": 1,
                    "longest_streak": 1,
                    "level": 1,
                    "experience_points": request.duration_minutes * 10,
                    "updated_at": datetime.now()
                },
                user_id=user_id
            )
        
        return RecordSessionResponse(
            success=True,
            carbon_metrics=carbon_data,
            message=f"Session enregistrée! Empreinte carbone: {carbon_data['carbon_footprint_grams']:.2f}g CO2"
        )
    except Exception as e:
        logger.error(f"Error recording session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/carbon-stats", response_model=CarbonStatsResponse)
async def get_carbon_stats(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's carbon statistics"""
    try:
        user_id = get_user_id_as_int(current_user)
        
        user_stats_service = User_statsService(db)
        stats_result = await user_stats_service.get_list(user_id=user_id, limit=1)
        
        if stats_result["items"]:
            user_stats = stats_result["items"][0]
            carbon_service = CarbonCalculatorService()
            stats = carbon_service.get_carbon_stats(
                total_carbon_kg=user_stats.total_carbon_footprint or 0,
                total_trees_planted=user_stats.total_trees_planted or 0
            )
            return CarbonStatsResponse(
                total_carbon_kg=stats["total_carbon_emitted_kg"],
                total_trees_planted=stats["trees_planted"],
                carbon_offset_kg=stats["total_carbon_offset_kg"],
                net_carbon_kg=stats["net_carbon_kg"],
                is_carbon_positive=stats["is_carbon_positive"]
            )
        
        return CarbonStatsResponse(
            total_carbon_kg=0,
            total_trees_planted=0,
            carbon_offset_kg=0,
            net_carbon_kg=0,
            is_carbon_positive=True
        )
    except Exception as e:
        logger.error(f"Error getting carbon stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plant-tree")
async def plant_tree(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Plant a tree to offset carbon"""
    try:
        user_id = get_user_id_as_int(current_user)
        
        from services.tree_plantations import Tree_plantationsService
        
        tree_service = Tree_plantationsService(db)
        carbon_service = CarbonCalculatorService()
        
        # Create tree plantation record
        tree_species = ["Chêne", "Érable", "Pin", "Bouleau", "Saule"]
        locations = ["France", "Brésil", "Kenya", "Indonésie", "Canada"]
        
        import random
        await tree_service.create(
            data={
                "trees_planted": 1,
                "carbon_offset": carbon_service.TREE_CO2_ABSORPTION,
                "location": random.choice(locations),
                "tree_species": random.choice(tree_species),
                "plantation_date": datetime.now(),
                "certificate_id": f"ECO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
                "created_at": datetime.now()
            },
            user_id=user_id
        )
        
        # Update user stats
        user_stats_service = User_statsService(db)
        stats_result = await user_stats_service.get_list(user_id=user_id, limit=1)
        
        if stats_result["items"]:
            user_stats = stats_result["items"][0]
            await user_stats_service.update(
                obj_id=user_stats.id,
                update_data={
                    "total_trees_planted": (user_stats.total_trees_planted or 0) + 1,
                    "total_carbon_offset": (user_stats.total_carbon_offset or 0) + carbon_service.TREE_CO2_ABSORPTION,
                    "experience_points": (user_stats.experience_points or 0) + 100,
                    "updated_at": datetime.now()
                },
                user_id=user_id
            )
        
        return {"success": True, "message": "🌳 Arbre planté avec succès!"}
    except Exception as e:
        logger.error(f"Error planting tree: {e}")
        raise HTTPException(status_code=500, detail=str(e))