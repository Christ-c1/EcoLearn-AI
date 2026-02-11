import logging
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.tree_plantations import Tree_plantations

logger = logging.getLogger(__name__)


# ------------------ Service Layer ------------------
class Tree_plantationsService:
    """Service layer for Tree_plantations operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Optional[Tree_plantations]:
        """Create a new tree_plantations"""
        try:
            if user_id:
                data['user_id'] = user_id
            obj = Tree_plantations(**data)
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Created tree_plantations with id: {obj.id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating tree_plantations: {str(e)}")
            raise

    async def check_ownership(self, obj_id: int, user_id: int) -> bool:
        """Check if user owns this record"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            return obj is not None
        except Exception as e:
            logger.error(f"Error checking ownership for tree_plantations {obj_id}: {str(e)}")
            return False

    async def get_by_id(self, obj_id: int, user_id: Optional[int] = None) -> Optional[Tree_plantations]:
        """Get tree_plantations by ID (user can only see their own records)"""
        try:
            query = select(Tree_plantations).where(Tree_plantations.id == obj_id)
            if user_id:
                query = query.where(Tree_plantations.user_id == user_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching tree_plantations {obj_id}: {str(e)}")
            raise

    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        user_id: Optional[int] = None,
        query_dict: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get paginated list of tree_plantationss (user can only see their own records)"""
        try:
            query = select(Tree_plantations)
            count_query = select(func.count(Tree_plantations.id))
            
            if user_id:
                query = query.where(Tree_plantations.user_id == user_id)
                count_query = count_query.where(Tree_plantations.user_id == user_id)
            
            if query_dict:
                for field, value in query_dict.items():
                    if hasattr(Tree_plantations, field):
                        query = query.where(getattr(Tree_plantations, field) == value)
                        count_query = count_query.where(getattr(Tree_plantations, field) == value)
            
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            if sort:
                if sort.startswith('-'):
                    field_name = sort[1:]
                    if hasattr(Tree_plantations, field_name):
                        query = query.order_by(getattr(Tree_plantations, field_name).desc())
                else:
                    if hasattr(Tree_plantations, sort):
                        query = query.order_by(getattr(Tree_plantations, sort))
            else:
                query = query.order_by(Tree_plantations.id.desc())

            result = await self.db.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error fetching tree_plantations list: {str(e)}")
            raise

    async def update(self, obj_id: int, update_data: Dict[str, Any], user_id: Optional[int] = None) -> Optional[Tree_plantations]:
        """Update tree_plantations (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Tree_plantations {obj_id} not found for update")
                return None
            for key, value in update_data.items():
                if hasattr(obj, key) and key != 'user_id':
                    setattr(obj, key, value)

            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f"Updated tree_plantations {obj_id}")
            return obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating tree_plantations {obj_id}: {str(e)}")
            raise

    async def delete(self, obj_id: int, user_id: Optional[int] = None) -> bool:
        """Delete tree_plantations (requires ownership)"""
        try:
            obj = await self.get_by_id(obj_id, user_id=user_id)
            if not obj:
                logger.warning(f"Tree_plantations {obj_id} not found for deletion")
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f"Deleted tree_plantations {obj_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting tree_plantations {obj_id}: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, field_value: Any) -> Optional[Tree_plantations]:
        """Get tree_plantations by any field"""
        try:
            if not hasattr(Tree_plantations, field_name):
                raise ValueError(f"Field {field_name} does not exist on Tree_plantations")
            result = await self.db.execute(
                select(Tree_plantations).where(getattr(Tree_plantations, field_name) == field_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching tree_plantations by {field_name}: {str(e)}")
            raise

    async def list_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 20
    ) -> List[Tree_plantations]:
        """Get list of tree_plantationss filtered by field"""
        try:
            if not hasattr(Tree_plantations, field_name):
                raise ValueError(f"Field {field_name} does not exist on Tree_plantations")
            result = await self.db.execute(
                select(Tree_plantations)
                .where(getattr(Tree_plantations, field_name) == field_value)
                .offset(skip)
                .limit(limit)
                .order_by(Tree_plantations.id.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching tree_plantationss by {field_name}: {str(e)}")
            raise