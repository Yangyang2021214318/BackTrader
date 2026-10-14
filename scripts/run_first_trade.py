# -*- coding = utf-8 -*-
# @Time: 2026/10/8 12:51
# @Author: Yang Yang
# @File: run_first_trade
# @Software: PyCharm

import backtrader as bt
from quantbt.data.a_share import load_a_share_bars
from quantbt.strategies.buy_once import BuyOnce
from quantbt.strategies.buy_then_sell import BuyThenSell

if __name__ == "__main__":
    bars = load_a_share_bars("000001","2025-01-01","2025-01-31")

    starting_cash = 100_000
    commission_rate = 0.001

    cerebro = bt.Cerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname = bars), name ="000001")
    cerebro.addstrategy(BuyThenSell,stake=100,hold_bars=3)
    cerebro.broker.setcash(starting_cash)
    cerebro.broker.setcommission(
        commission=commission_rate,
        commtype=bt.CommInfoBase.COMM_PERC,
        stocklike=True,
        percabs=True,
    )
    print(f"commission rate per side: {commission_rate:.2%}")
    print(f"starting portfolio value:{cerebro.broker.getvalue():.2f}")

    results = cerebro.run()
    strategy = results[0]
    ending_value = cerebro.broker.getvalue()
    print(f"end cash:{cerebro.broker.getcash():.2f}")
    print(f"end position:{results[0].position.size}")
    print(f"end portfolio value:{cerebro.broker.getvalue():.2f}")
    print(f"net portfolio change:{ending_value-starting_cash:.2f}")









