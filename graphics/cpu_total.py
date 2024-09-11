import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt

# Percorso ai file CSV (modifica il percorso se necessario)
path = "/home/federico/Documents/Tesi/Risultati/sender2/cpu_usage/cpu_usage_test_sender_*.csv"

# Lista per memorizzare i DataFrame di ogni test
data_frames = []

# Leggere tutti i file CSV
for file in glob.glob(path):
    df = pd.read_csv(file)
    data_frames.append(df)

# Concatenare tutti i DataFrame lungo l'asse 0 per avere un unico DataFrame con i dati di tutti i test
all_data = pd.concat(data_frames, axis=0)

# Selezionare solo le colonne numeriche per calcolare la media
numeric_cols = all_data.select_dtypes(include=np.number).columns
mean_data_per_second = all_data[numeric_cols].groupby(all_data.index).mean()

# Mostrare le prime righe del DataFrame aggregato
print(mean_data_per_second.head())

# Selezione delle metriche chiave per la visualizzazione
metrics_to_plot = [
    'CPU Percent', 
    'RSS', 
    'User', 
    'VMS', 
    'System'
]

# Generazione dei grafici temporali per ciascuna metrica aggregata
plt.figure(figsize=(12, 14))

for i, metric in enumerate(metrics_to_plot, 1):
    plt.subplot(3, 2, i)
    plt.plot(mean_data_per_second.index, mean_data_per_second[metric], marker='o')
    plt.title(f'Mean {metric} per Second')
    plt.xlabel('Secondi')
    plt.ylabel(metric)
    plt.grid(True)


plt.subplot(3, 2, 6)
plt.plot(mean_data_per_second.index, mean_data_per_second['Children User'], marker='o', label='Children User')
plt.plot(mean_data_per_second.index, mean_data_per_second['Children System'], marker='o', label='Children System')
plt.title(f'Mean Children User & System per Second')
plt.xlabel('Secondi')
plt.ylabel('Children User & System')
plt.legend(loc='upper left')
plt.grid(True)

# Impostare i margini e lo spazio verticale tra i subplot
plt.subplots_adjust(left=0.07, bottom=0.05, right=0.97, top=0.97, hspace=0.35)

plt.show()
