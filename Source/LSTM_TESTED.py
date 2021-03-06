# Not part of GUI, only used to build .h5 model to load into LSTM.py file
#update OUTPUT_PATH to your local file location

import yfinance as yf
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.preprocessing.sequence import TimeseriesGenerator
from keras import optimizers
from keras.callbacks import ModelCheckpoint, EarlyStopping
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt

class parameters:

    time_steps = 15
    batch_size = 20
    lr = 0.00010000
    epochs = 300
    future_days = 30 #how many days to predict ahead of the last date from the training dataset

class dataset:
    stock_code = "RYCEY"
    start_date = "2005-01-01"
    end_date = "2020-04-09"

    df = yf.download(stock_code, start_date, end_date)


parameters_obj = parameters()
dataset_obj = dataset()


def create_model():
    model = Sequential()

    model.add(LSTM(100, activation='relu', input_shape=(parameters_obj.time_steps, 1), return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(60, dropout=0.0))
    model.add(Dropout(0.4))

    model.add(Dense(1, activation='sigmoid'))
    optimizer = optimizers.RMSprop(lr=parameters_obj.lr)

    model.compile(optimizer=optimizer, loss='mse')

    return model

def graphing():
    plt.figure()
    plt.plot(date_train, close_train, color='black')
    plt.plot(reduce_date_range(date_test, prediction), prediction, color='orange')
    #plt.plot(date_val, close_train_val, color='green')
    #plt.plot(date_val, close_train_val_raw, color='black')
    plt.plot(date_test, close_test, color='red')
    plt.plot(forecast_dates, forecast, color='blue')
    plt.legend(['Data', 'Prediction', 'Raw Data', 'Future Prediction'], loc='upper left')  # Legend
    plt.ylabel('Price')
    plt.xlabel('Date')
    plt.show()
    
    plt.figure()
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Val', 'Test'], loc='upper left')
    plt.show()

OUTPUT_PATH = "/Users/riteshsookun/OneDrive/Uni/Coding Projects/LSTM/new_5.67"

# check if directory already exists
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)
    print("Directory created", OUTPUT_PATH)
else:
    raise Exception("Directory already exists. Don't override.")

print(dataset_obj.df.info())

dataset_obj.df['Date'] = dataset_obj.df.index
dataset_obj.df['Date'] = pd.to_datetime(dataset_obj.df['Date'])
dataset_obj.df.set_axis(dataset_obj.df['Date'], inplace=True)
dataset_obj.df.drop(columns=['Open', 'High', 'Low', 'Adj Close', 'Volume'], inplace=True)

close_data = dataset_obj.df['Close'].values
close_data = close_data.reshape((-1,1))

# split stock_data into two datasets (training, val and test) with a 80/20(training/test) split on raw data, then
#training is split again to create val
close_train_old, close_test = train_test_split(close_data, train_size=0.8, test_size=0.2, shuffle=False)
date_train_old, date_test = train_test_split(dataset_obj.df['Date'], train_size=0.8, test_size=0.2, shuffle=False)

close_train, close_train_val = train_test_split(close_train_old, train_size=0.8, test_size=0.2, shuffle=False)
date_train, date_val = train_test_split(date_train_old, train_size=0.8, test_size=0.2, shuffle=False)

close_train_val_raw = close_train_val
print(len(close_train))
print(len(close_test))

#scale the feature MinMax, build array
x = close_train
scaler = MinMaxScaler()
x_close_train = scaler.fit_transform(x)
x_close_test = scaler.transform(close_test)


train_generator = TimeseriesGenerator(x_close_train, x_close_train, length=parameters_obj.time_steps, batch_size=parameters_obj.batch_size)
val_generator = TimeseriesGenerator(close_train_val, close_train_val, length=parameters_obj.time_steps, batch_size=parameters_obj.batch_size)
test_generator = TimeseriesGenerator(x_close_test, x_close_test, length=parameters_obj.time_steps, batch_size=parameters_obj.batch_size)

model = create_model()

es = EarlyStopping(monitor='val_loss', mode='min', verbose=1,
                   patience=40, min_delta=0.0001)

mcp = ModelCheckpoint(os.path.join(OUTPUT_PATH,
                                   "best_model.h5"), monitor='val_loss', verbose=1,
                      save_best_only=True, save_weights_only=False, mode='min', period=1)

model.fit_generator(train_generator, steps_per_epoch=len(train_generator), epochs=parameters_obj.epochs, verbose=1,
                    callbacks=[es, mcp], validation_data=val_generator)


x_close_train = x_close_train.reshape((-1))
x_close_test = x_close_test.reshape((-1))
prediction = model.predict_generator(test_generator).reshape((-1))

close_data = close_data.reshape((-1))


def predict(future_days, model):
    close_data_1 = scaler.transform(close_data.reshape(-1, 1))

    prediction_list = close_data_1[-parameters_obj.time_steps:]

    for _ in range(future_days):
        x = prediction_list[-parameters_obj.time_steps:]
        x = x.reshape((1, parameters_obj.time_steps, 1))
        out = model.predict(x)[0][0]
        prediction_list = np.append(prediction_list, out)
    prediction_list = prediction_list[parameters_obj.time_steps - 1:]

    return prediction_list


def generate_dates(future_days):
    last_date = dataset_obj.df['Date'].values[-1]
    generate_dates = pd.date_range(last_date, periods=future_days + 1).tolist()
    return generate_dates


def reduce_date_range(date_range, dataset):

    drop_rows = date_range.shape[0] - dataset.shape[0]  # find remainder
    drop_rows = date_range.shape[0] - drop_rows

    if drop_rows > 0:
        return date_range[:drop_rows]  # if remainder is present, return dataset
                                     # up to the row that fits into batch size
    else:
        return date_range


forecast = np.array(predict(parameters_obj.future_days, model)).reshape(-1, 1)
forecast_dates = generate_dates(parameters_obj.future_days)

close_train = scaler.inverse_transform(x_close_train.reshape(-1, 1))
close_test = scaler.inverse_transform(x_close_test.reshape(-1, 1))
prediction = scaler.inverse_transform(prediction.reshape(-1, 1))
forecast = scaler.inverse_transform(forecast)

graphing()






