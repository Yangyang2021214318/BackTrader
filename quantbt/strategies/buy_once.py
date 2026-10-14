# -*- coding = utf-8 -*-
# @Time: 2026/10/6 13:07
# @Author: Yang Yang
# @File: but_once
# @Software: PyCharm

import backtrader as bt

class BuyOnce(bt.Strategy):
    params = (("stake",100),)
    def __init__(self):
        self.pending_order = None

    def next(self):
        if len(self) == 1 and self.pending_order is None:
            signal_date = self.data.datetime.date(0)
            print(f"{signal_date} close price:{self.data.close[0]:.2f},"
                  f" buy {self.p.stake}")
            self.pending_order = self.buy(size=self.p.stake)

    def notify_order(self, order):
        if order.status in (order.Submitted, order.Accepted):
            return

        if order.status == order.Completed:
            execution_date = bt.num2date(order.executed.dt).date()
            print(f"{execution_date} orders was executed for {self.p.stake} shares at a price of {order.executed.price:.2f}")

        else:
            print(f"order not executed : {order.getstatusname()}")

        self.pending_order = None



