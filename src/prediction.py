import pandas as pd
import numpy as np
import math
import pandas_datareader as pdr
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
import matplotlib.pyplot as plt

def preprocessing():
    # read file
    df = pd.read_excel('PQ2MON - Orders - Weeks -1 to -109 (1).xls.xlsx')
    
    # fill empty cells
    df['Shipper Region3'].fillna('PQ-NaN', inplace=True)
    df.loc[df['Consignee Region3'].isna() & df['Lane ID - City to City'].str.split(' to ').str[1].str.contains('PQ'), 'Consignee Region3'] = 'PQ'
    df['Consignee Region3'].fillna('UNKOWN-NaN', inplace=True)
    
    # eliminate unrelated columns
    df.drop('Client Grouping1', inplace=True, axis=1)
    df.drop('Customer Group', inplace=True, axis=1)
    df.drop('Requested Mode', inplace=True, axis=1)
    df.drop('Lane ID - City to City', inplace=True, axis=1)
    df.drop('Order #', inplace=True, axis=1)
    df.drop('Avg. Weekly Frequency', inplace=True, axis=1)

    # extract record regarding 'PQ' region only
    df = df[np.logical_or(df['Shipper Region3'].str.contains('PQ'), df['Consignee Region3'].str.contains('PQ'))]
    df = df.sort_values(by=['Start Date'])
    # print(df.info())

    # find outbound freight in PQ region
    df_start = df[df['Shipper Region3'].str.contains('PQ')]
    grouped_df_start = df_start.groupby('Start Date')
    outbound_priority_list = grouped_df_start['Priority'].apply(list)
    outbound_trailer_class_list = grouped_df_start['Requested Trailer Class'].apply(list)
    outbound = grouped_df_start.size()
    df_combine_start = pd.concat([outbound_priority_list, outbound_trailer_class_list, outbound],axis=1)
    df_combine_start = df_combine_start.set_axis(['outbound_priority_list', 'outbound_trailer_class_list', 'outbound'], axis=1)
    # print(df_combine_start)

    # find inbound freight in PQ region
    df_end = df[df['Consignee Region3'].str.contains('PQ')]
    grouped_df_end = df_end.groupby('Completion Date')
    inbound_priority_list = grouped_df_end['Priority'].apply(list)
    inbound_trailer_class_list = grouped_df_end['Requested Trailer Class'].apply(list)
    inbound = grouped_df_end.size()
    df_combine_end = pd.concat([inbound_priority_list, inbound_trailer_class_list, inbound],axis=1)
    df_combine_end = df_combine_end.set_axis(['inbound_priority_list', 'inbound_trailer_class_list', 'inbound'], axis=1)
    # print(df_combine_end)

    # inbound and outbound information for all dates
    df_final = pd.concat([df_combine_start, df_combine_end],axis=1)
    # print(df_final)

    df_final['inbound'] = df_final['inbound'].fillna(0, downcast='infer')
    df_final['outbound'] = df_final['outbound'].fillna(0, downcast='infer')
    df_final['balance_level'] = df_final['inbound'] - df_final['outbound']

    print(df_final['balance_level'].std())
    df_final.to_excel("BT_data_with_lists.xlsx", sheet_name='BisonTransport_data')  

# confusion matrix, TP, TN, FP, FN
def conf_matrix(df):
    result = [0, 0, 0, 0] #TP, TN, FP, FN
    acceptable_range = 10
    for i in range(1, len(df)):
        if df['cbalance_level'].values[i] - df['cbalance_level'].values[i-1] >= acceptable_range:
            if df['predictions'].values[i] - df['predictions'].values[i-1] >= acceptable_range:
                result[0] += 1 # both big growth
            else:
                result[1] += 1 # not detected
        elif df['cbalance_level'].values[i] - df['cbalance_level'].values[i-1] <= -acceptable_range:
            if df['predictions'].values[i] - df['predictions'].values[i-1] <= -acceptable_range:
                result[0] += 1 # both big reduction
            else:
                result[3] += 1 # not dected
        else:
            if abs(df['predictions'].values[i] - df['predictions'].values[i-1]) < acceptable_range:
                result[0] += 1 # both stable
            else:
                result[2] += 1 # not dected
                
    return result

def prediction():
    FILE_NAME = "BT_data_with_lists.xlsx"
    df = pd.read_excel(FILE_NAME)
    df["cbalance_level"] = df["balance_level"].cumsum()

    # show original imbalance graph
    # plt.figure(figsize=(15,8))
    # plt.title('original cumulative imbalance_level')
    # plt.plot(df['cbalance_level'])
    # plt.xlabel('Date')
    # plt.show()

    # only get cbalance_level
    data = df.filter(['cbalance_level'])
    dataset = data.values
    # len(dataset), 768

    # 70% training and 30% testing
    training_data_size = math.ceil(len(dataset)*.70)
    # normalize data
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(dataset)
    # specific the shape of input, 60 observation of the sample
    train_data = scaled_data[0:training_data_size, :]
    x_train = []
    y_train = []
    for i in range(60, len(train_data)):
        x_train.append(train_data[i-60:i,0])
        y_train.append(train_data[i,0])
    #     if i<=60:
    #         print(x_train)
    #         print(y_train)
            
    x_train, y_train = np.array(x_train), np.array(y_train)
    # LSTM: input 3d - number of shapes, number of steps, number of features
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1],1))

    # using sequential to build LSTM model
    regressor = Sequential()

    # input 4 LSTM layers 
    regressor.add(LSTM(units = 50, return_sequences = True, input_shape = (x_train.shape[1], 1)))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50))
    regressor.add(Dropout(0.2))

    # output layer
    regressor.add(Dense(units = 1))

    regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')
    regressor.fit(x_train, y_train, epochs = 50, batch_size = 32)

    # ERROR RATE TEST
    # history = regressor.fit(x_train, y_train, epochs = 50, batch_size = 32)
    # plt.plot(history.history['loss'])
    # plt.title('model train vs validation loss')
    # plt.ylabel('loss')
    # plt.xlabel('epoch')
    # plt.legend(['train', 'validation'], loc='upper right')
    # plt.show()

    test_data = scaled_data[training_data_size - 60: ,:]
    x_test = []

    for i in range(60, len(test_data)):
        x_test.append(test_data[i-60:i,0])

    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0],x_test.shape[1],1))

    predictions = regressor.predict(x_test)
    predictions = scaler.inverse_transform(predictions)

    valid = data[training_data_size:]
    valid['predictions'] = predictions

    result = conf_matrix(valid)
    TP, TN, FP, FN = result[:]
    accuracy = (TP + TN)/(TP + TN + FP + FN)
    print("The prediction accuray: ", accuracy)

    train = data[:training_data_size]
    valid = data[training_data_size:]
    valid['predictions'] = predictions

    #plt the prediction result
    plt.figure(figsize=(16,8))
    plt.title('Model LSTM - prediction')
    plt.xlabel('Dates', fontsize=18)
    plt.ylabel('Cumilative imbalance level', fontsize=18)
    plt.plot(train['cbalance_level'])
    plt.plot(valid[['cbalance_level','predictions']])
    plt.legend(['Train', 'Val', 'predictions'], loc='upper left')
    plt.show()

preprocessing()
prediction()