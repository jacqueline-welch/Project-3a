import requests
import pygal
from datetime import datetime
from flask import Flask, request, render_template
import csv

AV_API_KEY = "IMTO1H6UEKUDNM2G"
CSV_FILE = 'stocks.csv'

app = Flask(__name__)

def fetch_stock_data(symbol, function):
    url = "https://www.alphavantage.co/query"
    stock_info = {
        "function": function,
        "symbol": symbol,
        "apikey": AV_API_KEY,
        "datatype": "json"
    }

    response = requests.get(url, params=stock_info)

    if response.ok:
        data = response.json()
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key:
                time_series_key = key
                break

        if time_series_key:
            return data[time_series_key]
        else:
            print(f"Error: Could not find time series data in the response. Response: {data}")
            return None
    else:
        print(f"Error: API request failed with status code {response.status_code}")
        return None

def sort_data(data, start, end):
    filter_data = {}

    for date, values in data.items():
        if start <= date <= end:
            close_price = values.get("4. close")
            if close_price:
                try:
                    filter_data[date] = float(close_price)
                except ValueError:
                    print(f"Warning: Invalid close price data for {date}, skipping this date.")
                    continue
            else:
                print(f"Warning: Missing data for {date}, skipping this date.")

    #sorts dates chronologically from left to right so that the chart isn't misleading
                
    sorted_data = dict(sorted(filter_data.items())) 
    return sorted_data

def create_stock_chart(stock_data, symbol, chart_type, start_date, end_date):
    chart_types = {"line": pygal.Line, "bar": pygal.Bar}
    chart_class = chart_types.get(chart_type, pygal.Line)
    chart = chart_class(title=f"{symbol} Stock Prices ({start_date} to {end_date})", x_label_rotation=45)
    chart.x_labels = list(stock_data.keys())
    chart.add(symbol, list(stock_data.values()))
    chart_svg = chart.render()
    return chart_svg.decode('utf-8')

def get_stock_symbols(filename):
    symbols = []
    try:
        with open(filename, 'r') as csvfile:
            reader =csv.reader(csvfile)
            for row in reader:
                if row:
                    symbols.append(row[0].strip())
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
    return symbols

@app.route('/', methods=['GET', 'POST'])

def index():
    stock_symbols = get_stock_symbols(CSV_FILE)

    if request.method == 'POST':
        symbol = request.form['symbol'].upper()
        chart_type = request.form['chart_type'].lower()
        function_choice = request.form['function_choice']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']

        if not symbol:
            return render_template('index.html', error="Please select a stock symbol.", stock_symbols=stock_symbols)
        
        function = "TIME_SERIES_DAILY"
        if function_choice == "weekly":
            function = "TIME_SERIES_WEEKLY"
        elif function_choice == "monthly":
            function = "TIME_SERIES_MONTHLY"

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            return render_template('index.html', error="Incorrect date format. Use YYYY-MM-DD.", stock_symbols=stock_symbols)
        
        if end_date < start_date:
            return render_template('index.html', error="End date cannot be before start date.", stock_symbols=stock_symbols)
        
        data = fetch_stock_data(symbol, function)

        if not data:
            return render_template('index.html', error="Could not fetch stock data for the given symbol.", stock_symbols=stock_symbols)
        
        filtered_data = sort_data(data, start_date, end_date)

        if filtered_data:
            chart_svg = create_stock_chart(filtered_data, symbol, chart_type, start_date, end_date)
            return render_template('index.html', chart_svg=chart_svg, stock_symbols=stock_symbols)
        else:
            return render_template('index.html', error="No stock data available for the given date range.", stock_symbols=stock_symbols)
        
    return render_template('index.html', stock_symbols=stock_symbols)

if __name__ == "__main__":
    # I was having port issues so I included some extra stuff
    app.run(debug=True, port=5001, host='0.0.0.0')
