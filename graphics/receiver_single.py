import pandas as pd
import matplotlib.pyplot as plt

# Caricamento del file CSV
# Tutti i 50 file sono in questo percorso e si chiamano test_receiver_{i}.csv
file_path = "/home/federico/Documents/Tesi/Risultati/receiver/communication/test_receiver_3.csv"
df = pd.read_csv(file_path)

# Visualizzazione delle prime righe del DataFrame e delle informazioni di base
df_head = df.head()
df_info = df.info()

# Selezione delle metriche chiave per la visualizzazione semplice
metrics_to_plot = [
    'jitter', 
    'framesPerSecond', 
    'packetsLost', 
    'packetsReceived'
]

# Generazione dei grafici temporali per ciascuna metrica selezionata
plt.figure(figsize=(15, 10))

for i, metric in enumerate(metrics_to_plot, 1):
    plt.subplot(2, 2, i)
    plt.plot(df.index, df[metric], marker='o')
    plt.title(metric)
    plt.xlabel('Secondi')
    plt.ylabel(metric)
    plt.grid(True)

plt.tight_layout()
plt.show()

# Scatter plot per la relazione tra totalInterFrameDelay e jitter
plt.figure(figsize=(15, 10))

plt.subplot(2, 2, 1)
plt.scatter(df['totalInterFrameDelay'], df['jitter'], color='red')
plt.title('Correlation between Inter-Frame Delay and Jitter')
plt.xlabel('Inter-Frame Delay (totalInterFrameDelay)')
plt.ylabel('Jitter')
plt.grid(True)

# Scatter plot per la relazione tra jitter e framesPerSecond
plt.subplot(2, 2, 2)
plt.scatter(df['framesPerSecond'], df['jitter'], color='green')
plt.title('Relationship jitter and Frames Per Second')
plt.xlabel('FPS')
plt.ylabel('Jitter')
plt.grid(True)

# Jitter Buffer Delay over time
plt.subplot(2, 2, 3)
plt.plot(df.index, df['jitterBufferDelay'], marker='o', color='red')
plt.plot(df.index, df['jitterBufferTargetDelay'], marker='o', color='blue')
plt.title('Jitter Buffer Delay & Jitter Buffer Delay Target')
plt.xlabel('Secondi')
plt.ylabel('Jitter Buffer Delay (s)')
plt.grid(True)

# Scatter plot per la relazione tra jitterBufferDelay e jitter
plt.subplot(2, 2, 4)
plt.scatter(df['jitterBufferDelay'], df['jitter'], color='red')
plt.title('Correlation between Jitter Buffer Delay and Jitter')
plt.xlabel('Jitter Buffer Delay (s)')
plt.ylabel('Jitter')
plt.grid(True)

plt.tight_layout()
plt.show()
