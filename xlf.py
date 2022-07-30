
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

def etf_recent(XLF_trades, bond_trades, GS_trades, MS_trades, WFC_trades):
    margin = 150
    
    if (10*(XLF_trades[-1:]) + margin < (3*bond_trades[-1:0] + 2*GS_trades[-1:0] + 3*MS_trades[-1:0] + 2*WFC_trades[-1:0])):
        return [True, XLF_trades[-1:], bond_trades[-1:], GS_trades[-1:], MS_trades[-1:], WFC_trades[-1:]]

    if (10*(XLF_trades[-1:]) - margin > (3*bond_trades[-1:0] + 2*GS_trades[-1:0] + 3*MS_trades[-1:0] + 2*WFC_trades[-1:0])):
        return [False, XLF_trades[-1:], bond_trades[-1:], GS_trades[-1:], MS_trades[-1:], WFC_trades[-1:]]

def updated_etf_trade(exchange, xlf, bond, gs, ms, wfc):
    print("using etf")


    xlf_trades = xlf[-15:] 
    bond_trades = bond[-15:]
    gs_trades = gs[-15:]
    ms_trades = ms[-15:]
    wfc_trades = wfc[-15:]
    
    trades = etf_recent(xlf_trades, bond_trades, gs_trades, ms_trades, wfc_trades)

    if len(xlf) > 15 and len(bond) > 15 and len(gs) > 15 and len(ms) > 15 and len(wfc) > 15 :
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


            if message["symbol"] == "GS":
                for index in range(message["size"]):
                    dict_trades["GS"].append(message["price"])
            if message["symbol"] == "MS":
                for index in range(message["size"]):
                        dict_trades["MS"].append(message["price"])
            if message["symbol"] == "WFC":
                for index in range(message["size"]):
                    dict_trades["WFC"].append(message["price"])
            if message["symbol"] == "XLF":
                for index in range(message["size"]):
                    dict_trades["XLF"].append(message["price"])


                    