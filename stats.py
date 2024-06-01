import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体

import seaborn as sns
import pandas as pd
import io
import base64

def generate_img(pipe_conn, data, x_label, y_label, title, chart_type):
    try:
        x = data['x']
        y = data['y']
        df = pd.DataFrame({'x': x, 'y': y})

        plt.figure(figsize=(12,9))

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