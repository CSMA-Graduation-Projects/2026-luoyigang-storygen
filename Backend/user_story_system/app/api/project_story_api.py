from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from app.services.project_story_service import (
    ProjectParseError,
    analyze_project_source,
    export_project_story,
    get_project_node_story,
    load_project_result,
    stream_project_source,
)

router = APIRouter(prefix="/project_story", tags=["project_story"])


@router.post("/analyze")
async def analyze_project_story(file: UploadFile = File(...)):
    """
    非流式接口：上传项目源码，按每个函数/类/方法节点调用 AI 生成用户故事。
    """
    try:
        return await analyze_project_source(file)
    except ProjectParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"项目源码分析失败：{exc}")


@router.post("/analyze_stream")
async def analyze_project_story_stream(file: UploadFile = File(...)):
    """
    流式接口：先返回项目节点解析结果，再逐节点返回 AI 生成的用户故事。
    前端使用 fetch 读取 text/event-stream，适合展示逐节点生成过程。
    """
    return StreamingResponse(
        stream_project_source(file),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{project_id}")
def get_project_story_result(project_id: str):
    try:
        return load_project_result(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{project_id}/nodes/{node_id}")
def get_project_node_story_result(project_id: str, node_id: str):
    try:
        return get_project_node_story(project_id, node_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{project_id}/export")
def export_project_story_result(project_id: str, format: str = "markdown"):
    try:
        path = export_project_story(project_id, format)
        safe_format = (format or "markdown").lower()
        media_types = {
            "json": "application/json",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pdf": "application/pdf",
            "markdown": "text/markdown; charset=utf-8",
            "md": "text/markdown; charset=utf-8",
        }
        return FileResponse(path, media_type=media_types.get(safe_format, "application/octet-stream"), filename=__import__("os").path.basename(path))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ProjectParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
