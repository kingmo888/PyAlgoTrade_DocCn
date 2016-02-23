broker -- 订单管理类
==================================

基类和模块
------------------------

.. automodule:: pyalgotrade.broker
    :members: Order, MarketOrder, LimitOrder, StopOrder, StopLimitOrder, OrderExecutionInfo, Broker
    :member-order: bysource
    :show-inheritance:

回测模块和类
------------------------------

.. automodule:: pyalgotrade.broker.backtesting
    :members: Commission, NoCommission, FixedPerTrade, TradePercentage, Broker
    :show-inheritance:

.. automodule:: pyalgotrade.broker.slippage
    :members: SlippageModel, NoSlippage, VolumeShareSlippage
    :show-inheritance:

.. automodule:: pyalgotrade.broker.fillstrategy
    :members: FillStrategy, DefaultStrategy
    :show-inheritance:
