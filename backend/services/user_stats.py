import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_stats import User_stats

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class User_statsService:
    """Service layer for User_stats operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Optional[User_stats]:
        """Create a new user_stats"""
        try:
            if user_id:
                data['user_id'] = user_id
            obj = User_stats(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created user_stats with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user_stats: {str(e)}")
            raise

    async def check_ownership(self, obj_id: int, user_id: int) -> bool:
        """Check if user owns this record"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            return obj is not None
        except Exception as e:
            logger.error(f"Error checking ownership for user_stats {obj_id}: {str(e)}")
            return False

    async def get_by_id(self, obj_id: int, user_id: Optional[int] = None) -> Optional[User_stats]:
        """Get user_stats by ID (user can only see their own records)"""
        try:
            query = select(User_stats).where(User_stats.id == obj_id)
            if user_id:
                query = query.where(User_stats.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching user_stats {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        user_id: Optional[int] = None,
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of user_statss (user can only see their own records)"""
        try:
            query = select(User_stats)
            count_query = select(func.count(User_stats.id))
            
            if user_id:
                query = query.where(User_stats.user_id == user_id)
                count_query = count_query.where(User_stats.user_id == user_id)
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(User_stats, field):
                        query = query.where(getattr(User_stats, field) == value)
                        count_query = count_query.where(getattr(User_stats, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(User_stats, field_name):
                        query = query.order_by(getattr(User_stats, field_name).desc())
                else:
                    if hasattr(User_stats, sort):
                        query = query.order_by(getattr(User_stats, sort))
            else:
                query = query.order_by(User_stats.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching user_stats list: {str(e)}")
            raise

    async def get_or_create_for_user(self, user_id: int) -> User_stats:
        """Get user_stats for a user, or create one if it doesn't exist"""
        try:
            result = await self.db.execute(
                select(User_stats).where(User_stats.user_id == user_id)
            )
            obj = result.scalar_one_or_none()
            
            if not obj:
                # Create default stats for user
                obj = User_stats(
                    user_id=user_id,
                    total_learning_time=0,
                    total_carbon_footprint=0,
                    total_trees_planted=0,
                    total_carbon_offset=0,
                    paths_completed=0,
                    current_streak=0,
                    longest_streak=0,
                    level=1,
                    experience_points=0
                )
                self.db.add(obj)
                await self.db.commit()
                await self.db.refresh(obj)
                logger.info(f"Created default user_stats for user_id: {user_id}")
            
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error getting/creating user_stats for user {user_id}: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any], user_id: Optional[int] = None) -> Optional[User_stats]:
        """Update user_stats (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"User_stats {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key) and key != 'user_id':
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated user_stats {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user_stats {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int, user_id: Optional[int] = None) -> bool:
        """Delete user_stats (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"User_stats {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted user_stats {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting user_stats {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[User_stats]:
        """Get user_stats by any field"""
        try:
            if not hasattr(User_stats, field_name):
                raise ValueError(f"Field {field_name} does not exist on User_stats")
            result = await self.db.execute(
                select(User_stats).where(getattr(User_stats, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching user_stats by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[User_stats]:
        """Get list of user_statss filtered by field"""
        try:
            if not hasattr(User_stats, field_name):
                raise ValueError(f"Field {field_name} does not exist on User_stats")
            result = await self.db.execute(
                select(User_stats)
                .where(getattr(User_stats, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(User_stats.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching user_statss by {field_name}: {str(e)}")
            raise