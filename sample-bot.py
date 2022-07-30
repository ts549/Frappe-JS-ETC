#!/usr/bin/env python3
# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py --test prod-like; sleep 1; done

import argparse
from collections import deque
from enum import Enum
import time
import socket
import json
from socket import error as socket_error

# ~~~~~============== CONFIGURATION  ==============~~~~~
# Replace "REPLACEME" with your team name!
team_name = "FRAPPE"

# ~~~~~============== VARIABLES ==============~~~~~
## Book Prices
dict_book = {
    "BOND": [],
    "VALBZ": [],
    "VALE": [],
    "GS": [],
    "MS": [],
    "WFC": [],
    "XLF": []
}

dict_positions = {
    "BOND": 0,
    "VALBZ": 0,
    "VALE": 0,
    "GS": 0,
    "MS": 0,
    "WFC": 0,
    "XLF": 0
}

dict_trades = {
    "BOND": [],
    "VALBZ": [],
    "VALE": [],
    "GS": [],
    "MS": [],
    "WFC": [],
    "XLF": []
}

order_id = 0

# ~~~~~============== HELPER FUNCTIONS ==============~~~~~
def bond_trade(exchange, message):
    return

def avg(trades):
    return sum(trades) / len(trades)

def etf_last10_averages(XLF_trades, bond_trades, GS_trades, MS_trades, WFC_trades):
    margin = 150
    XLF_avg = avg(XLF_trades[-10:])
    bond_avg = avg(bond_trades[-10:])
    GS_avg = avg(GS_trades[-10:])
    MS_avg = avg(MS_trades[-10:])
    WFC_avg = avg(WFC_trades[-10:])

    if (10*(XLF_avg) + margin < (3*bond_avg + 2*GS_avg + 3*MS_avg + 2*WFC_avg)):
        return [True, XLF_avg, bond_avg, GS_avg, MS_avg, WFC_avg]

    if (10*(XLF_avg) - margin > (3*bond_avg + 2*GS_avg + 3*MS_avg + 2*WFC_avg)):
        return [False, XLF_avg, bond_avg, GS_avg, MS_avg, WFC_avg]

def updated_etf_trade(exchange, xlf, bond, gs, ms, wfc):
    print("using etf")


    xlf_trades = xlf[-15:] 
    bond_trades = bond[-15:]
    gs_trades = gs[-15:]
    ms_trades = ms[-15:]
    wfc_trades = wfc[-15:]
    
    trades = etf_last10_averages(xlf_trades, bond_trades, gs_trades, ms_trades, wfc_trades)

    if (trades[0]):
        print("ETF to stocks\n")
        order_id += 1
        exchange.send_add_message(order_id, symbol="XLF", dir=Dir.BUY, price=dict_trades['XLF'][-1], size=100)
        
        order_id += 1
        exchange.send_convert_message(order_id, symbol="XLF", dir=Dir.SELL, price=dict_trades['XLF'][-1], size=1)

        order_id += 1
        exchange.send_add_message(order_id, symbol="BOND", dir=Dir.SELL, price=dict_trades['BOND'][-1], size=30)

        order_id += 1
        exchange.send_add_message(order_id, symbol="GS", dir=Dir.SELL, price=dict_trades['GS'][-1], size=20)

        order_id += 1
        exchange.send_add_message(order_id, symbol="MS", dir=Dir.SELL, price=dict_trades['MS'][-1], size=30)

        order_id += 1
        exchange.send_add_message(order_id, symbol="WFC", dir=Dir.SELL, price=dict_trades['WFC'][-1], size=20)

    else:
        print("Stocks to ETF\n")
        order_id += 1
        exchange.send_add_message(order_id, symbol="BOND", dir=Dir.BUY, price=dict_trades['BOND'][-1], size=30)

        order_id += 1
        exchange.send_add_message(order_id, symbol="GS", dir=Dir.BUY, price=dict_trades['GS'][-1], size=20)

        order_id += 1
        exchange.send_add_message(order_id, symbol="MS", dir=Dir.BUY, price=dict_trades['MS'][-1], size=30)

        order_id += 1
        exchange.send_add_message(order_id, symbol="WFC", dir=Dir.BUY, price=dict_trades['WFC'][-1], size=20)

        order_id += 1
        exchange.send_convert_message(order_id, symbol="XLF", dir=Dir.BUY, price=dict_trades['XLF'][-1], size=1)

        order_id += 1
        exchange.send_add_message(order_id, symbol="XLF", dir=Dir.SELL, price=dict_trades['XLF'][-1], size=100)

# ~~~~~============== STRATS ==============~~~~~
def adr(exchange, valbz_trades, vale_trades):
    global order_id
    # do we want to take the average of the entire list
    # or do we want to take the average of the past 10 trades
    margin = 1
    if (len(valbz_trades) >= 10 and len(vale_trades) >=10):
        fair_value = avg(valbz_trades[-10:])
        if (avg(vale_trades[-10:]) - fair_value >=2):
            if (dict_positions["VALE"] < 10):
                #buy illiquid
                order_id += 1
                exchange.send_add_message(order_id, "VALE", Dir.BUY, int(fair_value - margin), 1)
                dict_positions["VALE"] += 1
            
            # if (dict_positions["VALE"] > 0):
            #     #sell illiquid
            #     order_id += 1
            #     exchange.send_add_message(order_id, "VALE", Dir.SELL, int(fair_value + margin), 1)

            if (dict_positions["VALE"] == 10):
                order_id += 1
                exchange.send_convert_message(order_id, "VALE", Dir.SELL, 10)
                dict_positions["VALE"] -= 10
                order_id += 1
                exchange.send_add_message(order_id, "VALBZ", Dir.SELL, int(fair_value + margin), 10)

            
            time.sleep(0.01)


# ~~~~~============== MAIN LOOP ==============~~~~~

# You should put your code here! We provide some starter code as an example,
# but feel free to change/remove/edit/update any of it as you'd like. If you
# have any questions about the starter code, or what to do next, please ask us!
#
# To help you get started, the sample code below tries to buy BOND for a low
# price, and it prints the current prices for VALE every second. The sample
# code is intended to be a working example, but it needs some improvement
# before it will start making good trades!


def main():
    global order_id
    orders = {"BOND": 0, "VALBZ": 0, "VALE": 0, "GS": 0, "MS": 0, "WFC": 0, "XLF": 0}
    args = parse_arguments()

    exchange = ExchangeConnection(args=args)

    # Store and print the "hello" message received from the exchange. This
    # contains useful information about your positions. Normally you start with
    # all positions at zero, but if you reconnect during a round, you might
    # have already bought/sold symbols and have non-zero positions.
    hello_message = exchange.read_message()
    print("First message from exchange:", hello_message)


    # Send an order for BOND at a good price, but it is low enough that it is
    # unlikely it will be traded against. Maybe there is a better price to
    # pick? Also, you will need to send more orders over time.
    # order_id += 1
    # exchange.send_add_message(order_id, symbol="BOND", dir=Dir.BUY, price=999, size=100)
    # order_id += 1
    # exchange.send_add_message(order_id, symbol="BOND", dir=Dir.SELL, price=1001, size=100)

    # Set up some variables to track the bid and ask price of a symbol. Right
    # now this doesn't track much information, but it's enough to get a sense
    # of the VALE market.
    vale_bid_price, vale_ask_price = None, None
    vale_last_print_time = time.time()

    # Here is the main loop of the program. It will continue to read and
    # process messages in a loop until a "close" message is received. You
    # should write to code handle more types of messages (and not just print
    # the message). Feel free to modify any of the starter code below.
    #
    # Note: a common mistake people make is to call write_message() at least
    # once for every read_message() response.
    #
    # Every message sent to the exchange generates at least one response
    # message. Sending a message in response to every exchange message will
    # cause a feedback loop where your bot's messages will quickly be
    # rate-limited and ignored. Please, don't do that!
    while True:

        message = exchange.read_message()
        adr(exchange, dict_trades["VALBZ"], dict_trades["VALE"])

        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!
        if message["type"] == "close":
            print(dict_positions)
            print("The round has ended")
            break
        elif message["type"] == "trade":
            if message["symbol"] == "VALBZ":
                for index in range(message["size"]):
                    dict_trades["VALBZ"].append(message["price"])
            if message["symbol"] == "VALE":
                for index in range(message["size"]):
                    dict_trades["VALE"].append(message["price"])
            if message["symbol"] == "BOND":
                    if (message["price"] > 1000 and dict_positions["BOND"]>=-10):
                        order_id +=1
                        exchange.send_add_message(order_id, "BOND", Dir.SELL, 1001, 1)
                    if (message["price"] < 1000 and dict_positions["BOND"]<=99):
                        order_id += 1
                        exchange.send_add_message(order_id, "BOND", Dir.BUY,  999, 1)
                
            # print(messagse)      
        elif message["type"] == "error":
        
            print(message)
        elif message["type"] == "reject":
            print(message)
        elif message["type"] == "fill":
            print(message)
            # if (message["symbol"] == "BOND"):
            #     if (message["dir"] == "BUY"):
            #         dict_positions["BOND"] += message["size"]
            #         continue
            #     else:
            #         dict_positions["BOND"] -= message["size"]
            #         continue
            
            # if (message["symbol"] == "VALBZ"):
            #     if (message["dir"] == "BUY"):
            #         dict_positions["VALBZ"] += message["size"]
            #         continue
            #     else:
            #         dict_positions["VALBZ"] -= message["size"]
            #         continue
            
            # if (message["symbol"] == "VALE"):
            #     if (message["dir"] == "BUY"):
            #         dict_positions["VALE"] += message["size"]
            #         continue
            #     else:
            #         dict_positions["VALE"] -= message["size"]
            #         continue
            
            # if (message["symbol"] == "XLF"):
            #     if (message["dir"] == "BUY"):
            #         dict_positions["XLF"] += 100
            #         dict_positions["BOND"] -= 30
            #         dict_positions["GS"] -= 20
            #         dict_positions["MS"] -= 30
            #         dict_positions["WFC"] -= 20
            #         continue
            #     else:
            #         dict_positions["XLF"] -= 100
            #         dict_positions["BOND"]+= 30
            #         dict_positions["GS"] += 20
            #         dict_positions["MS"] += 30
            #         dict_positions["WFC"] += 20
            #         continue
        elif message["type"] == "book":
            
            ''' if message["symbol"] == "VALE":

                def best_price(side):
                    if message[side]:
                        return message[side][0][0]

                vale_bid_price = best_price("buy")
                vale_ask_price = best_price("sell")

                now = time.time()

                if now > vale_last_print_time + 1:
                    vale_last_print_time = now
                    print(
                        {
                            "vale_bid_price": vale_bid_price,
                            "vale_ask_price": vale_ask_price,
                        }
                    ) '''
    while True:
         try:
             main()
         except socket_error:
             print ("\r\n----------------Main: socket error,do reconnect----------------")
             time.sleep(0.1)


# ~~~~~============== PROVIDED CODE ==============~~~~~

# You probably don't need to edit anything below this line, but feel free to
# ask if you have any questions about what it is doing or how it works. If you
# do need to change anything below this line, please feel free to


class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExchangeConnection:
    def __init__(self, args):
        self.message_timestamps = deque(maxlen=500)
        self.exchange_hostname = args.exchange_hostname
        self.port = args.port
        self.exchange_socket = self._connect(add_socket_timeout=args.add_socket_timeout)

        self._write_message({"type": "hello", "team": team_name.upper()})

    def read_message(self):
        """Read a single message from the exchange"""
        message = json.loads(self.exchange_socket.readline())
        if "dir" in message:
            message["dir"] = Dir(message["dir"])
        return message

    def send_add_message(
        self, order_id: int, symbol: str, dir: Dir, price: int, size: int
    ):
        """Add a new order"""
        self._write_message(
            {
                "type": "add",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "price": price,
                "size": size,
            }
        )

    def send_convert_message(self, order_id: int, symbol: str, dir: Dir, size: int):
        """Convert between related symbols"""
        self._write_message(
            {
                "type": "convert",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "size": size,
            }
        )

    def send_cancel_message(self, order_id: int):
        """Cancel an existing order"""
        self._write_message({"type": "cancel", "order_id": order_id})

    def _connect(self, add_socket_timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if add_socket_timeout:
            # Automatically raise an exception if no data has been recieved for
            # multiple seconds. This should not be enabled on an "empty" test
            # exchange.
            s.settimeout(5)
        s.connect((self.exchange_hostname, self.port))
        return s.makefile("rw", 1)

    def _write_message(self, message):
        json.dump(message, self.exchange_socket)
        self.exchange_socket.write("\n")

        now = time.time()
        self.message_timestamps.append(now)
        if len(
            self.message_timestamps
        ) == self.message_timestamps.maxlen and self.message_timestamps[0] > (now - 1):
            print(
                "WARNING: You are sending messages too frequently. The exchange will start ignoring your messages. Make sure you are not sending a message in response to every exchange message."
            )


def parse_arguments():
    test_exchange_port_offsets = {"prod-like": 0, "slower": 1, "empty": 2}

    parser = argparse.ArgumentParser(description="Trade on an ETC exchange!")
    exchange_address_group = parser.add_mutually_exclusive_group(required=True)
    exchange_address_group.add_argument(
        "--production", action="store_true", help="Connect to the production exchange."
    )
    exchange_address_group.add_argument(
        "--test",
        type=str,
        choices=test_exchange_port_offsets.keys(),
        help="Connect to a test exchange.",
    )

    # Connect to a specific host. This is only intended to be used for debugging.
    exchange_address_group.add_argument(
        "--specific-address", type=str, metavar="HOST:PORT", help=argparse.SUPPRESS
    )

    args = parser.parse_args()
    args.add_socket_timeout = True

    if args.production:
        args.exchange_hostname = "production"
        args.port = 25000
    elif args.test:
        args.exchange_hostname = "test-exch-" + team_name
        args.port = 25000 + test_exchange_port_offsets[args.test]
        if args.test == "empty":
            args.add_socket_timeout = False
    elif args.specific_address:
        args.exchange_hostname, port = args.specific_address.split(":")
        args.port = int(port)

    return args


if __name__ == "__main__":
    # Check that [team_name] has been updated.
    assert (
        team_name != "team_name"
    ), "Please put your team name in the variable [team_name]."

    main()

