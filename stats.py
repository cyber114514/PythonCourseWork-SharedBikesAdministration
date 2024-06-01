import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体

import seaborn as sns
import pandas as pd
import io
import base64
from statsmodels.tsa.arima.model import ARIMA

def generate_img(pipe_conn, data, x_label, y_label, title, chart_type):
    try:
        x = data['x']
        y = data['y']
        df = pd.DataFrame({'x': x, 'y': y})

        plt.figure(figsize=(9,7))

        if chart_type == 'line':
            sns.lineplot(x='x', y='y', data=df)
        elif chart_type == 'bar':
            sns.barplot(x='x', y='y', data=df)
        elif chart_type == 'scatter':
            sns.scatterplot(x='x', y='y', data=df)
        elif chart_type == 'hist':
            sns.histplot(df['y'])
        elif chart_type == 'box':
            sns.boxplot(y='y', data=df)
        else:
            sns.lineplot(x='x', y='y', data=df)

        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)

        img_base64 = base64.b64encode(img.getvalue()).decode()
        pipe_conn.send(img_base64)
        pipe_conn.close()

    except Exception as e:
        pipe_conn.send("")
        pipe_conn.close()
        raise e
    
def do_predict(data):
    try:
        df = pd.DataFrame({'x': data['x'], 'y': data['y']})
        df['x'] = pd.to_datetime(df['x'])
        df.set_index('x', inplace=True)

        # 使用 ARIMA 模型进行预测
        model = ARIMA(df['y'], order=(5, 1, 0))  # (p, d, q) 这里是一个简单的 ARIMA 模型参数
        model_fit = model.fit()
        forecast_steps = 30
        forecast = model_fit.forecast(steps=forecast_steps)[0]

        last_date = df.index[-1]
        forecast_dates = [last_date + pd.Timedelta(days=i) for i in range(1, forecast_steps + 1)]
        forecast_data = {'x': forecast_dates, 'y': forecast.tolist()}

        return forecast_data
    
    except Exception as e:
        return ''