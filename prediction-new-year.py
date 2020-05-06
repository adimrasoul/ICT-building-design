import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
from func import ind, fl, fitData
warnings.filterwarnings("ignore")

data = pd.read_csv('Data_for_ARIMA.csv',sep=',',decimal=',', low_memory=False)

data = fl(data)
X = data.total_power.values.astype(float)

# amount of data in the initial window of training
training_size = 24*365*2
# number of tests to be done for which we repeat the train and test
month_days = [31,28,31,30,31,30,31,31,30,31,30,31]
#month_days = [31]
p = 8
q = 7
# fixed parameters [needed for non-stationarity of the series -> parabolic trend] but in our case is 0
d = 0
order = (p,d,q)
i = 1
best_mse, best_order = float("inf"), None
result_temp = []
_month = 0

for month in month_days:
    print("month days : ",i , month)
    test_size = month * 24
    # split train and test
    train = X[0+_month:training_size+_month]
    test = X[training_size+_month:training_size+_month + test_size]
    _month += (month * 24)

    predictions = list()
    # data for training
    history = [x for x in train]
    # for all tests
    if i == 12:
        for t in range(0, test_size):
        # new ARIMA model
            try:
                model = ARIMA(history, order=order)
                # fit it
                model_fit = model.fit(method='css', disp=0)
                # forecasted data at t+j
                output = model_fit.forecast()[0][0]

                print("Iterate number: ",t, "Value : ", output)
                # get t+1 -> sorting obs
                predictions.append(output)
                # slide over time by putting now+1 into pa st
                history.append(test[t])
                # drop first sample to use sliding window (to use expanding window, comment the following line)
                history = history[1:]
            except:
                print("* ERROR IN TRAINING THE MODEL *")
    if i == 12:
        mse = mean_squared_error(test, predictions)
        result_temp.append({"month: ": i, 'mse: ': mse})
    print(result_temp)
    df_predictions = pd.DataFrame(predictions)
    df_predictions.to_csv(str(i) + '-month.csv', index=False)
    i+=1
    #if mse < best_mse:
    #    best_mse, best_order = mse, order

#print('Best ARIMA%s MSE=%.3f' % (best_order, best_mse))
# for residuals plot

plt.figure()
result = pd.DataFrame.from_dict(result_temp)
result.to_csv('res10.csv', index=False)