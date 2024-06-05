from hybridagi import CodeInterpreterUtility

def test_code_interpreter_plots():
    interpreter = CodeInterpreterUtility()

    code = \
"""
# Générer des données aléatoires
x = np.arange(10)  # Générer une séquence de 10 nombres (0 à 9)
y = np.random.rand(10)  # Générer 10 nombres aléatoires

# Créer un graphique
plt.plot(x, y, marker='o')  # Tracer les données avec des points marqués par des cercles

# Ajouter des titres et des étiquettes
plt.title('Graphique Simple avec Matplotlib')
plt.xlabel('Index')
plt.ylabel('Valeur aléatoire')

# Afficher le graphique
plt.show()
"""
    result, plots, err = interpreter.add_and_run(code)
    assert len(plots) == 1
    assert result == ""
    assert err == False

def test_code_interpreter_panda():
    interpreter = CodeInterpreterUtility()

    code = \
"""
import requests
import pandas as pd
from datetime import datetime, timedelta

def get_bitcoin_price_history(days):
    data = []
    base_url = "https://api.coingecko.com/api/v3/coins/bitcoin/history?date="

    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%d-%m-%Y")
        url = base_url + date
        response = requests.get(url)
        response_data = response.json()
        print(response_data)
        price = response_data['market_data']['current_price']['usd']
        data.append({'Date': date, 'Price': price})

    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    df.set_index('Date', inplace=True)
    return df

days = 7  # Change this to the number of days you want to fetch prices for
bitcoin_price_history = get_bitcoin_price_history(days)

print(bitcoin_price_history)"""
    result, plots, err = interpreter.add_and_run(code)
    assert len(plots) == 0
    assert result != ""