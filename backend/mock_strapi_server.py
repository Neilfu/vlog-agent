#!/usr/bin/env python3
"""
Mock Strapi Server for Testing
模拟Strapi服务器用于测试

提供基本的Strapi API端点来测试集成
Provides basic Strapi API endpoints for integration testing
"""

import json
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mock Strapi Server",
    description="Mock Strapi server for testing Chinese AI Video System integration",
    version="1.0.0"
)

# In-memory data storage
projects_db: Dict[str, Dict[str, Any]] = {}
creative_ideas_db: Dict[str, Dict[str, Any]] = {}
scripts_db: Dict[str, Dict[str, Any]] = {}
webhooks_db: List[Dict[str, Any]] = []

# Content type definitions
CONTENT_TYPES = {
    "projects": "project",
    "creative-ideas": "creative_idea",
    "scripts": "script",
    "storyboards": "storyboard",
    "media-assets": "media_asset",
    "final-videos": "final_video"
}

# Mock data templates
PROJECT_TEMPLATE = {
    "title": "",
    "description": "",
    "status": "draft",
    "business_input": {},
    "technical_specs": {},
    "priority": "medium",
    "tags": [],
    "metadata": {},
    "createdAt": "",
    "updatedAt": ""
}

CREATIVE_IDEA_TEMPLATE = {
    "title": "",
    "description": "",
    "content": {},
    "concept": "",
    "target_audience": {},
    "platform": "douyin",
    "tone": "professional",
    "style": "modern",
    "duration": 30,
    "tags": [],
    "createdAt": "",
    "updatedAt": ""
}

SCRIPT_TEMPLATE = {
    "title": "",
    "content": "",
    "scenes": [],
    "characters": [],
    "duration": 30,
    "language": "zh-CN",
    "tone": "friendly",
    "call_to_action": "",
    "keywords": [],
    "createdAt": "",
    "updatedAt": ""
}

class ProjectCreate(BaseModel):
    title: str
    description: str = ""
    status: str = "draft"
    business_input: Dict[str, Any] = {}
    technical_specs: Dict[str, Any] = {}
    priority: str = "medium"
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class CreativeIdeaCreate(BaseModel):
    title: str
    description: str = ""
    content: Dict[str, Any] = {}
    concept: str = ""
    target_audience: Dict[str, Any] = {}
    platform: str = "douyin"
    tone: str = "professional"
    style: str = "modern"
    duration: int = 30
    tags: List[str] = []

class ScriptCreate(BaseModel):
    title: str
    content: str
    scenes: List[Dict[str, Any]] = []
    characters: List[Dict[str, Any]] = []
    duration: int = 30
    language: str = "zh-CN"
    tone: str = "friendly"
    call_to_action: str = ""
    keywords: List[str] = []

@app.get("/")
async def root():
    """Root endpoint - returns basic API info"""
    return {
        "name": "Mock Strapi Server",
        "version": "1.0.0",
        "description": "Mock Strapi server for testing Chinese AI Video System integration"
    }

@app.get("/api")
@app.get("/api/")
async def api_root():
    """API root endpoint - mimics Strapi's API root"""
    return {
        "name": "Mock Strapi API",
        "version": "4.15.4",
        "description": "Mock Strapi API for testing"
    }

@app.get("/_health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    logger.info("📋 Listing all projects")
    return {
        "data": list(projects_db.values()),
        "meta": {
            "pagination": {
                "page": 1,
                "pageSize": 25,
                "pageCount": 1,
                "total": len(projects_db)
            }
        }
    }

@app.post("/api/projects")
async def create_project(project_data: Dict[str, Any]):
    """Create a new project"""
    try:
        project_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # Extract data from the nested structure that Strapi expects
        data = project_data.get("data", {})

        project = {
            "id": project_id,
            "attributes": {
                **PROJECT_TEMPLATE,
                **data,
                "createdAt": now,
                "updatedAt": now
            }
        }

        projects_db[project_id] = project
        logger.info(f"✅ Created project: {data.get('title', 'Unknown')} (ID: {project_id})")

        return {"data": project}

    except Exception as e:
        logger.error(f"❌ Failed to create project: {e}")
        raise HTTPException(status_code=400, detail=f"Project creation failed: {e}")

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get a specific project"""
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"data": project}

@app.put("/api/projects/{project_id}")
async def update_project(project_id: str, project_data: Dict[str, Any]):
    """Update a project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        data = project_data.get("data", {})
        now = datetime.now().isoformat()

        # Update the project
        projects_db[project_id]["attributes"].update(data)
        projects_db[project_id]["attributes"]["updatedAt"] = now

        logger.info(f"✅ Updated project: {project_id}")
        return {"data": projects_db[project_id]}

    except Exception as e:
        logger.error(f"❌ Failed to update project {project_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Project update failed: {e}")

@app.post("/api/creative-ideas")
async def create_creative_idea(idea_data: Dict[str, Any]):
    """Create a new creative idea"""
    try:
        idea_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        data = idea_data.get("data", {})

        idea = {
            "id": idea_id,
            "attributes": {
                **CREATIVE_IDEA_TEMPLATE,
                **data,
                "createdAt": now,
                "updatedAt": now
            }
        }

        creative_ideas_db[idea_id] = idea
        logger.info(f"✅ Created creative idea: {data.get('title', 'Unknown')} (ID: {idea_id})")

        return {"data": idea}

    except Exception as e:
        logger.error(f"❌ Failed to create creative idea: {e}")
        raise HTTPException(status_code=400, detail=f"Creative idea creation failed: {e}")

@app.post("/api/scripts")
async def create_script(script_data: Dict[str, Any]):
    """Create a new script"""
    try:
        script_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        data = script_data.get("data", {})

        script = {
            "id": script_id,
            "attributes": {
                **SCRIPT_TEMPLATE,
                **data,
                "createdAt": now,
                "updatedAt": now
            }
        }

        scripts_db[script_id] = script
        logger.info(f"✅ Created script: {data.get('title', 'Unknown')} (ID: {script_id})")

        return {"data": script}

    except Exception as e:
        logger.error(f"❌ Failed to create script: {e}")
        raise HTTPException(status_code=400, detail=f"Script creation failed: {e}")

@app.post("/api/webhooks")
async def register_webhook(webhook_data: Dict[str, Any]):
    """Register a webhook"""
    try:
        webhook_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        data = webhook_data.get("data", {})
        webhook = {
            "id": webhook_id,
            "attributes": {
                **data,
                "createdAt": now,
                "updatedAt": now
            }
        }

        webhooks_db.append(webhook)
        logger.info(f"✅ Registered webhook: {data.get('name', 'Unknown')} (ID: {webhook_id})")

        return {"data": webhook}

    except Exception as e:
        logger.error(f"❌ Failed to register webhook: {e}")
        raise HTTPException(status_code=400, detail=f"Webhook registration failed: {e}")

@app.post("/api/webhooks/receive")
async def receive_webhook(webhook_data: Dict[str, Any], request: Request):
    """Receive webhook from external source (for testing)"""
    try:
        logger.info(f"📨 Received webhook: {webhook_data.get('event', 'unknown')}")

        # Simulate webhook processing
        event = webhook_data.get("event")
        model = webhook_data.get("model")
        entry = webhook_data.get("entry", {})

        logger.info(f"📝 Processing webhook: {event} for {model} (ID: {entry.get('id', 'unknown')})")

        # Return success
        return {"success": True, "message": "Webhook processed successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to process webhook: {e}")
        return {"success": False, "error": str(e)}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "data": None,
            "error": {
                "status": 404,
                "name": "NotFoundError",
                "message": "Not Found",
                "details": {}
            }
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "error": {
                "status": 500,
                "name": "InternalServerError",
                "message": "Internal Server Error",
                "details": {}
            }
        }
    )

def run_mock_strapi_server():
    """Run the mock Strapi server"""
    print("🚀 Starting Mock Strapi Server...")
    print("📍 Server will be available at: http://localhost:1337")
    print("📊 Admin panel: http://localhost:1337/admin")
    print("🔍 API docs: http://localhost:1337/docs")
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=1337,
        log_level="info"
    )

if __name__ == "__main__":
    run_mock_strapi_server()