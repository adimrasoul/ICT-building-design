# useful functions

import pandas as pd
from datetime import datetime
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
import matplotlib.pyplot as plt
#%% CONVERTING DATA FROM STRING TO DATETIME INDEX
# input: data
# output: data
def ind(data):
    time = []
    # for each index/row
    for i in range(len(data.index)):
        # reading  index
        t = data.index[i]
        # splitting day and hour
        day, hour = t.split('  ')
        # 
        timestamp = datetime.strptime(t, "%Y/%m/%d  %H:%M:%S")
        #
        time.append(timestamp)
    #
    data.index = pd.to_datetime(time)
    return data
#%% CONVERTING DATA TO FLOAT
# input: data
# output: data
def fl(data):
    # retrieving data columns
    cols = data.columns
    # for each columns
    for col in cols:
        # converting to float
        data[col] = data[col].astype(float)
    return data
#%% FITTING MISSING DATA
# input parameters: time series
# output parameters: fitted time series
def fitData(df):
    # fitting with zero, can also be done differently
    for i in np.arange(1,len(df.total_power) - 1):
        d1 = df.index[i]
        d2 = df.index[i+1]
        diff = d2.hour - d1.hour
        # EXPLORATION of the values we could have
        #print(diff)
        # if there is no missing values, go on
        if ((diff == 1) | (diff == -22) | (diff == 0)):
            pass
        # if there is a missing value
        else:
            # EXPLORATION
            #print("Inserting missing value")
            # to check if the initial and final size of df are given by missing hours
            for j in np.arange(diff):
                new = d1.replace(hour=d1.hour+j).strftime("%Y-%m-%d %H:%M:%S")
                df = df.append({'index':new,'total_power':df.total_power.mean(),'t_in':df.t_in.mean(),'t_out':df.t_out.mean(),'temp_diff':df.temp_diff.mean(),'power_heating':df.power_heating.mean(),'power_cooling':df.power_cooling.mean(),'power_electricity':df.power_electricity.mean()},ignore_index=True)
    #df = df.sort_values(by=df.index)
    return df
#%% CREATING FINAL MODEL
# input parameters: time series, training size, testing size, p-d-q values, h represents sliding window or not
# output parameters: fitted model, predictions array, test
def createModel(df, size, testLen, orde, h):
    print('Training size:', size,'h')
    print('Test size:',testLen,'h')
    # to store prediction for each lag_order
    predictions = np.zeros((1,testLen))
    # extracting time seris
    X = df.total_power.values.astype(float)
    # split train and test
    train = X[0:size]
    test = X[size:size+testLen]
    # data for training
    history = [x for x in train]
    # for all tests we want to do
    for t in range(0,testLen):
         # new ARIMA model
         model = ARIMA(history,order=orde)
         try:
             # fitting the model
             modelFit = model.fit(method='css') #mle #css
             # forecasted data at t+j
             output = modelFit.forecast()
             # get t+1
             predictions[0][t] = output[0]
         except:
             print('PROBLEM IN TRAINING THE MODEL')
         # slide over time by putting now+1 into past
         history.append(test[t])
         if (h == 0):
             # drop first sample to use sliding window
             history = history[1:]
         else:
             # we don't remove data in training sample
             pass
    return modelFit, predictions, test
#%% PREDICTING MORE THAN ONE DAY
# input parameters: time series, training size, testing size, p-d-q values, step step for prediction
# output parameters: MAPE, MSE
def modelP(df, size, testLen, orde, step):
    print('Training size:', size,'h')
    print('Test size:',testLen,'h')
    # extracting the time seris
    X = df.total_power.values.astype(float)
    # split train and test
    train = X[0:size]
    #test = X[size:size+testLen]
    test = X[size:size+step]
    # data for training
    history = [x for x in train]
    # new ARIMA model
    model = ARIMA(history,order=orde)
    # fitting the model
    modelFit = model.fit(method='css')
    # forecasted data at t+j
    output = modelFit.forecast(steps = step)[0]
    plt.figure()
    plt.plot(np.arange(step), test[0:step], label="original")
    plt.plot(np.arange(step), output, label="prediction")
    plt.title('Prediction for '+str(step)+' hours')
    plt.ylabel("Power consumption [kWh]")
    plt.xlabel("time [h]")
    plt.legend()
    mp = round(mean_absolute_error(test[0:step],output) / test.mean()*100,5)
    ms = round(mean_squared_error(test[0:step],output),5)
    print('MAPE:',mp)
    print('MSE:',ms)
    return mp,ms
