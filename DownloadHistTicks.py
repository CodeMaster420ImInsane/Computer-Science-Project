import requests
import io
import os
from lzma import LZMADecompressor, LZMAError, FORMAT_AUTO
import struct
from datetime import timedelta, datetime, date
import pandas as pd
import gzip

def decompress_lzma(data):
    results = []
    len(data)
    while True:
        decomp = LZMADecompressor(FORMAT_AUTO, None, None)
        try:
            res = decomp.decompress(data)
        except LZMAError:
            if results:
                break  # Leftover data is not a valid LZMA/XZ stream; ignore it.
            else:
                raise  # Error on the first iteration; bail out.
        results.append(res)
        data = decomp.unused_data
        if not data:
            break
        if not decomp.eof:
            raise LZMAError("Compressed data ended before the end-of-stream marker was reached")
    return b"".join(results)

def tokenize(buffer):
    token_size = 20
    size = int(len(buffer) / token_size)
    tokens = []
    for i in range(0, size):
        tokens.append(struct.unpack('!IIIff', buffer[i * token_size: (i + 1) * token_size]))
    return tokens

def normalize(symbol, hour_datetime, ticks):
    def norm(time, ask, bid, volume_ask, volume_bid):
        #print("processing:",datetime,datetime.day,datetime.month,datetime.year,datetime.hour)
        tick_datetime = hour_datetime + timedelta(milliseconds=time)
        #date.replace(tzinfo=datetime.tzinfo("UTC"))
        point = 100000
        if symbol.lower() in ['usdrub', 'xagusd', 'xauusd'] or "jpy" in symbol.lower():
            point = 1000
            
        return tick_datetime, ask / point, bid / point, round(volume_ask * 1000000), round(volume_bid * 1000000)

    return list(map(lambda x: norm(*x), ticks))

def decompress(symbol, hour_datetime, compressed_buffer):
    if compressed_buffer.nbytes == 0:
        return compressed_buffer
    return normalize(symbol, hour_datetime, tokenize(decompress_lzma(compressed_buffer)))

def get_hour_ticks(symbol, datetime, verbose=False):
    url_info = {
        'currency': symbol,
        'year': datetime.year,
        'month': datetime.month-1, # jan = 0
        'day': datetime.day,
        'hour': datetime.hour
    }
    url = "https://www.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5".format(**url_info)
    if verbose:
        print("Fetching:",url)
    response = requests.get(url)

    local_filename = url.split('/')[-1]
    totalbits = 0
    if response.status_code == 200:
        with io.BytesIO() as f:
            download_verbose = "no data to download"
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    totalbits += 1024
                    download_verbose = "Downloaded {0:3.1f} kB".format(totalbits/1025,"KB...")
                    f.write(chunk)
            if verbose:
                print(download_verbose)
            if download_verbose != "no data to download":
                tokenised_data = decompress(symbol,datetime,f.getbuffer())
                return pd.DataFrame(tokenised_data)
            else:
                return None
# test
hour_datetime = datetime.strptime('2018-01-01T22:00:00', '%Y-%m-%dT%H:%M:%S')
data = get_hour_ticks('EURUSD', hour_datetime)
if data is None:
    print(hour_datetime,"No data")
else:
    print(hour_datetime,"row count:",len(data))
    print(data)

def download_year_ticks(symbol, year):
    # first date/time
    curr_datetime = datetime.strptime(str(year)+'-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S')

    with gzip.open("tickData/"+symbol+"/"+symbol+"_"+str(year)+"_ticks.csv.gz", "w") as gzipfile:
        gzipfile.write("time,Ask,Bid,AskVolume,BidVolume\n".encode())
        while curr_datetime.year == year:
            print("day:",curr_datetime.strftime('%Y-%m-%d'))
            for h in range(0,24):
                #print("requesting for:",curr_datetime,curr_datetime.day,curr_datetime.month,curr_datetime.year,curr_datetime.hour)
                data = get_hour_ticks(symbol, curr_datetime)
                if data is None:
                    print(curr_datetime,"No data")
                else:
                    print(curr_datetime,"row count:",len(data))
                    #data.to_csv(f, index=False, line_terminator='\n', header=False)
                    data.to_csv(gzipfile, index=False, line_terminator='\n', header=False)

                curr_datetime += timedelta(hours=1)


# run through each symbol and get 5 years tick data
#symbols = ["AUDUSD","GBPUSD","NZDUSD","USDCAD","USDCHF","USDJPY"] #EURUSD (manual)
symbols = ["GBPUSD"]
years = [2018,2019,2020,2021,2022]
years = [2023]

for symbol in symbols:
    # create dir if doesnt exist
    directory = "tickData/"+symbol
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for year in years:
        print("Starting download for: ",symbol,"@",year)
        download_year_ticks(symbol, year)

f=gzip.open('tickData/EURUSD/EURUSD_2022_ticks.csv.gz,'rb')
file_content=f.read()
print(len(file_content))

