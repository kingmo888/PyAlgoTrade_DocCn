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


def feed_iterator(feed):
    feed.start()
    try:
        while not feed.eof():
            yield feed.getNextValuesAndUpdateDS()
    finally:
        feed.stop()
        feed.join()


class BaseFeed(observer.Subject):
    """数据源基类

    :param maxLen: 每一个 :class:`pyalgotrade.dataseries.DataSeries` 驻留的最大数量。当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。
    :type maxLen: int.

    .. note::
        这是一个基类，不应该直接被调用。
    """

    def __init__(self, maxLen):
        if not maxLen > 0:
            raise Exception("Invalid maximum length")
        self.__ds = {}
        self.__event = observer.Event()
        self.__maxLen = maxLen

    def reset(self):
        keys = list(self.__ds.keys())
        self.__ds = {}
        for key in keys:
            self.registerDataSeries(key)

    # Subclasses should implement this and return the appropriate dataseries for the given key.
    @abc.abstractmethod
    def createDataSeries(self, key, maxLen):
        raise NotImplementedError()

    # Subclasses should implement this and return a tuple with two elements:
    # 1: datetime.datetime.
    # 2: dictionary or dict-like object.
    @abc.abstractmethod
    def getNextValues(self):
        raise NotImplementedError()

    def registerDataSeries(self, key):
        if key not in self.__ds:
            self.__ds[key] = self.createDataSeries(key, self.__maxLen)

    def getNextValuesAndUpdateDS(self):
        dateTime, values = self.getNextValues()
        if dateTime is not None:
            for key, value in list(values.items()):
                # Get or create the datseries for each key.
                try:
                    ds = self.__ds[key]
                except KeyError:
                    ds = self.createDataSeries(key, self.__maxLen)
                    self.__ds[key] = ds
                ds.appendWithDateTime(dateTime, value)
        return (dateTime, values)

    def __iter__(self):
        return feed_iterator(self)

    def getNewValuesEvent(self):
        """当一个新的值可用时，新的事件将被触发.
        订阅一个可调用对象需要两个参数：

         1. 一个 :class:`datetime.datetime` 实例。
         2. 新的值。
        """
        return self.__event

    def dispatch(self):
        dateTime, values = self.getNextValuesAndUpdateDS()
        if dateTime is not None:
            self.__event.emit(dateTime, values)
        return dateTime is not None

    def getKeys(self):
        return list(self.__ds.keys())

    def __getitem__(self, key):
        """返回给定key的 :class:`pyalgotrade.dataseries.DataSeries` """
        return self.__ds[key]

    def __contains__(self, key):
        """如果给定的 :class:`pyalgotrade.dataseries.DataSeries` 类型的key有效时，返回True。"""
        return key in self.__ds
