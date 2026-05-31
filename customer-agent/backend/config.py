from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    db_path: Path
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    max_parallel_tasks: int = 4
    source_coverage_threshold: float = 0.6
    in_scope_keywords: tuple[str, ...] = (
        "订单", "物流", "退货", "退款", "发票", "库存",
        "价格", "产品", "商品", "门铃", "摄像头", "夜视",
        "保修", "售后", "支持", "规格", "功能",
    )


def get_settings() -> Settings:
    import os
    root = Path(__file__).resolve().parent.parent
    return Settings(
        data_dir=root / "data",
        db_path=root / "data" / "customer_agent.db",
        deepseek_api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        deepseek_base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        deepseek_model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
    )
