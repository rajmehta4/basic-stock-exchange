from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

@dataclass(order=True)
class Order:
    # in python non-default fields have to be declared first
    price: float = field(compare=True) # compare=True means this field will be used to compare orders in heap
    side: str         = field(compare=False)
    type: str         = field(compare=False)
    symbol: str       = field(compare=False)
    quantity: int     = field(compare=False)

    timestamp: datetime = field(default_factory=datetime.now, compare=True)
    status: str          = field(default="open", compare=False)
    filled_quantity: int = field(default=0, compare=False)
    avg_price_got: float = field(default=-1, compare=False)
    id: int              = field(init=False, compare=True)
    _id_counter: ClassVar[int] = 1

    def __post_init__(self):
        self.id = Order._id_counter
        Order._id_counter += 1
