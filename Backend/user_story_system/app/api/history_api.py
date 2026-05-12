from fastapi import APIRouter, HTTPException, Query

from app.services.history_service import COLLECTIONS, get_history_detail, list_history

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{history_type}")
def get_history_list(
    history_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    if history_type not in COLLECTIONS:
        raise HTTPException(status_code=400, detail="历史类型仅支持 text/code/document/project")
    try:
        return {"type": history_type, "items": list_history(history_type, skip, limit)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"读取历史记录失败：{exc}")


@router.get("/{history_type}/{history_id}")
def get_history_item(history_type: str, history_id: str):
    if history_type not in COLLECTIONS:
        raise HTTPException(status_code=400, detail="历史类型仅支持 text/code/document/project")
    try:
        return get_history_detail(history_type, history_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"读取历史详情失败：{exc}")
