from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.services.pdf_service import generate_pdf

router = APIRouter()


@router.post("/export_pdf")
async def export_pdf(data: dict):
    requirement = data.get("requirement", "")
    sub_requirements = data.get("sub_requirements", [])
    final_stories = data.get("final_stories", [])

    filepath = generate_pdf(requirement, sub_requirements, final_stories)

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename="user_story_report.pdf"
    )