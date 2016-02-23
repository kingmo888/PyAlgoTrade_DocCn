# -*- coding: utf-8 -*-
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
.. moduleauthor:: Maciej Żok <maciek.zok@gmail.com>
"""

from pyalgotrade.barfeed import csvfeed
from pyalgotrade.barfeed import common
from pyalgotrade.utils import dt
from pyalgotrade import bar
from pyalgotrade import dataseries

import datetime


######################################################################
# Google Finance CSV parser
# Each bar must be on its own line and fields must be separated by comma (,).
#
# Bars Format:
# Date,Open,High,Low,Close,Volume
#
# The csv Date column must have the following format: D-B-YY

def parse_date(date):
    # Sample: 3-Dec-05
    # This custom parsing works faster than:
    # datetime.datetime.strptime(date, "%d-%b-%y")
    month_abbr = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                  'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                  'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    date = date.split("-")
    year = int(date[2]) + 2000
    if year > datetime.datetime.today().year:
        # it's probably 20th century
        year -= 100
    month = int(month_abbr[date[1]])
    day = int(date[0])
    ret = datetime.datetime(year, month, day)
    return ret


class RowParser(csvfeed.RowParser):
    def __init__(self, dailyBarTime, frequency, timezone=None, sanitize=False):
        self.__dailyBarTime = dailyBarTime
        self.__frequency = frequency
        self.__timezone = timezone
        self.__sanitize = sanitize

    def __parseDate(self, dateString):
        ret = parse_date(dateString)
        # Time on Google Finance CSV files is empty. If told to set one, do it.
        if self.__dailyBarTime is not None:
            ret = datetime.datetime.combine(ret, self.__dailyBarTime)
        # Localize the datetime if a timezone was given.
        if self.__timezone:
            ret = dt.localize(ret, self.__timezone)
        return ret

    def getFieldNames(self):
        # It is expected for the first row to have the field names.
        return None

    def getDelimiter(self):
        return ","

    def parseBar(self, csvRowDict):
        dateTime = self.__parseDate(csvRowDict["Date"])
        close = float(csvRowDict["Close"])
        open_ = float(csvRowDict["Open"])
        high = float(csvRowDict["High"])
        low = float(csvRowDict["Low"])
        volume = float(csvRowDict["Volume"])
        adjClose = None

        if self.__sanitize:
            open_, high, low, close = common.sanitize_ohlc(open_, high, low, close)

        return bar.BasicBar(dateTime, open_, high, low, close, volume,
                            adjClose, self.__frequency)


class Feed(csvfeed.BarFeed):
    """A :class:`pyalgotrade.barfeed.csvfeed.BarFeed` that loads bars from CSV files downloaded from Google Finance.

    :param frequency: bars的频率. 当前只支持 **pyalgotrade.bar.Frequency.DAY** 类型。
    :param timezone: 默认情况下使用bars自身的时区. 详见 :mod:`pyalgotrade.marketsession`.
    :type timezone: A pytz timezone.
    :param maxLen:  :class:`pyalgotrade.dataseries.bards.BarDataSeries` 类型的值驻留的最大数量。
	    当队列已满，一旦添加新的条目进来，将会在相反位置删除对应数量的条目。.
    :type maxLen: int.

    .. note::
        Google Finance 的CSV文件中缺少时区信息。
         当多品种同时运行时:

            * 如果加载的所有品种具有相同的时区，则时区参数可以不指定。
            * 如果有任何一个加载的品种具有不同的时区，则时区参数需要设置。
    """

    def __init__(self, frequency=bar.Frequency.DAY, timezone=None, maxLen=dataseries.DEFAULT_MAX_LEN):
        if frequency not in [bar.Frequency.DAY]:
            raise Exception("Invalid frequency.")

        csvfeed.BarFeed.__init__(self, frequency, maxLen)
        self.__timezone = timezone
        self.__sanitizeBars = False

    def sanitizeBars(self, sanitize):
        self.__sanitizeBars = sanitize

    def barsHaveAdjClose(self):
        return False

    def addBarsFromCSV(self, instrument, path, timezone=None):
        """为指定的品种从格式化后的CSV文件中加载bars，同时在bar数据源中注册品种。

        :param instrument: 品种标识。
        :type instrument: string.
        :param path: CSV文件的路径
        :type path: string.
        :param timezone: The timezone to use to localize bars. 详情 :mod:`pyalgotrade.marketsession`.
        :type timezone: A pytz timezone.
        """

        if timezone is None:
            timezone = self.__timezone

        rowParser = RowParser(self.getDailyBarTime(), self.getFrequency(), timezone, self.__sanitizeBars)
        csvfeed.BarFeed.addBarsFromCSV(self, instrument, path, rowParser)
