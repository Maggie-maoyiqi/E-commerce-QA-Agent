"""FastAPI entry point for the Customer Agent backend."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import DatabaseManager
from backend.step_5_api.workflow import CustomerServiceWorkflow
from backend.step_5_api import app_state
from backend.step_5_api.routes import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(f"Data dir: {settings.data_dir}")

    # Initialize DB
    db = DatabaseManager(settings.db_path, settings.data_dir)
    db.initialize()

    # Initialize LLM client (optional - works without API key in fallback mode)
    llm_client = None
    if settings.deepseek_api_key:
        try:
            from openai import OpenAI
            llm_client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )
            logger.info("DeepSeek LLM client initialized")
        except Exception as e:
            logger.warning(f"Could not initialize LLM client: {e}")
    else:
        logger.warning("No DEEPSEEK_API_KEY set — running in rule-based fallback mode")

    # Initialize workflow
    workflow = CustomerServiceWorkflow(settings, llm_client=llm_client)
    app_state.init_workflow(workflow)
    logger.info("Workflow initialized")

    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Customer Agent API",
    description="Multi-agent e-commerce customer service system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
