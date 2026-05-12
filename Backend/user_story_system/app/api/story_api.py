from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.story_service import stream_user_stories
from app.services.code_story_service import analyze_code_story

router = APIRouter()


class CodeStoryRequest(BaseModel):
    code: str
    language: str = "unknown"


@router.get("/generate_story_stream")
async def generate_story_stream(requirement: str):

    generator = stream_user_stories(requirement)

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/generate_story_from_code_stream")
async def generate_story_from_code_stream(req: CodeStoryRequest):
    """
    兼容旧前端的代码生成接口。

    当前实现已改为独立的代码单元解析 + 逐代码单元逆向生成用户故事，
    不再复用文本需求拆分/文本需求生成用户故事流程。
    """

    if not req.code or not req.code.strip():
        raise HTTPException(status_code=400, detail="代码内容不能为空")

    async def generator():
        result = await analyze_code_story(code=req.code, language=req.language, filename="code_snippet")
        import json
        yield f"data: {json.dumps({'type': 'code_story_result', 'data': result}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
