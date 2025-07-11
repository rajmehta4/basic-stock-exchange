from typing import Dict, List
from order import Order
from trade import Trade
import heapq
import json

class Exchange:

    completed_orders: List[Order] = []
    buy_orders: Dict[str, List[Order]] = {} # max-heap for each symbol (pending buy limit orders)
    sell_orders: Dict[str, List[Order]] = {} # min-heap for each symbol (pending sell limit orders)
    trades: List[Trade]

    @staticmethod
    def _to_json(o: Order):
        # default=str so that it doesn't give this error - Object of type datetime is not JSON serializable
        return json.dumps(o.__dict__, indent=2, default=str)

    def _push_to_completed_orders(self, order):
        self.completed_orders.append(order)

    def _push_to_heap(self, heap_name: str, symbol: str, order: Order):
        dic = getattr(self, heap_name)

        # Ensure a heap exists for this symbol, else initialize []
        heap = dic.setdefault(symbol, [])
        heapq.heappush(heap, order)

        if heap_name == "buy_orders":
            heapq._heapify_max(heap)

    
    def _pop_from_heap(self, heap_name: str, symbol: str) -> Order:
        dic = getattr(self, heap_name)
        heap = dic[symbol]
        popped_order = heapq.heappop(heap)

        if heap_name == "buy_orders":
            heapq._heapify_max(heap)

        # if you just popped the last element, del the dictionary entry
        if not dic[symbol]:
            del dic[symbol]

        return popped_order

    def show_completed_orders(self):
        print("\nCompleted orders:")
        for order in self.completed_orders:
            print(self._to_json(order))

    def new_limit_order(self, side: str, symbol: str, price: float, quantity: int):
        match side:
            case "buy":
                buy_order = Order(price, side, "limit", symbol, quantity)

                # does exchange have any sell orders for this symbol? Yes.
                if symbol in self.sell_orders:
                    top_sell_order = self.sell_orders[symbol][0]

                    while top_sell_order.price <= buy_order.price and buy_order.quantity != 0:

                            # top sell order has enough quantity to sell
                            if top_sell_order.quantity >= buy_order.quantity:

                                # modify sell order

                                # if avg not set before
                                if top_sell_order.avg_price_got == -1:
                                    top_sell_order.avg_price_got = top_sell_order.price
                                else:
                                    top_sell_order.avg_price_got = (top_sell_order.avg_price_got * top_sell_order.filled_quantity + buy_order.price * buy_order.quantity) / (top_sell_order.filled_quantity + buy_order.quantity)

                                top_sell_order.quantity -= buy_order.quantity
                                top_sell_order.filled_quantity += buy_order.quantity
                                if top_sell_order.quantity == 0:
                                    top_sell_order.status = "filled"
                                    completed_order = self._pop_from_heap("sell_orders", symbol)
                                    self._push_to_completed_orders(completed_order)
                                else:
                                    top_sell_order.status = "partially filled"

                                # modify buy order

                                # if avg not set before - meaning first and only trade for this buy order
                                if buy_order.avg_price_got == -1:
                                    buy_order.avg_price_got = top_sell_order.price
                                else:
                                    buy_order.avg_price_got = (buy_order.avg_price_got * buy_order.filled_quantity + top_sell_order.price * buy_order.quantity) / (buy_order.filled_quantity + buy_order.quantity)

                                buy_order.filled_quantity += buy_order.quantity
                                buy_order.quantity = 0
                                buy_order.status = "filled"

                                # in case buy_order was partially filled in last loop, and we pushed it to heap at that time
                                if symbol in self.buy_orders:
                                    self._pop_from_heap("buy_orders", symbol)
                                    
                            # top sell order doesn't have enough quantity to sell, so sell what it has and repeat
                            else:
                                
                                # modify buy order

                                # if avg not set before
                                if buy_order.avg_price_got == -1:
                                    buy_order.avg_price_got = top_sell_order.price
                                else:
                                    buy_order.avg_price_got = (buy_order.avg_price_got * buy_order.filled_quantity + top_sell_order.price * top_sell_order.quantity) / (buy_order.filled_quantity + top_sell_order.quantity)

                                buy_order.quantity -= top_sell_order.quantity
                                buy_order.filled_quantity += top_sell_order.quantity
                                buy_order.status = "partially filled"
                                # self._push_to_heap("buy_orders", symbol, buy_order)
                                

                                # modify sell order

                                # if avg not set before - meaning first and only trade for this sell order
                                if top_sell_order.avg_price_got == -1:
                                    top_sell_order.avg_price_got = top_sell_order.price
                                else:
                                    top_sell_order.avg_price_got = (top_sell_order.avg_price_got * top_sell_order.filled_quantity + buy_order.price * top_sell_order.quantity) / (top_sell_order.filled_quantity + top_sell_order.quantity)

                                top_sell_order.filled_quantity += top_sell_order.quantity
                                top_sell_order.quantity = 0
                                top_sell_order.status = "filled"
                                self._pop_from_heap("sell_orders", symbol)
                                self._push_to_completed_orders(top_sell_order)

                                # if there are more sell orders, assign top one
                                if self.sell_orders[symbol]:
                                    top_sell_order = self.sell_orders[symbol][0]
                                # if no more sell orders, break loop
                                else:
                                    break

                    # after running loop if quantity is left, add it to heap
                    if buy_order.quantity != 0:
                        self._push_to_completed_orders(buy_order)

                # does exchange have any sell orders for this symbol? No. Just insert this order in buy_orders dict
                else:
                    self._push_to_heap("buy_orders", symbol, buy_order)

                return self._to_json(buy_order)





            case "sell":
                sell_order = Order(price, side, "limit", symbol, quantity)

                # does exchange have any buy orders for this symbol? Yes.
                if symbol in self.buy_orders:
                    top_buy_order = self.buy_orders[symbol][0]

                    while top_buy_order.price >= sell_order.price and sell_order.quantity != 0: # change 1

                        # top buy order has enough quantity to buy
                        if top_buy_order.quantity >= sell_order.quantity:

                            # modify top buy order

                            # if avg not set before
                            if top_buy_order.avg_price_got == -1:
                                top_buy_order.avg_price_got = top_buy_order.price
                            else:
                                top_buy_order.avg_price_got = (
                                                                      top_buy_order.avg_price_got * top_buy_order.filled_quantity + sell_order.price * sell_order.quantity) / (
                                                                      top_buy_order.filled_quantity + sell_order.quantity)

                            top_buy_order.quantity -= sell_order.quantity
                            top_buy_order.filled_quantity += sell_order.quantity
                            top_buy_order.status = "partially filled"

                            # if buy order is exhausted, do the necesarry
                            if top_buy_order.quantity == 0:
                                top_buy_order.status = "filled"
                                completed_order = self._pop_from_heap("buy_orders", symbol)
                                self._push_to_completed_orders(completed_order)

                            # modify sell order

                            # if avg not set before - meaning first and only trade for this sell order
                            if sell_order.avg_price_got == -1:
                                sell_order.avg_price_got = top_buy_order.price
                            else:
                                sell_order.avg_price_got = (
                                                                   sell_order.avg_price_got * sell_order.filled_quantity + top_buy_order.price * sell_order.quantity) / (
                                                                   sell_order.filled_quantity + sell_order.quantity)

                            sell_order.filled_quantity += sell_order.quantity
                            sell_order.quantity = 0
                            sell_order.status = "filled"
                            self._push_to_completed_orders(sell_order)

                            # in case sell_order was partially filled in last loop, and we pushed it to heap at that time, remove it
                            if symbol in self.sell_orders:
                                self._pop_from_heap("sell_orders", symbol)

                        # top buy order doesn't have enough quantity to buy, so let him buy what he wants and repeat
                        else:

                            # modify sell order

                            # if avg not set before
                            if sell_order.avg_price_got == -1:
                                sell_order.avg_price_got = top_buy_order.price
                            else:
                                sell_order.avg_price_got = (
                                                                   sell_order.avg_price_got * sell_order.filled_quantity + top_buy_order.price * top_buy_order.quantity) / (
                                                                   sell_order.filled_quantity + top_buy_order.quantity)

                            sell_order.quantity -= top_buy_order.quantity
                            sell_order.filled_quantity += top_buy_order.quantity
                            sell_order.status = "partially filled"

                            # modify top buy order

                            # if avg not set before - meaning first and only trade for this sell order
                            if top_buy_order.avg_price_got == -1:
                                top_buy_order.avg_price_got = top_buy_order.price
                            else:
                                top_buy_order.avg_price_got = (
                                                                      top_buy_order.avg_price_got * top_buy_order.filled_quantity + sell_order.price * top_buy_order.quantity) / (
                                                                      top_buy_order.filled_quantity + top_buy_order.quantity)

                            top_buy_order.filled_quantity += top_buy_order.quantity
                            top_buy_order.quantity = 0
                            top_buy_order.status = "filled"
                            self._pop_from_heap("buy_orders", symbol)
                            self._push_to_completed_orders(top_buy_order)

                            # if there are more buy orders, assign top one
                            if self.buy_orders[symbol]:
                                top_buy_order = self.buy_orders[symbol][0]
                                print()
                            # if no more buy orders, break loop
                            else:
                                break

                    # after running loop if quantity is left, add it to heap
                    if sell_order.quantity != 0:
                        self._push_to_heap("sell_orders", symbol, sell_order)

                # does exchange have any buy orders for this symbol? No. Just insert this order in sell_orders dict
                else:
                    self._push_to_heap("sell_orders", symbol, sell_order)

                return self._to_json(sell_order)

        return None

        # check_book
        # generate order
        # register trade
        # update book/completed order