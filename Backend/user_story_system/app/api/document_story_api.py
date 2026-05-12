from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services.document_story_service import (
    DocumentParseError,
    analyze_requirement_document,
    export_document_stories_json,
    export_document_stories_markdown,
    get_requirement_story,
    load_document_result,
)

router = APIRouter(prefix="/document_story", tags=["document_story"])


@router.post("/analyze")
async def analyze_document_story(file: UploadFile = File(...)):
    """
    上传 Word / PDF / Markdown / TXT 需求文档，返回：
    - 分析后的各条需求
    - 功能性 / 非功能性需求分类
    - 模块划分
    - 用户故事与验收标准
    - 需求关系图数据
    """
    try:
        return await analyze_requirement_document(file)
    except DocumentParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"需求文档分析失败：{exc}")


@router.get("/{document_id}")
def get_document_story_result(document_id: str):
    try:
        return load_document_result(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{document_id}/requirements/{requirement_id}")
def get_requirement_story_result(document_id: str, requirement_id: str):
    try:
        return get_requirement_story(document_id, requirement_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{document_id}/export")
def export_document_story_result(document_id: str, format: str = "markdown"):
    try:
        if format == "json":
            path = export_document_stories_json(document_id)
            media_type = "application/json"
        else:
            path = export_document_stories_markdown(document_id)
            media_type = "text/markdown"
        return FileResponse(path, media_type=media_type, filename=path.split("/")[-1])
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
