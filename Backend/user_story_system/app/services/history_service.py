from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from bson import ObjectId
    from pymongo import MongoClient, DESCENDING
except Exception:  # 允许项目在未安装 pymongo 时仍可启动生成逻辑
    ObjectId = None
    MongoClient = None
    DESCENDING = -1

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGODB_DB", "user_story_system")

COLLECTIONS = {
    "text": "text_story_history",
    "code": "code_story_history",
    "document": "document_story_history",
    "project": "project_story_history",
}

_client = None


def _get_client():
    global _client
    if MongoClient is None:
        raise RuntimeError("未安装 pymongo，请执行：pip install pymongo")
    if _client is None:
        _client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=2500)
    return _client


def _get_collection(history_type: str):
    if history_type not in COLLECTIONS:
        raise ValueError("不支持的历史类型")
    db = _get_client()[MONGO_DB_NAME]
    return db[COLLECTIONS[history_type]]


def _serialize(value: Any) -> Any:
    if ObjectId is not None and isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat(timespec="seconds")
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value


def save_history(history_type: str, payload: Dict[str, Any]) -> Optional[str]:
    """保存历史记录。MongoDB 不可用时不阻断原生成流程。"""
    try:
        collection = _get_collection(history_type)
        now = datetime.utcnow()
        doc = {
            **payload,
            "history_type": history_type,
            "created_at": now,
            "updated_at": now,
        }
        result = collection.insert_one(doc)
        return str(result.inserted_id)
    except Exception as exc:
        print(f"[history] 保存 {history_type} 历史失败：{exc}")
        return None


def list_history(history_type: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
    collection = _get_collection(history_type)
    projection = {
        "events": 0,
        "code": 0,
        "requirements": 0,
        "relations": 0,
        "graph": 0,
        "nodes": 0,
        "edges": 0,
        "function_tree": 0,
        "story_tree": 0,
        "stories": 0,
        "data": 0,
    }
    cursor = (
        collection.find({}, projection)
        .sort("created_at", DESCENDING)
        .skip(max(skip, 0))
        .limit(min(max(limit, 1), 100))
    )
    items = []
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        items.append(_serialize(doc))
    return items


def get_history_detail(history_type: str, history_id: str) -> Dict[str, Any]:
    if ObjectId is None:
        raise RuntimeError("未安装 pymongo，请执行：pip install pymongo")
    collection = _get_collection(history_type)
    try:
        object_id = ObjectId(history_id)
    except Exception:
        raise FileNotFoundError("历史记录 ID 格式不正确")
    doc = collection.find_one({"_id": object_id})
    if not doc:
        raise FileNotFoundError("未找到对应历史记录")
    doc["id"] = str(doc.pop("_id"))
    return _serialize(doc)
