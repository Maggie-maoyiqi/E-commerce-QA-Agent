#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""GraphRAG 查询脚本 — 三星冰箱知识图谱"""

import asyncio
import logging
import warnings
import os
import json
from pathlib import Path

warnings.filterwarnings("ignore", category=SyntaxWarning)

import graphrag.api as api
from graphrag.config.load_config import load_config
from graphrag.callbacks.noop_query_callbacks import NoopQueryCallbacks
from graphrag.utils.storage import load_table_from_storage
from graphrag.storage.file_pipeline_storage import FilePipelineStorage

# ========================================
# 配置 — 按需修改
# ========================================
ROOT = Path(__file__).resolve().parents[2]  # ~/customer-agent
GRAPHRAG_DIR = ROOT / "data" / "graphrag"   # ~/customer-agent/data/graphrag

QUERY = "冰箱如何清洁？有哪些注意事项？"
QUERY_TYPE = "local"   # local | global | drift | basic
COMMUNITY_LEVEL = 2
RESPONSE_TYPE = "text"
OUTPUT_FILE = None     # 设为文件路径则保存结果，None 则只打印

# ========================================

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


async def run_query(query: str, query_type: str = "local",
                    community_level: int = 2, response_type: str = "text"):

    graphrag_config = load_config(GRAPHRAG_DIR)

    output_dir = Path(graphrag_config.output_storage.base_dir)
    if not output_dir.is_absolute():
        output_dir = GRAPHRAG_DIR / output_dir

    storage = FilePipelineStorage(root_dir=str(output_dir))

    entities          = await load_table_from_storage("entities", storage)
    text_units        = await load_table_from_storage("text_units", storage)
    communities       = await load_table_from_storage("communities", storage)
    community_reports = await load_table_from_storage("community_reports", storage)
    relationships     = await load_table_from_storage("relationships", storage)

    try:
        covariates = await load_table_from_storage("covariates", storage)
    except Exception:
        covariates = None

    callbacks = [NoopQueryCallbacks()]

    if query_type == "local":
        response, context = await api.local_search(
            config=graphrag_config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            text_units=text_units,
            relationships=relationships,
            covariates=covariates,
            community_level=community_level,
            response_type=response_type,
            query=query,
            callbacks=callbacks,
        )
    elif query_type == "global":
        response, context = await api.global_search(
            config=graphrag_config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            community_level=community_level,
            response_type=response_type,
            query=query,
            callbacks=callbacks,
        )
    elif query_type == "basic":
        response, context = await api.basic_search(
            config=graphrag_config,
            text_units=text_units,
            query=query,
            callbacks=callbacks,
        )
    else:
        raise ValueError(f"不支持的查询类型: {query_type}")

    return response, context


def main():
    response, context = asyncio.run(run_query(
        query=QUERY,
        query_type=QUERY_TYPE,
        community_level=COMMUNITY_LEVEL,
        response_type=RESPONSE_TYPE,
    ))

    print("\n" + "=" * 60)
    print("查询结果:")
    print("=" * 60)
    print(response)
    print("=" * 60)

    if OUTPUT_FILE:
        Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump({"query": QUERY, "response": response}, f,
                      ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
