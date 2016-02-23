简介
============
PyAlgoTrade作为事件驱动型的算法交易工具，其支持:
 * 从CSV文件中获取历史数据并进行回测。
 * 通过使用 :ref:`Xignite <xignite-tutorial-label>` 和 :ref:`Bitstamp <bitstamp-tutorial-label>` 的实时数据进行模拟交易。
 * 在Bitstamp上进行实战交易。

它可以很方便的在多台计算机之间优化策略。

PyAlgoTrade基于Python2.7开发并依托于以下python库:
 * NumPy and SciPy (http://numpy.scipy.org/).：科学计算库
 * pytz (http://pytz.sourceforge.net/).
 * matplotlib (http://matplotlib.sourceforge.net/) ：绘图库
 * ws4py (https://github.com/Lawouach/WebSocket-for-Python) ：用于得到Bitstamp支持
 * tornado (http://www.tornadoweb.org/en/stable/) 用于得到Bitstamp支持.
 * tweepy (https://github.com/tweepy/tweepy) 用于得到推特支持.

因此，你需要安装上述扩展库才能使用本扩展库。

你可以通过pip来安装PyAlgoTrade: ::

    pip install pyalgotrade

译者注：0.17版本已经迁移到Python3.x上，原版只能在py27环境下运行，请谨慎升级。
down:PyAlgoTrade0.16_for_py3