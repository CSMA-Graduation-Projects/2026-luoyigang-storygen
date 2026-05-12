from fastapi import FastAPI
from app.api.story_api import router
from fastapi.middleware.cors import CORSMiddleware
from app.api.pdf_api import router as pdf_router
from app.api.document_story_api import router as document_story_router
from app.api.project_story_api import router as project_story_router
from app.api.user_story_optimization_api import router as story_optimization_router
from app.api.code_story_api import router as code_story_router
from app.api.history_api import router as history_router
from app.api.agent_config_api import router as agent_config_router
app = FastAPI(title="Multi-Agent User Story System")

# 解决跨域（关键）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(pdf_router)
app.include_router(document_story_router)
app.include_router(project_story_router)
app.include_router(history_router)
app.include_router(story_optimization_router)
app.include_router(code_story_router)
app.include_router(agent_config_router)