from flask import Flask, render_template, send_file, request
import pandas as pd
import os
import plotly.express as px
import json
import io

app = Flask(__name__)

with open('data/news_data.json', 'r') as file:
    news_data = json.load(file)

@app.route('/')
def index():
    return render_template('base.html')
@app.route('/<commodity>')
def commodity(commodity):
    data_path = os.path.join('data', commodity, 'spot_price.csv')

    if not os.path.exists(data_path):
        return f"No data available for {commodity}", 404

    try:
        spot_price_data = pd.read_csv(data_path)
    except Exception as e:
        return f"Error reading data: {e}", 500

    strategy_path = os.path.join('data', commodity)
    strategies = [f.split('.csv')[0] for f in os.listdir(strategy_path) if f.endswith('.csv') and f != 'spot_price.csv']

    news = news_data.get(commodity, [])

    selected_strategy = request.args.get('strategy')

    strategy_data = []
    if selected_strategy and f"{selected_strategy}.csv" in os.listdir(strategy_path):
        try:
            df = pd.read_csv(os.path.join(strategy_path, f"{selected_strategy}.csv"))
            strategy_data = df.tail(5).fillna("N/A").to_dict('records')
        except Exception as e:
            return f"Error reading strategy data: {e}", 500

    return render_template(f'{commodity.lower()}.html',
                           commodity=commodity,
                           spot_price_data=spot_price_data.to_dict('records'),
                           news=news,
                           strategies=strategies,
                           selected_strategy=selected_strategy,
                           strategy_data=strategy_data)

@app.route('/strategy/<commodity>')
def strategy(commodity):
    selected_strategy = request.args.get('strategy')

    if not selected_strategy:
        return f"No strategy selected", 400

    strategy_file = os.path.join('data', commodity, f'{selected_strategy}.csv')

    if not os.path.exists(strategy_file):
        return f"Strategy file {selected_strategy}.csv not found", 404

    try:
        df = pd.read_csv(strategy_file)
    except Exception as e:
        return f"Error reading strategy data: {e}", 500

    tail_data = df.tail(5).fillna("N/A").to_dict('records')

    strategy_path = os.path.join('data', commodity)
    strategies = [f.split('.csv')[0] for f in os.listdir(strategy_path) if f.endswith('.csv') and f != 'spot_price.csv']

    news = news_data.get(commodity, [])

    return render_template('gold.html',
                           commodity=commodity,
                           strategies=strategies,
                           selected_strategy=selected_strategy,
                           strategy_data=tail_data,
                           news=news) 


@app.route('/plot/<commodity>')
def plot_commodity(commodity):
    data_path = os.path.join('data', commodity, 'spot_price.csv')

    if not os.path.exists(data_path):
        return "No data available", 404

    df = pd.read_csv(data_path)

    if 'Date' not in df.columns or 'Price' not in df.columns:
        return "Invalid data format", 500

    df['Date'] = df['Date'].astype(str)

    fig = px.line(df, x='Date', y='Price',
                  markers=True, line_shape='linear')

    if commodity == "Gold":
        fig.update_traces(line=dict(color='gold'))
    if commodity == "Silver":
        fig.update_traces(line=dict(color='silver'))
    if commodity == "Copper":
        fig.update_traces(line=dict(color='orangered'))
    if commodity == "Aluminium":
        fig.update_traces(line=dict(color='silver'))

    fig.update_layout(xaxis_title="Date", yaxis_title="Price",
                      template="plotly_white", margin=dict(l=40, r=40, t=40, b=40))

    img = io.BytesIO()
    fig.write_image(img, format="png")
    img.seek(0)

    return send_file(img, mimetype='image/png')


@app.route('/plot_strategy/<commodity>/<strategy>')
def plot_strategy(commodity, strategy):
    print(f"Generating plot for: {commodity}, strategy: {strategy}")
    strategy_file = os.path.join('data', commodity, f'{strategy}.csv')

    if not os.path.exists(strategy_file):
        return "No strategy data available", 404

    df = pd.read_csv(strategy_file)

    if 'entry_index' not in df.columns:
        print(df.columns)
        return "No entry_index in strategy file", 500
    if 'pnl' not in df.columns:
        print(df.columns)
        return "No pnl column in strategy file", 500
    
    df['entry_index'] = df['entry_index'].astype(str)
    df['cum_pnl'] = df['pnl'].cumsum()
    fig = px.line(df, x='entry_index', y='cum_pnl', title=f'{commodity} Strategy {strategy} pnl',
                  markers=True, line_shape='linear')

    fig.update_traces(line=dict(color='blue'))
    fig.update_layout(xaxis_title="Date", yaxis_title="pnl",
                      template="plotly_white", margin=dict(l=40, r=40, t=40, b=40))

    img = io.BytesIO()
    fig.write_image(img, format="png")
    img.seek(0)
    
    return send_file(img, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
