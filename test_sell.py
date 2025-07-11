import json
from exchange import Exchange

def test_basic_sell():
    e = Exchange()
    e.new_limit_order(side='buy', symbol='aapl', price=101, quantity=1)
    order_status = json.loads(e.new_limit_order(side='sell', symbol='aapl', price=100., quantity=1))
    assert order_status['status'] == 'filled'
    assert order_status['quantity'] == 0
    assert order_status['avg_price_got'] == 101

def test_two_step_sell():
    e = Exchange()
    e.new_limit_order(side='buy', symbol='aapl', price=101, quantity=1)
    e.new_limit_order(side='buy', symbol='aapl', price=100, quantity=1)
    order_status = json.loads(e.new_limit_order(side='sell', symbol='aapl', price=100, quantity=2))
    assert order_status['status'] == 'filled'
    assert order_status['quantity'] == 0
    assert order_status['avg_price_got'] == 100.5

def test_three_step_buy():
    e = Exchange()
    e.new_limit_order(side='buy', symbol='aapl', price=99, quantity=1)
    e.new_limit_order(side='buy', symbol='aapl', price=100, quantity=1)
    e.new_limit_order(side='buy', symbol='aapl', price=101, quantity=2)
    order_status = json.loads(e.new_limit_order(side='sell', symbol='aapl', price=99, quantity=4))
    assert order_status['status'] == 'filled'
    assert order_status['quantity'] == 0
    assert order_status['avg_price_got'] == 100.25
    e.show_completed_orders()
