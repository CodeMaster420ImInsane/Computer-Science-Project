import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.finance import candlestick
from datetime import *

def conv_str_to_datetime(x):
    return(datetime.strptime(x, '%Y%m%d %H:%M:%S.%f'))

df = pd.read_csv('/tickData/{symbol}', names=['Symbol', 'Date_Time', 'Bid', 'Ask'], converters={'Date_Time': conv_str_to_datetime})
# Example data                Symbol      Bid      Ask
#Datetime
#2012-06-01 00:00:00.207000  EUR/USD  1.23618  1.23630
#2012-06-01 00:00:00.209000  EUR/USD  1.23618  1.23631
#2012-06-01 00:00:00.210000  EUR/USD  1.23618  1.23631
#2012-06-01 00:00:00.211000  EUR/USD  1.23623  1.23631
#2012-06-01 00:00:00.240000  EUR/USD  1.23623  1.23627
#2012-06-01 00:00:00.423000  EUR/USD  1.23622  1.23627
#2012-06-01 00:00:00.457000  EUR/USD  1.23620  1.23626
#2012-06-01 00:00:01.537000  EUR/USD  1.23620  1.23625
#2012-06-01 00:00:03.010000  EUR/USD  1.23620  1.23624
#2012-06-01 00:00:03.012000  EUR/USD  1.23620  1.23625
# Want: select time period (15 mins). When tick increased by 15 mins, the ask is the close, original bid is the open at the start of the 15 mins. do max(bid) to find high and min(bid) to find low
