均线交叉择时
=============================================


This example is inspired on the Market Timing / GTAA model described in:
 * http://mebfaber.com/timing-model/
 * http://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461

The stragegy supports analyzing more than one instrument per asset class, and selects the one that has highest
returns in the last month.

.. literalinclude:: ../samples/market_timing.py

本例输出结果如下:

.. literalinclude:: ../samples/market_timing.output

最终结果绘制如下图所示:

.. image:: ../samples/market_timing.png
