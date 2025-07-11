from dataclasses import dataclass
from datetime import datetime

@dataclass
class Trade:
    buy_side_order_id: int
    sell_side_order_id: int
    price: float
    quantity: int
    timestamp: datetime