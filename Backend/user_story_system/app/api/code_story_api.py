from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.code_story_service import (
    CodeStoryParseError,
    analyze_code_story,
    analyze_code_story_file,
    export_code_story,
    get_code_story_item,
    load_code_story_result,
)

router = APIRouter(prefix="/code_story", tags=["code_story"])


class CodeStoryRequest(BaseModel):
    code: str
    language: str = ""
    filename: str = "code_snippet"


@router.post("/analyze")
async def analyze_code_story_api(req: CodeStoryRequest):
    """
    代码片段到用户故事：
    - 能拆分为多个函数/方法/类时，按代码单元逐个逆向生成需求和用户故事
    - 不能拆分时，将整体代码作为一个代码单元分析
    - 直接根据代码生成，不复用文本需求生成流程
    """
    try:
        return await analyze_code_story(req.code, req.language, req.filename)
    except CodeStoryParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"代码用户故事生成失败：{exc}")


@router.post("/analyze_file")
async def analyze_code_story_file_api(
    file: UploadFile = File(...),
    language: str = Form(""),
):
    try:
        return await analyze_code_story_file(file, language)
    except CodeStoryParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"代码文件用户故事生成失败：{exc}")


@router.get("/{code_story_id}")
def get_code_story_result(code_story_id: str):
    try:
        return load_code_story_result(code_story_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{code_story_id}/nodes/{node_id}")
def get_code_story_node_result(code_story_id: str, node_id: str):
    try:
        return get_code_story_item(code_story_id, node_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{code_story_id}/export")
def export_code_story_result(code_story_id: str, format: str = "markdown"):
    try:
        path = export_code_story(code_story_id, format)
        ext = path.split(".")[-1].lower()
        media_types = {
            "md": "text/markdown",
            "json": "application/json",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pdf": "application/pdf",
        }
        return FileResponse(path, media_type=media_types.get(ext, "application/octet-stream"), filename=path.split("/")[-1])
    except CodeStoryParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
