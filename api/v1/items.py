from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from db.database import get_db
from models.item import Item
from models.user import User
from schemas.item import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    """새 아이템 생성"""
    # 소유자 존재 확인
    result = await db.execute(select(User).where(User.id == item.owner_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 새 아이템 생성
    db_item = Item(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.get("/", response_model=List[ItemResponse])
async def read_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """모든 아이템 조회 (페이지네이션 지원)"""
    result = await db.execute(select(Item).offset(skip).limit(limit))
    items = result.scalars().all()
    return items


@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """특정 아이템 조회"""
    result = await db.execute(select(Item).where(Item.id == item_id))
    db_item = result.scalar_one_or_none()
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="아이템을 찾을 수 없습니다."
        )
    return db_item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemUpdate, db: AsyncSession = Depends(get_db)):
    """아이템 정보 업데이트"""
    result = await db.execute(select(Item).where(Item.id == item_id))
    db_item = result.scalar_one_or_none()
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="아이템을 찾을 수 없습니다."
        )
    
    # 소유자 변경 시 존재 확인
    if item.owner_id is not None:
        user_result = await db.execute(select(User).where(User.id == item.owner_id))
        db_user = user_result.scalar_one_or_none()
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
    
    # 업데이트할 필드만 적용
    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """아이템 삭제"""
    result = await db.execute(select(Item).where(Item.id == item_id))
    db_item = result.scalar_one_or_none()
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="아이템을 찾을 수 없습니다."
        )
    
    await db.delete(db_item)
    await db.commit()
    return None


@router.get("/owner/{owner_id}", response_model=List[ItemResponse])
async def read_items_by_owner(owner_id: int, db: AsyncSession = Depends(get_db)):
    """특정 사용자의 모든 아이템 조회"""
    result = await db.execute(select(User).where(User.id == owner_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    items_result = await db.execute(select(Item).where(Item.owner_id == owner_id))
    items = items_result.scalars().all()
    return items

