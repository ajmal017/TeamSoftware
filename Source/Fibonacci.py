import yfinance as yf
from dateutil import parser
import dateutil.relativedelta
from matplotlib import pyplot as plt
from datetime import *
import socket

stock_code = "MSFT"
end_date = "2020/04/07"

class Dataset:

    def get_data(self):
        global stock_code
        global end_date

        #raise exception if no stock code is entered
        if len(end_date) == 0:
            raise ValueError("End date is missing")

        # parse current date in the right format
        # end_date = date.today()
        end_date = parser.parse(end_date, dayfirst=True)

        # minus 6 months from current date and convert to correct format
        start_date = end_date - dateutil.relativedelta.relativedelta(months=6)
        start_date = (start_date.strftime("%Y-%m-%d"))

        # convert current date to correct format
        end_date = (end_date.strftime("%Y-%m-%d"))
        # print (end_date)
        # print (self.DataSet_Obj.start_date)

        #raise exception if no stock code is entered
        if len(stock_code) == 0:
            raise ValueError("Enter a stock code")

        # Retrieve stock data
        stock_data = yf.download(stock_code, start_date, end_date)

        return stock_data

class Prepare_Data:

    global stock_code
    global end_date

    DataSet_Obj = Dataset()

    df = None
    level_1 = None
    level_2 = None
    level_3 = None
    minimum_price = None
    maximum_price = None

    def retrive_dataset(self):
        self.df = self.DataSet_Obj.get_data()
        # raise exception if no data exists
        if len(self.df) == 0:
            raise ValueError("No data found, please try another stock")

    def calculate_fib(self):

        self.minimum_price = self.df.Close.min()
        self.maximum_price = self.df.Close.max()

        #calculate Fibonacci levels (using golden ratios)
        diff = self.maximum_price - self.minimum_price
        self.level1 = self.maximum_price - 0.236 * diff
        self.level2 = self.maximum_price - 0.382 * diff
        self.level3 = self.maximum_price - 0.618 * diff

    def graphing(self):
        plt.plot(self.df["Close"], color='black')
        plt.axhspan(self.level1, self.minimum_price, alpha=0.4, color='lightsteelblue')
        plt.axhspan(self.level2, self.level1, alpha=0.5, color='papayawhip')
        plt.axhspan(self.level3, self.level2, alpha=0.5, color='lightgreen')
        plt.axhspan(self.maximum_price, self.level3, alpha=0.5, color='lightskyblue')
        plt.legend(['Historical Data'], loc='upper left')  # Legend
        plt.ylabel("Price")
        plt.xlabel("Date")
        plt.legend(loc=2)
        plt.show()

class Compile:

    # function to check internet conectivity by pinging Google's DNS server
    def internet_check(self, host="8.8.8.8", port=53, timeout=3):

        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            return False

    def compile_fibonacci(self):
        if self.internet_check() == 0:
            raise Exception("No internet connectivity")
        else:
            prepare_data_obj = Prepare_Data()

            prepare_data_obj.retrive_dataset()
            prepare_data_obj.calculate_fib()
            prepare_data_obj.graphing()
