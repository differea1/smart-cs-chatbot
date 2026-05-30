from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.knowledge import (
    KnowledgeItemCreate, KnowledgeItemUpdate,
    KnowledgeItemResponse, KnowledgeCategoryResponse,
)
from app.models.knowledge import KnowledgeCategory, KnowledgeItem
from app.core.database import get_db
from app.services.rag_service import RAGService

router = APIRouter()


@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    cats = db.query(KnowledgeCategory).order_by(KnowledgeCategory.sort_order).all()
    # Build tree
    cat_map = {}
    roots = []
    for c in cats:
        c_dict = KnowledgeCategoryResponse.model_validate(c).model_dump()
        c_dict["children"] = []
        cat_map[c.id] = c_dict
    for c in cats:
        if c.parent_id and c.parent_id in cat_map:
            cat_map[c.parent_id]["children"].append(cat_map[c.id])
        else:
            roots.append(cat_map[c.id])
    return roots


@router.get("/items")
async def list_items(
    category_id: int | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgeItem).filter(KnowledgeItem.is_published == 1)
    if category_id:
        sub_ids = [category_id]
        sub_cats = db.query(KnowledgeCategory).filter(
            KnowledgeCategory.parent_id == category_id
        ).all()
        sub_ids.extend([c.id for c in sub_cats])
        query = query.filter(KnowledgeItem.category_id.in_(sub_ids))
    if keyword:
        query = query.filter(
            (KnowledgeItem.title.contains(keyword)) |
            (KnowledgeItem.keywords.contains(keyword))
        )

    total = query.count()
    items = (
        query.order_by(KnowledgeItem.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [KnowledgeItemResponse.model_validate(item).model_dump() for item in items],
    }


@router.post("/items")
async def create_item(data: KnowledgeItemCreate, db: Session = Depends(get_db)):
    item = KnowledgeItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    # Sync to ChromaDB
    rag = RAGService()
    embedding_id = f"kb_{item.id}"
    search_text = f"[{item.title}] {item.keywords}\n{item.content}"
    rag.add_document(doc_id=embedding_id, content=search_text, metadata={
        "category_id": str(item.category_id),
        "type": item.type,
    })
    item.embedding_id = embedding_id
    db.commit()

    return KnowledgeItemResponse.model_validate(item).model_dump()


@router.put("/items/{item_id}")
async def update_item(item_id: int, data: KnowledgeItemUpdate, db: Session = Depends(get_db)):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(item, key, val)
    db.commit()

    # Sync to ChromaDB
    rag = RAGService()
    search_text = f"[{item.title}] {item.keywords}\n{item.content}"
    rag.add_document(doc_id=item.embedding_id or f"kb_{item.id}", content=search_text)

    return KnowledgeItemResponse.model_validate(item).model_dump()


@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    rag = RAGService()
    if item.embedding_id:
        rag.delete_document(item.embedding_id)
    db.delete(item)
    db.commit()
    return {"status": "deleted"}
