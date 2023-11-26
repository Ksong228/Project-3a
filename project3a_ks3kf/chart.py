import pygal
from pygal.style import DefaultStyle
from flask import render_template

# Function to generate a chart based on user input and save it as an SVG file
def generate_chart(chart_type, x_labels, data, symbol, start_date, end_date):
    # Choose the chart type based on user input
    if chart_type == 'bar':
        chart = pygal.Bar(style=DefaultStyle, x_label_rotation=20, show_minor_x_labels=True, tooltips=True)
    elif chart_type == 'line':
        chart = pygal.Line(style=DefaultStyle, x_label_rotation=20, show_minor_x_labels=True, tooltips=True)
    else:
        raise ValueError("Invalid chart type specified")

    # Set the title with the stock symbol and date range
    chart.title = f'Stock Data for {symbol}: {start_date} to {end_date}'

    # Set the x-axis labels as dates
    chart.x_labels = x_labels

    # Add data to the chart
    chart.add('Open', data['open'])
    chart.add('High', data['high'])
    chart.add('Low', data['low'])
    chart.add('Close', data['close'])

    svg_data = chart.render(is_unicode=True)
    return render_template('index.html', chart_data=svg_data)

    # Note: This below code is of another method of displaying the chart, keeping it there for reference, not part of code.
    # Save the chart as an SVG file with a name based on the symbol and date range
    # chart_file_name = f'{symbol}_{start_date}_to_{end_date}.svg'
    # chart_file_path = f'static/{chart_file_name}'
    # chart.render_to_file(chart_file_path)

    # Return the path to the saved chart file
    # return chart_file_path