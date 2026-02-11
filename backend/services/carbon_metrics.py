import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.carbon_metrics import Carbon_metrics

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Carbon_metricsService:
    """Service layer for Carbon_metrics operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Optional[Carbon_metrics]:
        """Create a new carbon_metrics"""
        try:
            if user_id:
                data['user_id'] = user_id
            obj = Carbon_metrics(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created carbon_metrics with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating carbon_metrics: {str(e)}")
            raise

    async def check_ownership(self, obj_id: int, user_id: int) -> bool:
        """Check if user owns this record"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            return obj is not None
        except Exception as e:
            logger.error(f"Error checking ownership for carbon_metrics {obj_id}: {str(e)}")
            return False

    async def get_by_id(self, obj_id: int, user_id: Optional[int] = None) -> Optional[Carbon_metrics]:
        """Get carbon_metrics by ID (user can only see their own records)"""
        try:
            query = select(Carbon_metrics).where(Carbon_metrics.id == obj_id)
            if user_id:
                query = query.where(Carbon_metrics.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching carbon_metrics {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        user_id: Optional[int] = None,
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of carbon_metricss (user can only see their own records)"""
        try:
            query = select(Carbon_metrics)
            count_query = select(func.count(Carbon_metrics.id))
            
            if user_id:
                query = query.where(Carbon_metrics.user_id == user_id)
                count_query = count_query.where(Carbon_metrics.user_id == user_id)
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Carbon_metrics, field):
                        query = query.where(getattr(Carbon_metrics, field) == value)
                        count_query = count_query.where(getattr(Carbon_metrics, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Carbon_metrics, field_name):
                        query = query.order_by(getattr(Carbon_metrics, field_name).desc())
                else:
                    if hasattr(Carbon_metrics, sort):
                        query = query.order_by(getattr(Carbon_metrics, sort))
            else:
                query = query.order_by(Carbon_metrics.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching carbon_metrics list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any], user_id: Optional[int] = None) -> Optional[Carbon_metrics]:
        """Update carbon_metrics (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Carbon_metrics {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key) and key != 'user_id':
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated carbon_metrics {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating carbon_metrics {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int, user_id: Optional[int] = None) -> bool:
        """Delete carbon_metrics (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Carbon_metrics {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted carbon_metrics {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting carbon_metrics {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Carbon_metrics]:
        """Get carbon_metrics by any field"""
        try:
            if not hasattr(Carbon_metrics, field_name):
                raise ValueError(f"Field {field_name} does not exist on Carbon_metrics")
            result = await self.db.execute(
                select(Carbon_metrics).where(getattr(Carbon_metrics, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching carbon_metrics by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Carbon_metrics]:
        """Get list of carbon_metricss filtered by field"""
        try:
            if not hasattr(Carbon_metrics, field_name):
                raise ValueError(f"Field {field_name} does not exist on Carbon_metrics")
            result = await self.db.execute(
                select(Carbon_metrics)
                .where(getattr(Carbon_metrics, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Carbon_metrics.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching carbon_metricss by {field_name}: {str(e)}")
            raise