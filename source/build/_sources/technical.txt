technical -- 技术指标
=================================

.. automodule:: pyalgotrade.technical
    :members: EventWindow, EventBasedFilter
    :show-inheritance:

例子
-------
下面的这个例子演示了如何结合 :class:`EventWindow` 和  :class:`EventBasedFilter` 来计算一个指标：

.. literalinclude:: ../samples/technical-1.py

输出内容如下:

.. literalinclude:: ../samples/technical-1.output

移动平均线
---------------

.. automodule:: pyalgotrade.technical.ma
    :members: SMA, EMA, WMA
    :show-inheritance:

.. automodule:: pyalgotrade.technical.vwap
    :members: VWAP
    :show-inheritance:

动量指标
-------------------

.. automodule:: pyalgotrade.technical.macd
    :members: MACD
    :show-inheritance:

.. automodule:: pyalgotrade.technical.rsi
    :members: RSI
    :show-inheritance:

.. automodule:: pyalgotrade.technical.stoch
    :members: StochasticOscillator
    :show-inheritance:

.. automodule:: pyalgotrade.technical.roc
    :members: RateOfChange
    :show-inheritance:

其他指标
----------------

.. automodule:: pyalgotrade.technical.atr
    :members: ATR
    :show-inheritance:

.. automodule:: pyalgotrade.technical.bollinger
    :members: BollingerBands
    :show-inheritance:

.. automodule:: pyalgotrade.technical.cross
    :members: cross_above, cross_below
    :show-inheritance:

.. automodule:: pyalgotrade.technical.cumret
    :members: CumulativeReturn
    :show-inheritance:

.. automodule:: pyalgotrade.technical.highlow
    :members: High, Low
    :show-inheritance:

.. automodule:: pyalgotrade.technical.hurst
    :members: HurstExponent
    :show-inheritance:

.. automodule:: pyalgotrade.technical.linebreak
    :members: Line, LineBreak
    :show-inheritance:

.. automodule:: pyalgotrade.technical.linreg
    :members: LeastSquaresRegression, Slope
    :show-inheritance:

.. automodule:: pyalgotrade.technical.stats
    :members: StdDev, ZScore
    :show-inheritance:

