import os
import pandas as pd
import numpy as np
import pymysql
import settings,utils
from datetime import datetime


COLUMNS_CHART_DATA = ['date', 'open', 'high', 'low', 'close', 'volume']

COLUMNS_TRAINING_DATA_V1 = [
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
]

COLUMNS_TRAINING_DATA_V1_1 = COLUMNS_TRAINING_DATA_V1 + [
    'inst_lastinst_ratio', 'frgn_lastfrgn_ratio',
    'inst_ma5_ratio', 'frgn_ma5_ratio',
    'inst_ma10_ratio', 'frgn_ma10_ratio',
    'inst_ma20_ratio', 'frgn_ma20_ratio',
    'inst_ma60_ratio', 'frgn_ma60_ratio',
    'inst_ma120_ratio', 'frgn_ma120_ratio',
]

COLUMNS_TRAINING_DATA_V2 = ['per', 'pbr', 'roe'] + COLUMNS_TRAINING_DATA_V1 + [
    'market_kospi_ma5_ratio', 'market_kospi_ma20_ratio', 
    'market_kospi_ma60_ratio', 'market_kospi_ma120_ratio', 
    'bond_k3y_ma5_ratio', 'bond_k3y_ma20_ratio', 
    'bond_k3y_ma60_ratio', 'bond_k3y_ma120_ratio',
]



def preprocess(data, ver='v1'):
    windows = [5, 10, 20, 60, 120]
    for window in windows:
        data[f'close_ma{window}'] = data['close'].rolling(window=window,min_periods=1).mean()
        data[f'volume_ma{window}'] = data['volume'].rolling(window=window,min_periods=1).mean()
        data[f'close_ma{window}_ratio'] = \
            (data['close'] - data[f'close_ma{window}']) / data[f'close_ma{window}']
        data[f'volume_ma{window}_ratio'] = \
            (data['volume'] - data[f'volume_ma{window}']) / data[f'volume_ma{window}']
    
    data['open_lastclose_ratio'] = np.zeros(len(data))
    data.loc[1:, 'open_lastclose_ratio'] = \
        (data['open'][1:].values - data['close'][:-1].values) / data['close'][:-1].values
    data['high_close_ratio'] = (data['high'].values - data['close'].values) / data['close'].values
    data['low_close_ratio'] = (data['low'].values - data['close'].values) / data['close'].values
    data['close_lastclose_ratio'] = np.zeros(len(data))
    data.loc[1:, 'close_lastclose_ratio'] = \
        (data['close'][1:].values - data['close'][:-1].values) / data['close'][:-1].values
    data['volume_lastvolume_ratio'] = np.zeros(len(data))
    data.loc[1:, 'volume_lastvolume_ratio'] = (
        (data['volume'][1:].values - data['volume'][:-1].values) 
        / data['volume'][:-1].replace(to_replace=0, method='ffill')\
            .replace(to_replace=0, method='bfill').values
    )

    if ver == 'v1.1':
        for window in windows:
            data[f'inst_ma{window}'] = data['close'].rolling(window=window,min_periods=1).mean()
            data[f'frgn_ma{window}'] = data['volume'].rolling(window=window,min_periods=1).mean()
            data[f'inst_ma{window}_ratio'] = \
                (data['close'] - data[f'inst_ma{window}']) / data[f'inst_ma{window}']
            data[f'frgn_ma{window}_ratio'] = \
                (data['volume'] - data[f'frgn_ma{window}']) / data[f'frgn_ma{window}']
        data['inst_lastinst_ratio'] = np.zeros(len(data))
        data.loc[1:, 'inst_lastinst_ratio'] = (
            (data['inst'][1:].values - data['inst'][:-1].values)
            / data['inst'][:-1].replace(to_replace=0, method='ffill')\
                .replace(to_replace=0, method='bfill').values
        )
        data['frgn_lastfrgn_ratio'] = np.zeros(len(data))
        data.loc[1:, 'frgn_lastfrgn_ratio'] = (
            (data['frgn'][1:].values - data['frgn'][:-1].values)
            / data['frgn'][:-1].replace(to_replace=0, method='ffill')\
                .replace(to_replace=0, method='bfill').values
        )

    return data


def load_data(code, date_from, date_to, ver='v1'):
    if ver in ['v1', 'v1.1', 'v2']:
        return load_data_v1_v2(code, date_from, date_to, ver)
    else:
        print("### [data_manger][load_data] Error ###")
        exit(0)


def load_data_v1_v2(code, date_from, date_to, ver='v1'):
    header = None if ver == 'v1' else 0
    
    # 코드 교체
    #df = pd.read_csv(
    #    os.path.join(settings.BASE_DIR, 'data', ver, f'{code}.csv'),
    #    thousands=',', header=header, converters={'date': lambda x: str(x)})
    conn=""
    try:
        conn=pymysql.connect(host="127.0.0.1", user="root", password="비밀번호", db="testcapstone", charset="utf8")
    except:
        print("### [Failed][data_manager.py][load_data_v1_v2] DB: testcapstone ###]")
        exit(0)
    
    cur=conn.cursor()
    cur.execute(f"SELECT * FROM daily_chart WHERE code={code}")
    result=cur.fetchall()
    df=pd.DataFrame(result)
    
    conn.close()

    #print(df.shape)
    #print(df.head(5))
    
    if ver == 'v1':
        df.columns = ['code', 'date', 'time', 'open', 'high', 'low', 'close', 'volume']

    # 날짜 오름차순 정렬
    #df = df.sort_values(by='date').reset_index(drop=True)

    # 데이터 전처리
    df = preprocess(df)
    #print(df.head(5))
    #print()
    
    # 기간 필터링
    df['date'] = df['date'].replace('-','')
    #print(type(df['date'][0]))
    #print(type(date_from))
    date_from=datetime.strptime(date_from,'%Y%m%d').date()
    date_to=datetime.strptime(date_to,'%Y%m%d').date()
    df = df[(df['date'] >= date_from) & (df['date'] <= date_to)]
    df = df.fillna(method='ffill').reset_index(drop=True)

    # 차트 데이터 분리
    chart_data = df[COLUMNS_CHART_DATA]

    # 학습 데이터 분리
    training_data = None
    if ver == 'v1':
        training_data = df[COLUMNS_TRAINING_DATA_V1]
    elif ver == 'v1.1':
        training_data = df[COLUMNS_TRAINING_DATA_V1_1]
    elif ver == 'v2':
        df.loc[:, ['per', 'pbr', 'roe']] = df[['per', 'pbr', 'roe']].apply(lambda x: x / 100)
        training_data = df[COLUMNS_TRAINING_DATA_V2]
        training_data = training_data.apply(np.tanh)
    else:
        raise Exception('Invalid version.')
    
    #print(training_data)
    return chart_data, training_data.values

"""
if __name__=="__main__":
    a,b=load_data('005930','20200101',utils.get_today_str())
    print(a)
    print(b)
"""