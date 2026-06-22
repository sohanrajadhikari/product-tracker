import helper

def get_mode():
    while True:
        mode =  int(input("What do you want to do? \n 1. Track a new product. \n 2. Update prices of tracked products. \n 3. List all the tracked products. \n [1], [2], and [3] are the only valid inputs. \n"))
        if mode in [1,2,3]:
            return mode
        print("\n Please enter a valid input. \n")

if __name__ == '__main__':
    mode = get_mode()

    match mode:
        case 1:
            print('Track new product')
            helper.track_new()
        # case 2:
        #     print('Update prices of tracked products.')
        #     helper.update_prices()
        # case 3:
        #     print('List all products.')
        #     helper.list_products()
        case _:


            print('Something went wrong while handling modes.')