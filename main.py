from exchange import Exchange

e = Exchange()

while True:
    print('')
    print('1. New Order')
    print('2. View book (pending orders)')
    print('3. View all completed orders')
    print('4. View all past trades - for exchange')
    print('5. Exit')
    choice = input('Enter choice: ')

    match choice:
        case '1':
            side = input('Side (buy or sell):')
            type = input('Type (limit or market):')
            symbol = input('Symbol:')
            quantity = int(input('Quantity:'))
            if type == 'limit':
                price = float(input('Price:'))
                print(e.new_limit_order(side=side, symbol=symbol, price=price, quantity=quantity))
        
        case '2':
            e.show_completed_orders()
    
        case '5':
            break