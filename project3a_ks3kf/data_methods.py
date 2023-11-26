import requests
import json
import pygal
from pygal.style import DefaultStyle

# retrieve data from AlphaVantage's open API
def print_pretty(data: dict):
  print(json.dumps(data, indent=4))

# api_key = 'M5U4GAA5AW5TD1I1'
test_symbol = 'IBM'
test_function = 'TIME_SERIES_DAILY'
test_start_date = '2023-08-01'
test_end_date = '2023-08-31'
test_chart_type = '2'


def get_time_series_key(function):
    time_series_keys = {
        'TIME_SERIES_DAILY': 'Time Series (Daily)',
        'TIME_SERIES_WEEKLY': 'Weekly Time Series',
        'TIME_SERIES_MONTHLY': 'Monthly Time Series',
        'TIME_SERIES_INTRADAY': 'Time Series (60min)'
    }

    return time_series_keys.get(function, 'Time Series (Daily)')  # Default to daily if function is not recognized


def retrieve_data(function: str, symbol: str, api_key: str, start_date, end_date) -> dict:
    # query from API
    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    time_series_key = str(get_time_series_key(function))

    if response.status_code == 200:
        data = response.json()
        data = response.json()
        print(data)
        time_series = data.get(time_series_key)
        filtered_data = {date: values for date, values in time_series.items() if start_date <= date <= end_date}
        return {time_series_key: filtered_data}
    else:
        print("ERROR: failed to retrieve data")
        return None

# print_pretty(retrieve_data(test_function, test_symbol, api_key, test_start_date, test_end_date))

# graph data
def generate_chart(data, chart_type, function, symbol, start_date, end_date):
    # Initialize the correct chart type
    if chart_type == '1':  # bar chart
        chart = pygal.Bar(style=DefaultStyle, x_label_rotation=45, show_minor_x_labels=False)
    elif chart_type == '2':  # line chart
        chart = pygal.Line(style=DefaultStyle, x_label_rotation=45, show_minor_x_labels=False)
    else:
        print('Invalid chart type selected. Please choose either "line" or "bar".')
        return None

    # graph data
    time_series_key = str(get_time_series_key(function))
    time_series = data.get(time_series_key)
    dates = sorted(time_series.keys())
    opens = [float(time_series[date]['1. open']) for date in dates]
    highs = [float(time_series[date]['2. high']) for date in dates]
    lows = [float(time_series[date]['3. low']) for date in dates]
    closes = [float(time_series[date]['4. close']) for date in dates]

    chart.title = f'{symbol} Stock Data: {start_date} to {end_date}'
    chart.x_labels = dates
    chart.x_labels_major = dates[::5]  # Reduce the number of major labels if there are too many dates
    chart.add('Open', opens)
    chart.add('High', highs)
    chart.add('Low', lows)
    chart.add('Close', closes)
    chart.show_legend = True
    chart.legend_at_bottom = True
    chart.tooltip_border_radius = 10

    # Generate and save the chart
    chart_file_name = f'{symbol}_{start_date}_to_{end_date}.svg'
    chart.render_to_file(f'static/{chart_file_name}')

    return f'static/{chart_file_name}'