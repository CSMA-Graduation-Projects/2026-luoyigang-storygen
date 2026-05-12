from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services.user_story_optimization_service import (
    StoryOptimizationParseError,
    analyze_and_optimize_story_document,
    export_optimization_docx,
    export_optimization_json,
    export_optimization_markdown,
    get_optimization_item,
    load_optimization_result,
)

router = APIRouter(prefix="/story_optimization", tags=["story_optimization"])


@router.post("/analyze")
async def analyze_story_optimization(file: UploadFile = File(...)):
    """
    上传用户故事文档，系统自动拆分每条用户故事并逐个优化。
    返回优化前、优化后、验收标准和提升点。
    """
    try:
        return await analyze_and_optimize_story_document(file)
    except StoryOptimizationParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"用户故事优化失败：{exc}")


@router.get("/{optimization_id}")
def get_story_optimization_result(optimization_id: str):
    try:
        return load_optimization_result(optimization_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{optimization_id}/items/{story_id}")
def get_story_optimization_item(optimization_id: str, story_id: str):
    try:
        return get_optimization_item(optimization_id, story_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{optimization_id}/export")
def export_story_optimization_result(optimization_id: str, format: str = "markdown"):
    try:
        if format == "json":
            path = export_optimization_json(optimization_id)
            media_type = "application/json"
        elif format == "docx":
            path = export_optimization_docx(optimization_id)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            path = export_optimization_markdown(optimization_id)
            media_type = "text/markdown"
        return FileResponse(path, media_type=media_type, filename=path.split("/")[-1])
    except StoryOptimizationParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
