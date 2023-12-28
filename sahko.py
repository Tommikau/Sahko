import requests
import datetime
import json
import tkinter as tk
from tkinter import Button, Label
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import timezone, timedelta

local_tz = timezone(timedelta(hours=2))  

def get_data():
    # Haetaan data
    response = requests.get("https://api.porssisahko.net/v1/latest-prices.json")
    data = json.loads(response.text)
    return data

def find_future_prices(data, num_points=24):
    current_time_local = datetime.datetime.now(local_tz).replace(second=0, microsecond=0)

    data['prices'] = [
        {
            'startDate': datetime.datetime.strptime(price['startDate'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc),
            'endDate': datetime.datetime.strptime(price['endDate'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc),
            'price': price['price']
        }
        for price in data['prices']
    ]

    # Järjestä data ajan mukaan
    data['prices'] = sorted(data['prices'], key=lambda x: x['startDate'])

    # Tulevat hinnat tästä hetkestä eteenpäin
    future_prices = []
    for price in data['prices']:
        if current_time_local < price['startDate']:
            future_prices.append({'startDate': price['startDate'], 'price': price['price']})
        if len(future_prices) == num_points:
            break

    # Kuluvan tunnin hinta
    current_hour_price = None
    for price in data['prices']:
        if price['startDate'] <= current_time_local < price['endDate']:
            current_hour_price = price['price']
            break

    return future_prices, current_hour_price

def plot_graph():
    data = get_data()

    # Hae ja tulosta tulevat hinnat
    future_prices, current_hour_price = find_future_prices(data)
    if future_prices:
        for price_info in future_prices:
            print(f"Hour: {price_info['startDate']}, Price: {price_info['price']}")
    else:
        print(f"No future price data found")

    x_values = [price['startDate'].astimezone(local_tz) for price in future_prices]
    y_values = [price['price'] for price in future_prices]

    # Päivitä Label tämän hetken hinnalla
    current_price_label.config(text=f'Tämän hetken hinta: {current_hour_price:.2f} Snt') 

    # Piirretään Graafi
    ax.clear()
    ax.plot(x_values, y_values, label='Data')
    ax.set_title('Graafi')
    ax.set_xlabel('Aika')
    ax.set_ylabel('Hinta (Snt)')
    ax.legend()

    # Päivitetään tkinter-ikkuna
    canvas.draw()

# Luo tkinter-ikkuna
root = tk.Tk()
root.title("Graafinen Käyttöliittymä")

# Luo matplotlib-kuva ja akselit
fig = Figure(figsize=(8, 6), dpi=100)
ax = fig.add_subplot(111)

# Luo napin, joka päivittää graafin 
update_button = Button(root, text="Päivitä Graafi", command=plot_graph)
update_button.pack()

# Luo Label-objekti näyttämään nykyisen hinnan
current_price_label = Label(root, text="Tämän hetken hinta: N/A")
current_price_label.pack()

# Luo matplotlib-Canvas tkinter-ikkunaan
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

# Käynnistä tkinter-silmukka
root.mainloop()
