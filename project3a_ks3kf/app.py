from flask import Flask, render_template, request
import os
import datetime
import requests
import pygal
import csv

app = Flask(__name__)

# Alpha Vantage API key
api_key = '8FCYBQQE0XDXJWDC'

# Add a route to fetch stock symbols
@app.route('/get_stock_symbols')
def get_stock_symbols():
    symbols = []
    with open('stocks.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        symbols = [row[0] for row in reader if row]
    return {'symbols': symbols}

def get_time_series_key(function):
    time_series_keys = {
        'TIME_SERIES_DAILY': 'Time Series (Daily)',
        'TIME_SERIES_WEEKLY': 'Weekly Time Series',
        'TIME_SERIES_MONTHLY': 'Monthly Time Series',
        'TIME_SERIES_INTRADAY': 'Time Series (60min)'
    }
    return time_series_keys.get(function, 'Time Series (Daily)')  # Default to daily if function is not recognized


def retrieve_data(function: str, symbol: str, api_key: str, start_date, end_date) -> dict:
    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    time_series_key = str(get_time_series_key(function))

    if response.status_code == 200:
        data = response.json()
        time_series = data.get(time_series_key)
        filtered_data = {date: values for date, values in time_series.items() if start_date <= date <= end_date}
        return {time_series_key: filtered_data}
    else:
        print("ERROR: failed to retrieve data")
        return None

def generate_chart(data, chart_type, function, symbol, start_date, end_date):
    time_series_key = get_time_series_key(function)
    chart_data = data[time_series_key]
    
    # Create the chart based on the chart_type
    if chart_type == '2':
        chart = pygal.Line(x_label_rotation=20, show_minor_x_labels=True)
    elif chart_type == '1':
        chart = pygal.Bar(x_label_rotation=20, show_minor_x_labels=True)
    else:
        return None  # If the chart type is not recognized, return None
    
    # Set the title and labels for the chart
    chart.title = f'{symbol} Stock Data: {start_date} to {end_date}'
    chart.x_labels = list(chart_data.keys())
    
    # Add the data to the chart
    chart.add('Open', [float(day['1. open']) for day in chart_data.values()])
    chart.add('High', [float(day['2. high']) for day in chart_data.values()])
    chart.add('Low', [float(day['3. low']) for day in chart_data.values()])
    chart.add('Close', [float(day['4. close']) for day in chart_data.values()])
    
    # Set the file path for the SVG chart file
    chart_file_name = f'{symbol}_{start_date}_to_{end_date}.svg'
    chart_file_path = f'static/{chart_file_name}'

    # Save the chart as an SVG file to the static directory
    chart.render_to_file(chart_file_path)

    # Return the relative path to the SVG file
    return chart_file_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        chart_choice = request.form['chart_choice']
        time_series_choice = request.form['time_series_choice']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        try:
            check_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            check_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

            if check_end_date < check_start_date:
                return render_template('index.html', error="End date cannot be before the begin date.")

            time_series_functions = {
                '1': 'TIME_SERIES_INTRADAY',
                '2': 'TIME_SERIES_DAILY',
                '3': 'TIME_SERIES_WEEKLY',
                '4': 'TIME_SERIES_MONTHLY'
            }
            time_series_function = time_series_functions.get(time_series_choice, 'TIME_SERIES_DAILY')

            data = retrieve_data(time_series_function, stock_symbol, api_key, start_date, end_date)
            if data:
                # Note: Comment out code of another method to keep as reference, not part of code. 
                # chart_file_path = generate_chart(data, chart_choice, time_series_function, stock_symbol, start_date, end_date)
                chart = generate_chart(data, chart_choice, time_series_function, stock_symbol, start_date, end_date)
                if chart:
                    svg_data = chart.render(is_unicode=True)
                    return render_template('index.html', chart_data=svg_data)
                # if chart_file_path:
                #     return render_template('result.html', chart_path=chart_file_path)
                else:
                    return render_template('index.html', error="Failed to generate chart.")
            else:
                return render_template('index.html', error="Failed to retrieve data.")

        except ValueError:
            return render_template('index.html', error="Invalid date format. Please use YYYY-MM-DD format for the dates.")
        except Exception:
            return render_template('index.html', error="An Error Occurred.")
    return render_template('index.html', error=None)
      
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)