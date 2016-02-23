# encoding:utf-8
# PyAlgoTrade
#
# Copyright 2011-2015 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

import abc

from pyalgotrade import observer
from pyalgotrade import warninghelpers


# This class is used to prevent bugs like the one triggered in testcases.bitstamp_test:TestCase.testRoundingBug.
# Why not use decimal.Decimal instead ?
# 1: I'd have to expose this to users. They'd have to deal with decimal.Decimal and it'll break existing users.
# 2: numpy arrays built using decimal.Decimal instances have dtype=object.
class InstrumentTraits(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def roundQuantity(self, quantity):
        raise NotImplementedError()


class IntegerTraits(InstrumentTraits):
    def roundQuantity(self, quantity):
        return int(quantity)


######################################################################
# Orders
# http://stocks.about.com/od/tradingbasics/a/markords.htm
# http://www.interactivebrokers.com/en/software/tws/usersguidebook/ordertypes/basic_order_types.htm
#
# State chart:
# INITIAL           -> SUBMITTED
# INITIAL           -> CANCELED
# SUBMITTED         -> ACCEPTED
# SUBMITTED         -> CANCELED
# ACCEPTED          -> FILLED
# ACCEPTED          -> PARTIALLY_FILLED
# ACCEPTED          -> CANCELED
# PARTIALLY_FILLED  -> PARTIALLY_FILLED
# PARTIALLY_FILLED  -> FILLED
# PARTIALLY_FILLED  -> CANCELED

class Order(object):
    """订单基类.

    :param type_: 订单类型
    :type type_: :class:`Order.Type`
    :param action: 订单操作
    :type action: :class:`Order.Action`
    :param instrument: 品种标识
    :type instrument: string.
    :param quantity: 订单数量
    :type quantity: int/float.

    .. note::
        这是一个基类，不应该直接被调用

        有效 **type** 参数如下：

         * Order.Type.MARKET
         * Order.Type.LIMIT
         * Order.Type.STOP
         * Order.Type.STOP_LIMIT

        有效 **action** 参数如下：

         * Order.Action.BUY
         * Order.Action.BUY_TO_COVER
         * Order.Action.SELL
         * Order.Action.SELL_SHORT
    """

    class Action(object):
        BUY = 1
        BUY_TO_COVER = 2
        SELL = 3
        SELL_SHORT = 4

    class State(object):
        INITIAL = 1  # Initial state.
        SUBMITTED = 2  # Order has been submitted.
        ACCEPTED = 3  # Order has been acknowledged by the broker.
        CANCELED = 4  # Order has been canceled.
        PARTIALLY_FILLED = 5  # Order has been partially filled.
        FILLED = 6  # Order has been completely filled.

        @classmethod
        def toString(cls, state):
            if state == cls.INITIAL:
                return "INITIAL"
            elif state == cls.SUBMITTED:
                return "SUBMITTED"
            elif state == cls.ACCEPTED:
                return "ACCEPTED"
            elif state == cls.CANCELED:
                return "CANCELED"
            elif state == cls.PARTIALLY_FILLED:
                return "PARTIALLY_FILLED"
            elif state == cls.FILLED:
                return "FILLED"
            else:
                raise Exception("Invalid state")

    class Type(object):
        MARKET = 1
        LIMIT = 2
        STOP = 3
        STOP_LIMIT = 4

    # Valid state transitions.
    VALID_TRANSITIONS = {
        State.INITIAL: [State.SUBMITTED, State.CANCELED],
        State.SUBMITTED: [State.ACCEPTED, State.CANCELED],
        State.ACCEPTED: [State.PARTIALLY_FILLED, State.FILLED, State.CANCELED],
        State.PARTIALLY_FILLED: [State.PARTIALLY_FILLED, State.FILLED, State.CANCELED],
    }

    def __init__(self, type_, action, instrument, quantity, instrumentTraits):
        if quantity <= 0:
            raise Exception("Invalid quantity")
        self.__id = None
        self.__type = type_
        self.__action = action
        self.__instrument = instrument
        self.__quantity = quantity
        self.__instrumentTraits = instrumentTraits
        self.__filled = 0
        self.__avgFillPrice = None
        self.__executionInfo = None
        self.__goodTillCanceled = False
        self.__commissions = 0
        self.__allOrNone = False
        self.__state = Order.State.INITIAL
        self.__submitDateTime = None

    # This is to check that orders are not compared directly. order ids should be compared.
#    def __eq__(self, other):
#        if other is None:
#            return False
#        assert(False)

    # This is to check that orders are not compared directly. order ids should be compared.
#    def __ne__(self, other):
#        if other is None:
#            return True
#        assert(False)

    def getInstrumentTraits(self):
        return self.__instrumentTraits

    def getId(self):
        """
        返回订单编号.

        .. note::

            如果没提交订单，则返回None
        """
        return self.__id

    def getType(self):
        """返回订单类型. 有效订单类型如下:

         * Order.Type.MARKET
         * Order.Type.LIMIT
         * Order.Type.STOP
         * Order.Type.STOP_LIMIT
        """
        return self.__type

    def getSubmitDateTime(self):
        """当订单被提交时，返回下订单时的datetime"""
        return self.__submitDateTime

    def setSubmitted(self, orderId, dateTime):
        assert(self.__id is None or orderId == self.__id)
        self.__id = orderId
        self.__submitDateTime = dateTime

    def getAction(self):
        """返回订单操作. 有效返回订单操作如下:

         * Order.Action.BUY
         * Order.Action.BUY_TO_COVER
         * Order.Action.SELL
         * Order.Action.SELL_SHORT
        """
        return self.__action

    def getState(self):
        """返回订单状态. 有效订单状态如下:

         * Order.State.INITIAL (the initial state).
         * Order.State.SUBMITTED
         * Order.State.ACCEPTED
         * Order.State.CANCELED
         * Order.State.PARTIALLY_FILLED
         * Order.State.FILLED
        """
        return self.__state

    def isActive(self):
        """返回订单活动是否活动"""
        return self.__state not in [Order.State.CANCELED, Order.State.FILLED]

    def isInitial(self):
        """返回订单状态是否为 Order.State.INITIAL."""
        return self.__state == Order.State.INITIAL

    def isSubmitted(self):
        """返回订单状态是否为 Order.State.SUBMITTED."""
        return self.__state == Order.State.SUBMITTED

    def isAccepted(self):
        """返回订单状态是否为 Order.State.ACCEPTED."""
        return self.__state == Order.State.ACCEPTED

    def isCanceled(self):
        """返回订单状态是否为 Order.State.CANCELED."""
        return self.__state == Order.State.CANCELED

    def isPartiallyFilled(self):
        """返回订单状态是否为 Order.State.PARTIALLY_FILLED."""
        return self.__state == Order.State.PARTIALLY_FILLED

    def isFilled(self):
        """返回订单状态是否为 Order.State.FILLED."""
        return self.__state == Order.State.FILLED

    def getInstrument(self):
        """返回品种标识"""
        return self.__instrument

    def getQuantity(self):
        """返回数量."""
        return self.__quantity

    def getFilled(self):
        """返回已经成交的股票数量"""
        return self.__filled

    def getRemaining(self):
        """返回未成交的股票数量"""
        return self.__instrumentTraits.roundQuantity(self.__quantity - self.__filled)

    def getAvgFillPrice(self):
        """返回已成交的股票的均价，如果无已成交订单返回None"""
        return self.__avgFillPrice

    def getCommissions(self):
        return self.__commissions

    def getGoodTillCanceled(self):
        """Returns True if the order is good till canceled."""
        return self.__goodTillCanceled

    def setGoodTillCanceled(self, goodTillCanceled):
        """Sets if the order should be good till canceled.
        Orders that are not filled by the time the session closes will be will be automatically canceled
        if they were not set as good till canceled

        :param goodTillCanceled: True if the order should be good till canceled.
        :type goodTillCanceled: boolean.

        .. note:: 一旦提交订单将不可变。
        """
        if self.__state != Order.State.INITIAL:
            raise Exception("The order has already been submitted")
        self.__goodTillCanceled = goodTillCanceled

    def getAllOrNone(self):
        """如果订单全部成交或者撤销则返回真。"""
        return self.__allOrNone

    def setAllOrNone(self, allOrNone):
        """设置订单属性为ALL或者None。

        :param allOrNone: 布尔型 True：全部成交。
        :type allOrNone: boolean.

        .. note:: 一旦提交订单将不可变。
        """
        if self.__state != Order.State.INITIAL:
            raise Exception("The order has already been submitted")
        self.__allOrNone = allOrNone

    def addExecutionInfo(self, orderExecutionInfo):
        if orderExecutionInfo.getQuantity() > self.getRemaining():
            raise Exception("Invalid fill size. %s remaining and %s filled" % (self.getRemaining(), orderExecutionInfo.getQuantity()))

        if self.__avgFillPrice is None:
            self.__avgFillPrice = orderExecutionInfo.getPrice()
        else:
            self.__avgFillPrice = (self.__avgFillPrice * self.__filled + orderExecutionInfo.getPrice() * orderExecutionInfo.getQuantity()) / float(self.__filled + orderExecutionInfo.getQuantity())

        self.__executionInfo = orderExecutionInfo
        self.__filled = self.getInstrumentTraits().roundQuantity(self.__filled + orderExecutionInfo.getQuantity())
        self.__commissions += orderExecutionInfo.getCommission()

        if self.getRemaining() == 0:
            self.switchState(Order.State.FILLED)
        else:
            assert(not self.__allOrNone)
            self.switchState(Order.State.PARTIALLY_FILLED)

    def switchState(self, newState):
        validTransitions = Order.VALID_TRANSITIONS.get(self.__state, [])
        if newState not in validTransitions:
            raise Exception("Invalid order state transition from %s to %s" % (Order.State.toString(self.__state), Order.State.toString(newState)))
        else:
            self.__state = newState

    def setState(self, newState):
        self.__state = newState

    def getExecutionInfo(self):
        """返回订单最后的执行信息。如果到目前为止一直未成交则返回None。
        这在每时每刻都可能改变，或部分成交 或全部成交。（？？）

        :rtype: :class:`OrderExecutionInfo`.
        """
        return self.__executionInfo

    # Returns True if this is a BUY or BUY_TO_COVER order.
    def isBuy(self):
        return self.__action in [Order.Action.BUY, Order.Action.BUY_TO_COVER]

    # Returns True if this is a SELL or SELL_SHORT order.
    def isSell(self):
        return self.__action in [Order.Action.SELL, Order.Action.SELL_SHORT]


class MarketOrder(Order):
    """市价订单基类.

    .. note::

        这是一个基类，不应该直接被调用
    """

    def __init__(self, action, instrument, quantity, onClose, instrumentTraits):
        Order.__init__(self, Order.Type.MARKET, action, instrument, quantity, instrumentTraits)
        self.__onClose = onClose

    def getFillOnClose(self):
        """如果订单尽可能的接近收盘价成交，返回True。 (Market-On-Close order)."""
        return self.__onClose


class LimitOrder(Order):
    """限价订单基类

    .. note::

        这是一个基类，不应该直接被调用
    """

    def __init__(self, action, instrument, limitPrice, quantity, instrumentTraits):
        Order.__init__(self, Order.Type.LIMIT, action, instrument, quantity, instrumentTraits)
        self.__limitPrice = limitPrice

    def getLimitPrice(self):
        """返回限价."""
        return self.__limitPrice


class StopOrder(Order):
    """停损单基类.

    .. note::

        这是一个基类，不应该直接被调用.
    """

    def __init__(self, action, instrument, stopPrice, quantity, instrumentTraits):
        Order.__init__(self, Order.Type.STOP, action, instrument, quantity, instrumentTraits)
        self.__stopPrice = stopPrice

    def getStopPrice(self):
        """返回停损价."""
        return self.__stopPrice


class StopLimitOrder(Order):
    """限价停损单基类.

    .. note::

        这是一个基类，不应该直接被调用
    """

    def __init__(self, action, instrument, stopPrice, limitPrice, quantity, instrumentTraits):
        Order.__init__(self, Order.Type.STOP_LIMIT, action, instrument, quantity, instrumentTraits)
        self.__stopPrice = stopPrice
        self.__limitPrice = limitPrice

    def getStopPrice(self):
        """返回停损价."""
        return self.__stopPrice

    def getLimitPrice(self):
        """返回限价."""
        return self.__limitPrice


class OrderExecutionInfo(object):
    """一个订单的执行信息"""
    def __init__(self, price, quantity, commission, dateTime):
        self.__price = price
        self.__quantity = quantity
        self.__commission = commission
        self.__dateTime = dateTime

    def __str__(self):
        return "%s - Price: %s - Amount: %s - Fee: %s" % (self.__dateTime, self.__price, self.__quantity, self.__commission)

    def getPrice(self):
        """Returns the fill price."""
        return self.__price

    def getQuantity(self):
        """返回数量"""
        return self.__quantity

    def getCommission(self):
        """返回应用的手续费"""
        return self.__commission

    def getDateTime(self):
        """返回订单被执行时的 :class:`datatime.datetime` """
        return self.__dateTime


class OrderEvent(object):
    class Type:
        ACCEPTED = 1  # Order has been acknowledged by the broker.
        CANCELED = 2  # Order has been canceled.
        PARTIALLY_FILLED = 3  # Order has been partially filled.
        FILLED = 4  # Order has been completely filled.

    def __init__(self, order, eventyType, eventInfo):
        self.__order = order
        self.__eventType = eventyType
        self.__eventInfo = eventInfo

    def getOrder(self):
        return self.__order

    def getEventType(self):
        return self.__eventType

    # This depends on the event type:
    # ACCEPTED: None
    # CANCELED: A string with the reason why it was canceled.
    # PARTIALLY_FILLED: An OrderExecutionInfo instance.
    # FILLED: An OrderExecutionInfo instance.
    def getEventInfo(self):
        return self.__eventInfo


######################################################################
# Base broker class
class Broker(observer.Subject, metaclass=abc.ABCMeta):
    """经纪商基类.

    .. note::

        这是一个基类，不应该直接被调用
    """

    def __init__(self):
        self.__orderEvent = observer.Event()

    def notifyOrderEvent(self, orderEvent):
        self.__orderEvent.emit(self, orderEvent)

    # Handlers should expect 2 parameters:
    # 1: broker instance
    # 2: OrderEvent instance
    def getOrderUpdatedEvent(self):
        return self.__orderEvent

    @abc.abstractmethod
    def getInstrumentTraits(self, instrument):
        raise NotImplementedError()

    @abc.abstractmethod
    def getCash(self, includeShort=True):
        """
        返回可用的现金。

        :param includeShort: 是否包含空头仓位的现金（译者注：国际特有）
        :type includeShort: boolean.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def getShares(self, instrument):
        """返回一个品种的股数"""
        raise NotImplementedError()

    @abc.abstractmethod
    def getPositions(self):
        """返回一个品种和股数相对应的字典"""
        raise NotImplementedError()

    @abc.abstractmethod
    def getActiveOrders(self, instrument=None):
        """返回仍然活动的连续订单。

        :param instrument: 品种标识。可选参数。若非空，则只返回给定品种的活动订单
        :type instrument: string.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def submitOrder(self, order):
        """提交订单

        :param order: 需要提交的订单
        :type order: :class:`Order`.

        .. note::
            * 提交后订单状态变为SUBMITTED状态，事件并不能引发这种转换。（？？？）
            * 相同的订单提交2次将会引发一个异常。
        """
        raise NotImplementedError()

    def placeOrder(self, order):
        # Deprecated since v0.16
        warninghelpers.deprecation_warning("placeOrder will be deprecated in the next version. Please use submitOrder instead.", stacklevel=2)
        return self.submitOrder(order)

    @abc.abstractmethod
    def createMarketOrder(self, action, instrument, quantity, onClose=False):
        """创建市价单.
        市价订单是按市场当时最优价或市价立即购买或出售一定数量股票合约的指令。一般来说，这种类型的订单将立即执行。然而市价单的成交价往往不能确定。


        :param action: 订单操作.
        :type action: Order.Action.BUY, or Order.Action.BUY_TO_COVER, or Order.Action.SELL or Order.Action.SELL_SHORT.
        :param instrument: 品种标识.
        :type instrument: string.
        :param quantity: 订单数量.
        :type quantity: int/float.
        :param onClose: 默认为假。若需要尽可能的贴近收盘价成交(Market-On-Close order)则应为True.
        :type onClose: boolean.
        :rtype: 一个 :class:`MarketOrder` 子类.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def createLimitOrder(self, action, instrument, limitPrice, quantity):
        """创建限价单.
		限价单是一种以明确的或更优的价格来购买或出售股票的订单。
		一张限价买单只能以限价或更低的价格执行，一张限价卖单只能以限价或更高的价格执行。


        :param action: 订单操作.
        :type action: Order.Action.BUY, or Order.Action.BUY_TO_COVER, or Order.Action.SELL or Order.Action.SELL_SHORT.
        :param instrument: 品种标识.
        :type instrument: string.
        :param limitPrice: The order price.
        :type limitPrice: float
        :param quantity: 订单数量.
        :type quantity: int/float.
        :rtype: 一个 :class:`LimitOrder` 子类.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def createStopOrder(self, action, instrument, stopPrice, quantity):
        """创建停损单.
        停损单, 也被称为止损单。停损单只有当价格到达某一设定水准时才可执行的买单或卖单。这种买/卖单的目的通常是为了要降低某一现有头寸的损失。一旦触及停损的价位，便会依照下一个市价执行（尤其是在动荡的市场上更是如此）。
        当价格达到停损价时，停损单成为市价单。
        A buy stop order is entered at a stop price above the current market price. Investors generally use a buy stop order
        to limit a loss or to protect a profit on a stock that they have sold short.
        A sell stop order is entered at a stop price below the current market price. Investors generally use a sell stop order
        to limit a loss or to protect a profit on a stock that they own.

        :param action: 订单操作.
        :type action: Order.Action.BUY, or Order.Action.BUY_TO_COVER, or Order.Action.SELL or Order.Action.SELL_SHORT.
        :param instrument: 品种标识.
        :type instrument: string.
        :param stopPrice: 触发价格
        :type stopPrice: float
        :param quantity: 订单数量.
        :type quantity: int/float.
        :rtype: 一个 :class:`StopOrder` 子类.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def createStopLimitOrder(self, action, instrument, stopPrice, limitPrice, quantity):
        """Creates a Stop-Limit order.
        A stop-limit order is an order to buy or sell a stock that combines the features of a stop order and a limit order.
        Once the stop price is reached, a stop-limit order becomes a limit order that will be executed at a specified price
        (or better). The benefit of a stop-limit order is that the investor can control the price at which the order can be executed.

        :param action: 订单操作.
        :type action: Order.Action.BUY, or Order.Action.BUY_TO_COVER, or Order.Action.SELL or Order.Action.SELL_SHORT.
        :param instrument: 品种标识.
        :type instrument: string.
        :param stopPrice: The trigger price.
        :type stopPrice: float
        :param limitPrice: 限价
        :type limitPrice: float
        :param quantity: 订单数量.
        :type quantity: int/float.
        :rtype: 一个 :class:`StopLimitOrder` 子类.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def cancelOrder(self, order):
        """请求撤销一个订单。如果订单已成交将引发一个异常

        :param order: 需要撤销的订单
        :type order: :class:`Order`.
        """
        raise NotImplementedError()
