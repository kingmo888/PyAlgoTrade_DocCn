strategy -- 策略基类
==================================

Strategies类是你定义的何时买、何时卖等等交易逻辑的类。

做多和做空可以通过以下两种方式:

    * 使用下面任意一个方法下单：

     * :meth:`pyalgotrade.strategy.BaseStrategy.marketOrder`
     * :meth:`pyalgotrade.strategy.BaseStrategy.limitOrder`
     * :meth:`pyalgotrade.strategy.BaseStrategy.stopOrder`
     * :meth:`pyalgotrade.strategy.BaseStrategy.stopLimitOrder`

    * 使用封装了买/卖的高级接口下单：

     * :meth:`pyalgotrade.strategy.BaseStrategy.enterLong`
     * :meth:`pyalgotrade.strategy.BaseStrategy.enterShort`
     * :meth:`pyalgotrade.strategy.BaseStrategy.enterLongLimit`
     * :meth:`pyalgotrade.strategy.BaseStrategy.enterShortLimit`

Positions are higher level abstractions for placing orders. They are escentially a pair of entry-exit orders and provide
easier tracking for returns and PnL than using individual orders.


Strategy
--------

.. automodule:: pyalgotrade.strategy
    :members: BaseStrategy, BacktestingStrategy
    :show-inheritance:
    :member-order: bysource

Position
--------

.. automodule:: pyalgotrade.strategy.position
    :members: Position
    :show-inheritance:
    :member-order: bysource
