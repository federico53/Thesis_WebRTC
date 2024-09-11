import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Percorso ai file CSV (modifica il percorso se necessario)
receiver_path = "/home/federico/Documents/Tesi/Risultati/receiver2/communication/test_receiver_*.csv"
cpu_path = "/home/federico/Documents/Tesi/Risultati/receiver2/cpu_usage/cpu_usage_test_receiver_*.csv"

# Lista per memorizzare i DataFrame di ogni test
receiver_data_frames = []
cpu_data_frames = []

# Leggere tutti i file CSV
for file in glob.glob(receiver_path):
    df = pd.read_csv(file)
    receiver_data_frames.append(df)

# Leggere tutti i file CSV per cpu
for file in glob.glob(cpu_path):
    df = pd.read_csv(file)
    cpu_data_frames.append(df)

# Concatenare tutti i DataFrame lungo l'asse 0 per avere un unico DataFrame con i dati di tutti i test
all_receiver_data = pd.concat(receiver_data_frames, axis=0)
all_cpu_data = pd.concat(cpu_data_frames, axis=0)

# Calcolare la media per ciascun secondo aggregando per l'indice (che rappresenta il tempo)
receiver_numeric_cols = all_receiver_data.select_dtypes(include=np.number).columns
mean_receiver_data_per_second = all_receiver_data[receiver_numeric_cols].groupby(all_receiver_data.index).mean()

cpu_numeric_cols = all_cpu_data.select_dtypes(include=np.number).columns
mean_cpu_data_per_second = all_cpu_data[cpu_numeric_cols].groupby(all_cpu_data.index).mean()

# Mostrare le prime righe del DataFrame aggregato
print(mean_receiver_data_per_second.head())
print(mean_cpu_data_per_second.head())

# Selezione delle metriche chiave per la visualizzazione
receiver_metrics_to_plot = [
    'framesPerSecond', 
    'packetsReceived',
    'jitter (s)', 
    'packetsLost'
]

cpu_metrics_to_plot = [
    'CPU Percent', 
    'RSS', 
    'User', 
    'VMS', 
    'System'
]

# ------------------------ CPU -------------------------------
# Generazione dei grafici temporali per ciascuna metrica aggregata
plt.figure(figsize=(12, 14))

for i, metric in enumerate(cpu_metrics_to_plot, 1):
    plt.subplot(3, 2, i)
    plt.plot(mean_cpu_data_per_second.index, mean_cpu_data_per_second[metric], marker='o')
    plt.title(f'Mean {metric} per Second')
    plt.xlabel('Secondi')
    plt.ylabel(metric)
    plt.grid(True)


plt.subplot(3, 2, 6)
plt.plot(mean_cpu_data_per_second.index, mean_cpu_data_per_second['Children User'], marker='o', label='Children User')
plt.plot(mean_cpu_data_per_second.index, mean_cpu_data_per_second['Children System'], marker='o', label='Children System')
plt.title(f'Mean Children User & System per Second')
plt.xlabel('Secondi')
plt.ylabel('Children User & System')
plt.legend(loc='upper left')
plt.grid(True)

# Impostare i margini e lo spazio verticale tra i subplot
plt.subplots_adjust(left=0.07, bottom=0.05, right=0.97, top=0.97, hspace=0.35)

plt.show()

# ------------------------ Receiver -------------------------------
# Generazione dei grafici temporali per ciascuna metrica aggregata
plt.figure(figsize=(15, 10))

for i, metric in enumerate(receiver_metrics_to_plot, 1):
    plt.subplot(2, 2, i)
    plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second[metric.split(' ')[0]], marker='o')
    plt.title(f'Mean {metric} per Second')
    plt.xlabel('Secondi')
    plt.ylabel(metric)
    plt.grid(True)

plt.tight_layout()
plt.show()

# Calcolare la differenza tra il valore attuale e quello precedente per totalInterFrameDelay
mean_receiver_data_per_second['totalInterFrameDelay_diff'] = mean_receiver_data_per_second['totalInterFrameDelay'].diff()
mean_receiver_data_per_second = mean_receiver_data_per_second.dropna(subset=['totalInterFrameDelay_diff'])


plt.figure(figsize=(15, 10))

# # Riallineare i dati per avere lo stesso indice
# aligned_data = mean_receiver_data_per_second[['framesPerSecond']].join(mean_cpu_data_per_second[['CPU Percent']], how='inner')

# Dual-Axis Line Chart: Frames Per Second vs. CPU Percent
plt.subplot(2, 2, 1)

# Primo asse y per Frames Per Second
ax1 = plt.gca()
ax1.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['framesPerSecond'], color='b', label='Frames Per Second')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Frames Per Second', color='b')
ax1.tick_params(axis='y', labelcolor='b')

# Secondo asse y per CPU Percent
ax2 = ax1.twinx()
ax2.plot(mean_cpu_data_per_second.index, mean_cpu_data_per_second['CPU Percent'], color='r', label='CPU Percent')
ax2.set_ylabel('CPU Percent (%)', color='r')
ax2.tick_params(axis='y', labelcolor='r')

# Aggiungi legende e titolo
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
plt.title('Frames Per Second and CPU Percent Over Time')
plt.grid(True)


# Scatter plot per la relazione tra jitter e framesPerSecond nella media aggregata

plt.subplot(2, 2, 2)
plt.scatter(mean_receiver_data_per_second['jitter'], mean_receiver_data_per_second['framesPerSecond'], color='green')
plt.title('Mean Relationship between jitter and Frames Per Second')
plt.xlabel('Jitter (s)')
plt.ylabel('Frames Per Second')
plt.grid(True)


# Jitter e Ritardi di Buffer

plt.subplot(2, 2, 3)
plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['jitter'], marker='o', color='blue', label='Jitter')
plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['jitterBufferDelay'], marker='o', color='orange', label='Jitter Buffer Delay')
plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['jitterBufferTargetDelay'], marker='o', color='green', label='Jitter Buffer Target Delay')
plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['jitterBufferMinimumDelay'], marker='o', color='red', label='Jitter Buffer Minimum Delay')
plt.title('Mean Jitter and Jitter Buffer Delays per Second')
plt.xlabel('Secondi')
plt.ylabel('Delay (s)')
plt.legend()
plt.grid(True)


# 6. Decode Time e Processing Delay

plt.subplot(2, 2, 4)
plt.bar(mean_receiver_data_per_second.index, mean_receiver_data_per_second['totalProcessingDelay'], label='Total Processing Delay')
plt.bar(mean_receiver_data_per_second.index, mean_receiver_data_per_second['totalDecodeTime'], label='Total Decode Time')

# Calcolare la percentuale di overhead
mean_receiver_data_per_second['decodePercent'] = (mean_receiver_data_per_second['totalDecodeTime'] / mean_receiver_data_per_second['totalProcessingDelay']) * 100
average_decode_percent = mean_receiver_data_per_second['decodePercent'].mean()

# Aggiungere una annotazione per la media della percentuale di overhead
plt.annotate(f'Avg Decode Percent: {average_decode_percent:.2f}%', xy=(0.5, 0.95), xycoords='axes fraction', fontsize=12, color='green')

plt.title('Mean Decode Time and Processing Delay per Second')
plt.xlabel('Secondi')
plt.ylabel('Time (s)')
plt.legend()
plt.grid(True)


plt.tight_layout()
plt.show()


# Grafico per confrontare headerBytesReceived con bytesReceived
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)

plt.bar(mean_receiver_data_per_second.index, mean_receiver_data_per_second['bytesReceived'], label='Total Bytes Received')
plt.bar(mean_receiver_data_per_second.index, mean_receiver_data_per_second['headerBytesReceived'], label='Header Bytes Received')

# Calcolare la percentuale di overhead
mean_receiver_data_per_second['headerOverheadPercent'] = (mean_receiver_data_per_second['headerBytesReceived'] / mean_receiver_data_per_second['bytesReceived']) * 100
average_overhead_percent = mean_receiver_data_per_second['headerOverheadPercent'].mean()

# Aggiungere una annotazione per la media della percentuale di overhead
plt.annotate(f'Avg Header Overhead: {average_overhead_percent:.2f}%', xy=(0.5, 0.95), xycoords='axes fraction', fontsize=12, color='green')

plt.title('Comparison of Header Bytes vs Total Bytes Received')
plt.xlabel('Secondi')
plt.ylabel('Bytes')
plt.legend(loc='upper left')
plt.grid(True)


plt.subplot(1, 2, 2)

plt.bar(mean_receiver_data_per_second.index, mean_receiver_data_per_second['packetsReceived'], label='Total Packets Received')
plt.bar(mean_receiver_data_per_second.index, mean_receiver_data_per_second['retransmittedPacketsReceived'], label='Retransmitted Packets')

# Calcolare la percentuale di pacchetti ritrasmessi
mean_receiver_data_per_second['retransmitPercent'] = (mean_receiver_data_per_second['retransmittedPacketsReceived'] / mean_receiver_data_per_second['packetsReceived']) * 100
average_retransmit_percent = mean_receiver_data_per_second['retransmitPercent'].mean()

# Aggiungere una annotazione per la media della percentuale di pacchetti ritrasmessi
plt.annotate(f'Avg Retransmit Percent: {average_retransmit_percent:.2f}%', xy=(0.5, 0.95), xycoords='axes fraction', fontsize=12, color='green')

plt.title('Comparison of Total Packets vs Retransmitted Packets')
plt.xlabel('Secondi')
plt.ylabel('Packets')
plt.legend(loc='upper left')
plt.grid(True)

plt.tight_layout()
plt.show()

# Calcolare la velocità in bit/s
mean_receiver_data_per_second['bitsPerSecond'] = mean_receiver_data_per_second['bytesReceived'].diff() * 8
mean_receiver_data_per_second = mean_receiver_data_per_second.dropna(subset=['bitsPerSecond'])

# Line plot per la velocità in bit/s
plt.figure(figsize=(12, 6))
plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['bitsPerSecond'], color='purple')
plt.title('Bitrate Over Time')
plt.xlabel('Time (s)')
plt.ylabel('Bitrate (bit/s)')
plt.grid(True)

average_bitrate = mean_receiver_data_per_second['bitsPerSecond'].mean()
plt.annotate(f'Avg Bitrate: {average_bitrate:.2f} bit/s', xy=(0.5, 0.95), xycoords='axes fraction', fontsize=12, color='green')

plt.tight_layout()
plt.show()

# # Jitter e Ritardi di Buffer

# plt.figure(figsize=(15, 10))
# plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['jitter'], marker='o', color='blue', label='Jitter')
# plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['totalInterFrameDelay'], marker='o', color='orange', label='Total Inter-Frame Delay')
# plt.title('Mean Jitter and Total Inter-Frame Delay per Second')
# plt.xlabel('Secondi')
# plt.ylabel('Delay (s)')
# plt.legend()
# plt.grid(True)

# plt.tight_layout()
# plt.show()

# ------------------------ DA ELIMINARE -------------------------------

# # Jitter Buffer Delay over time nella media aggregata
# plt.subplot(2, 2, 3)
# plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['jitterBufferDelay'], marker='o', color='blue')
# plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['jitterBufferTargetDelay'], marker='o', color='green')
# plt.title('Mean Jitter Buffer Delay & Target per Second')
# plt.xlabel('Secondi')
# plt.ylabel('Jitter Buffer Delay (s)')
# plt.grid(True)

# # Scatter plot per la relazione tra jitterBufferDelay e jitter nella media aggregata
# plt.subplot(2, 2, 4)
# plt.scatter(mean_receiver_data_per_second['jitterBufferDelay'], mean_receiver_data_per_second['jitter'], color='red')
# plt.title('Mean Correlation between Jitter Buffer Delay and Jitter')
# plt.xlabel('Jitter Buffer Delay (s)')
# plt.ylabel('Jitter')
# plt.grid(True)

# plt.tight_layout()
# plt.show()


# # 4. Inter Frame Delay e Variabilità
# plt.subplot(2, 2, 2)
# plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['totalInterFrameDelay'], marker='o', color='blue', label='Total Inter-Frame Delay')
# plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['totalSquaredInterFrameDelay'], marker='o', color='orange', label='Total Squared Inter-Frame Delay')
# plt.title('Mean Inter-Frame Delay and Variability per Second')
# plt.xlabel('Secondi')
# plt.ylabel('Delay (s)')
# plt.legend()
# plt.grid(True)


# # 9. Quantization Parameter (QP)
# plt.subplot(2, 2, 4)
# plt.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['qpSum'], marker='o', color='blue', label='QP Sum')
# plt.title('Mean Quantization Parameter (QP) per Second')
# plt.xlabel('Secondi')
# plt.ylabel('QP Sum')
# plt.legend()
# plt.grid(True)



# # 1. **Bubble Chart: Bytes Received vs. Frames Per Second (con dimensione della bolla rappresentante il Jitter Buffer Delay)**
# plt.figure(figsize=(10, 6))

# # Moltiplica il jitterBufferDelay per un fattore per amplificare la dimensione delle bolle
# scaling_factor = 100  # Modifica questo valore per adattare la scala delle bolle
# sizes = mean_receiver_data_per_second['jitterBufferDelay'].fillna(0) * scaling_factor

# # Assicurati che le dimensioni siano almeno un valore minimo per migliorare la visibilità
# sizes = np.clip(sizes, 10, 500)

# plt.scatter(
#     mean_receiver_data_per_second['bytesReceived'],
#     mean_receiver_data_per_second['framesPerSecond'],
#     s=sizes, 
#     alpha=0.5,
#     c=mean_receiver_data_per_second['jitterBufferDelay'], 
#     cmap='viridis'
# )
# plt.colorbar(label='Jitter Buffer Delay')
# plt.xlabel('Bytes Received')
# plt.ylabel('Frames Per Second')
# plt.title('Bytes Received vs. Frames Per Second with Jitter Buffer Delay as Bubble Size')
# plt.grid(True)
# plt.show()




# # 5. **Bubble Chart: Packets Received vs. Retransmitted Packets Received (con dimensione della bolla rappresentante il NACK Count)**
# plt.figure(figsize=(10, 6))
# plt.scatter(
#     mean_receiver_data_per_second['packetsReceived'],
#     mean_receiver_data_per_second['retransmittedPacketsReceived'],
#     s=mean_receiver_data_per_second['nackCount'] * 10, 
#     alpha=0.5,
#     c=mean_receiver_data_per_second['nackCount'],
#     cmap='plasma'
# )
# plt.colorbar(label='NACK Count')
# plt.xlabel('Packets Received')
# plt.ylabel('Retransmitted Packets Received')
# plt.title('Packets Received vs. Retransmitted Packets Received with NACK Count as Bubble Size')
# plt.grid(True)
# plt.show()

# ------------------------ NON DA ELIMINARE -------------------------------

# # Dual-Axis Line Chart: Total Inter-Frame Delay vs. Jitter
# plt.figure(figsize=(12, 6))


# # Primo asse y per Total Inter-Frame Delay
# ax1 = plt.gca()
# ax1.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['totalInterFrameDelay_diff'], color='b', label='Total Inter-Frame Delay')
# ax1.set_xlabel('Time (s)')
# ax1.set_ylabel('Total Inter-Frame Delay (diff)', color='b')
# ax1.tick_params(axis='y', labelcolor='b')

# # Secondo asse y per Jitter
# ax2 = ax1.twinx()
# ax2.plot(mean_receiver_data_per_second.index, mean_receiver_data_per_second['jitter'], color='r', label='jitter')
# ax2.set_ylabel('Jitter', color='r')
# ax2.tick_params(axis='y', labelcolor='r')

# # Aggiungi legende e titolo
# ax1.legend(loc='upper left')
# ax2.legend(loc='upper center')
# plt.title('Total Inter-Frame Delay (diff) and Jitter Over Time')
# plt.grid(True)
# plt.show()

# # Correlation Matrix
# plt.figure(figsize=(12, 8))
# corr = mean_receiver_data_per_second.corr()
# sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
# plt.title('Correlation Matrix')
# plt.show()



