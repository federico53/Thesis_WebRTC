import pandas as pd
import matplotlib.pyplot as plt

# Percorso del file (modifica questo percorso per analizzare un file diverso)
file_path = "/home/federico/Documents/Tesi/Risultati/receiver2/cpu_usage/cpu_usage_test_receiver_1.csv"

# Caricamento del file CSV
df = pd.read_csv(file_path)

# Visualizzazione delle prime righe del DataFrame
print(df.head())

# Visualizzazione delle informazioni del DataFrame
print(df.info())

# Selezione delle metriche chiave per la visualizzazione
metrics_to_plot = [
    'CPU Percent', 
    'RSS', 
    'VMS', 
    'User', 
    'System', 
    'Children User', 
    'Children System'
]

# Generazione dei grafici temporali per ciascuna metrica
plt.figure(figsize=(12, 14))

for i, metric in enumerate(metrics_to_plot, 1):
    plt.subplot(len(metrics_to_plot), 1, i)
    plt.plot(df.index, df[metric], marker='o')
    plt.title(metric)
    plt.xlabel('Secondi')
    plt.ylabel(metric)
    plt.grid(True)

plt.tight_layout()
plt.show()
