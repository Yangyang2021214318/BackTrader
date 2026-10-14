# -*- coding = utf-8 -*-
# @Time: 2026/10/8 16:38
# @Author: Yang Yang
# @File: buy_then_sell
# @Software: PyCharm

import backtrader as bt

class BuyThenSell(bt.Strategy):
    params = (("stake",100),("hold_bars",3))
    def __init__(self):
        self.pending_order = None
        self.buy_bar = None
        self.buy_submitted = None
        self.finished = None

    def next(self):
        if self.pending_order is not None or self.finished :
            return

        signal_date = self.data.datetime.date(0)

        if not self.position and not self.buy_submitted:
            print(f"{signal_date} BUY submitted: {self.p.stake} shares, close = {self.data.close[0]:.2f}")
            self.pending_order = self.buy(size=self.p.stake)
            self.buy_submitted = True

        elif self.position and self.buy_bar is not None:
            bars_since_buy = len(self) - self.buy_bar

            if bars_since_buy >= self.p.hold_bars:
                print(f"{signal_date} SELL submitted: {self.p.stake} shares, close={self.data.close[0]:.2f}")
                self.pending_order =self.close()

    def notify_order(self, order):
        if order.status in (order.Submitted, order.Accepted):
            return
        if order.status == order.Partial:
            return
        if order.status == order.Completed:
            execution_date = bt.num2date(order.executed.dt).date()
            side ="BUY" if order.isbuy() else "SELL"

            print(f"{execution_date} {side} executed: {abs(order.executed.size):.0f} shares at {order.executed.price:.2f}")

            if order.isbuy():
                self.buy_bar = len(self)
            else:
                self.finished = True

        else:
            print(f"Order ended: {order.getstatusname()}")
            self.finished = True

        self.pending_order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            print(f"Trade close: gross profit ={trade.pnl:.2f}, net profit ={trade.pnlcomm:.2f}")









