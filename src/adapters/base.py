"""数据适配器抽象基类."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AdapterError(Exception):
    """适配器通用异常."""
    pass


class BaseAdapter(ABC):
    """数据适配器抽象接口.

    所有数据源适配器必须实现此接口.
    接口定义来自 engine/data-architecture.md §适配器接口规范.
    """

    @abstractmethod
    def fetch_product_list(self, product_type: str) -> List[Dict[str, Any]]:
        """按产品类型拉取产品列表.

        Args:
            product_type: 产品类型（stock/equity_fund/mixed_fund/...）

        Returns:
            产品字典列表
        """
        ...

    @abstractmethod
    def fetch_product_detail(self, product_code: str) -> Dict[str, Any]:
        """拉取单只产品详情."""
        ...

    @abstractmethod
    def fetch_financial_data(
        self, product_code: str, data_points: List[str]
    ) -> Dict[str, float]:
        """拉取指定数据点."""
        ...

    @abstractmethod
    def fetch_market_signal(
        self, product_code: str, signal_ids: List[str]
    ) -> Dict[str, float]:
        """拉取市场信号数据."""
        ...

    @abstractmethod
    def check_health(self) -> bool:
        """检查适配器可用性."""
        ...
