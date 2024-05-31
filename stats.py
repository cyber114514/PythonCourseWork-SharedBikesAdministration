import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import seaborn as sns
import pandas as pd
import io
import base64

def generate_img(pipe_conn, data):
    try:
        x = data['x']
        y = data['y']
        df = pd.DataFrame({'x': x, 'y': y})

        sns.lineplot(x='x', y='y', data=df)
        plt.title("Data Plot from Database")
        plt.xlabel("X Axis")
        plt.ylabel("Y Axis")

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
