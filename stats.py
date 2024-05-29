from flask import jsonify
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64

def GenerateImg():
    x = [1, 2, 3, 4, 5]
    y = [2, 3, 5, 7, 11]
    data = pd.DataFrame({'x': x, 'y': y})

    sns.lineplot(x='x', y='y', data=data)
    plt.title("Simple Line Plot with Seaborn")
    plt.xlabel("X Axis")
    plt.ylabel("Y Axis")

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # 将图片转换为 base64 编码的字符串然后返回
    img_base64 = base64.b64encode(img.getvalue()).decode()
    return jsonify({'img_base64': img_base64})
