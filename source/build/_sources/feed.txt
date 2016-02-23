feed -- 数据源基类
===================

Feeds 是将时间序列抽象化
当这些在事件调度循环时，会推送一个新的可用数据。
When these are included in the event dispatch loop, they emit an event as new data is available.
Feeds are also responsible for updating the :class:`pyalgotrade.dataseries.DataSeries` associated 
with each piece of data that the feed provides.

**当前位置是关于数据源基类的，要了解bar的数据源请查阅：** :ref:`barfeed-label` **板块.**

.. automodule:: pyalgotrade.feed
    :members: BaseFeed
    :special-members:
    :exclude-members: __weakref__
    :show-inheritance:

CSV 支持
-----------

.. automodule:: pyalgotrade.feed.csvfeed
    :members: Feed
    :special-members:
    :exclude-members: __weakref__
    :show-inheritance:

CSV 支持的例子
-------------------
一个带有以下格式的文件 ::

    Date,USD,GBP,EUR
    2013-09-29,1333.0,831.203,986.75
    2013-09-22,1349.25,842.755,997.671
    2013-09-15,1318.5,831.546,993.969
    2013-09-08,1387.0,886.885,1052.911
    .
    .
    .

像这样引入并使用:

.. literalinclude:: ../samples/csvfeed_1.py

输出结果如下:

.. literalinclude:: ../samples/csvfeed_1.output

