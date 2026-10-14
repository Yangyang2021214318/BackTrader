# -*- coding = utf-8 -*-
# @Time: 2026/10/4 16:47
# @Author: Yang Yang
# @File: preview_backtrader_feed
# @Software: PyCharm

import backtrader as bt
from quantbt.data.a_share import load_a_share_bars

class PrintBars(bt.Strategy):
    def next(self):
        trade_date = self.data.datetime.date(0)
        close_price = self.data.close[0]
        print(f"{trade_date}closing price: {close_price:.2f}")

if __name__ == '__main__':
    bars = load_a_share_bars("000001","2025-01-01","2025-01-31")
    cerebro = bt.Cerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=bars),name="000001")
    cerebro.addstrategy(PrintBars)
    cerebro.broker.setcash(100_000)
    print(f"starting capital：{cerebro.broker.getvalue():.2f}")
    cerebro.run()
    print(f"ending capital：{cerebro.broker.getvalue():.2f}")





