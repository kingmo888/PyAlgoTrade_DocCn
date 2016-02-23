# encoding:utf-8
# PyAlgoTrade
#
# Copyright 2011-2015 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
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


class SlippageModel(object, metaclass=abc.ABCMeta):
    """交易滑点模型的基类

    .. note::
        这是一个基类，不应该直接被调用
    """

    @abc.abstractmethod
    def calculatePrice(self, order, price, quantity, bar, volumeUsed):
        """
        返回一张订单的滑价

        :param order: 将要成交的订单
        :type order: :class:`pyalgotrade.broker.Order`.
        :param price: 计算滑价前的每股价格
        :type price: float.
        :param quantity: 此时此刻这张订单的成交股数。
        :type quantity: float.
        :param bar: 当前bar.
        :type bar: :class:`pyalgotrade.bar.Bar`.
        :param volumeUsed: The volume size that was taken so far from the current bar.
        :type volumeUsed: float.
        :rtype: float.
        """
        raise NotImplementedError()


class NoSlippage(SlippageModel):
    """一个不计滑点模型."""

    def calculatePrice(self, order, price, quantity, bar, volumeUsed):
        return price


class VolumeShareSlippage(SlippageModel):
    """
    A volume share slippage model as defined in Zipline's VolumeShareSlippage model.
    The slippage is calculated by multiplying the price impact constant by the square of the ratio of the order
    to the total volume.

    Check https://www.quantopian.com/help#ide-slippage for more details.

    :param priceImpact: Defines how large of an impact your order will have on the backtester's price calculation.
    :type priceImpact: float.
    """

    def __init__(self, priceImpact=0.1):
        self.__priceImpact = priceImpact

    def calculatePrice(self, order, price, quantity, bar, volumeUsed):
        assert bar.getVolume(), "Can't use 0 volume bars with VolumeShareSlippage"

        totalVolume = volumeUsed + quantity
        volumeShare = totalVolume / float(bar.getVolume())
        impactPct = volumeShare ** 2 * self.__priceImpact
        if order.isBuy():
            ret = price * (1 + impactPct)
        else:
            ret = price * (1 - impactPct)
        return ret
