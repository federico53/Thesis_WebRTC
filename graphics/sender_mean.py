import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Percorso ai file CSV (modifica il percorso se necessario)
sender_path = "./data/sender60/communication/test_sender_*.csv"
cpu_path = "./data/sender60/cpu_usage/cpu_usage_test_sender_*.csv"

N = 60

# Lista per memorizzare i DataFrame di ogni test
sender_data_frames = []
cpu_data_frames = []

# Leggere tutti i file CSV per sender
for file in glob.glob(sender_path):
    df = pd.read_csv(file)
    sender_data_frames.append(df)

# Leggere tutti i file CSV per cpu
for file in glob.glob(cpu_path):
    df = pd.read_csv(file)
    cpu_data_frames.append(df)

# Concatenare tutti i DataFrame lungo l'asse 0 per avere un unico DataFrame con i dati di tutti i test
all_sender_data = pd.concat(sender_data_frames, axis=0)
all_cpu_data = pd.concat(cpu_data_frames, axis=0)

# Calcolare la media per ciascun secondo aggregando per l'indice (che rappresenta il tempo)
sender_numeric_cols = all_sender_data.select_dtypes(include=np.number).columns
mean_sender_data_per_second = all_sender_data[sender_numeric_cols].groupby(all_sender_data.index).mean()

cpu_numeric_cols = all_cpu_data.select_dtypes(include=np.number).columns
mean_cpu_data_per_second = all_cpu_data[cpu_numeric_cols].groupby(all_cpu_data.index).mean()

# Convertire RSS e VMS da byte a gigabyte
all_cpu_data['RSS'] = all_cpu_data['RSS'] / (1024 ** 3)
all_cpu_data['VMS'] = all_cpu_data['VMS'] / (1024 ** 3)

# Mostrare le prime righe del DataFrame aggregato
print(mean_sender_data_per_second.head())
print(mean_cpu_data_per_second.head())

# Selezione delle metriche chiave per la visualizzazione
sender_metrics_to_plot = [
    'bytesSent',
    'framesPerSecond'
]

cpu_metrics_to_plot = [
    'CPU %', 
    'RSS (GB)', 
    'User', 
    'VMS (GB)', 
    'System'
]

# ------------------------ CPU -------------------------------
# Generazione dei grafici temporali per ciascuna metrica aggregata
plt.figure(figsize=(12, 14))

for i, metric in enumerate(cpu_metrics_to_plot, 1):
    plt.subplot(3, 2, i)
    plt.plot(mean_cpu_data_per_second.index, mean_cpu_data_per_second[metric.split(' ')[0]], marker='o')
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

# ------------------------ Sender -------------------------------
# Generazione dei grafici temporali per ciascuna metrica aggregata
plt.figure(figsize=(15, 10))

for i, metric in enumerate(sender_metrics_to_plot, 1):
    plt.subplot(2, 2, i)
    plt.plot(mean_sender_data_per_second.index, mean_sender_data_per_second[metric], marker='o')
    plt.title(f'Mean {metric} per Second')
    plt.xlabel('Secondi')
    plt.ylabel(metric)
    plt.grid(True)


# Total Encode Time e Total Packet Send Delay

plt.subplot(2, 2, 3)
plt.plot(mean_sender_data_per_second.index, mean_sender_data_per_second['totalEncodeTime'], marker='o', color='blue', label='Total Encode Time')
plt.plot(mean_sender_data_per_second.index, mean_sender_data_per_second['totalPacketSendDelay'], marker='o', color='orange', label='Total Packet Send Delay')
plt.title('Mean Encode Time and Processing Delay per Second')
plt.xlabel('Secondi')
plt.ylabel('Time (s)')
plt.legend()
plt.grid(True)


# Scatter Plot: Total Packet Send Delay vs. Huge Frames Sent

plt.subplot(2, 2, 4)
plt.scatter(
    mean_sender_data_per_second['totalPacketSendDelay'],
    mean_sender_data_per_second['hugeFramesSent'],
    alpha=0.5, 
    c='blue'
)

# Aggiungere una linea di regressione
sns.regplot(
    x='totalPacketSendDelay',
    y='hugeFramesSent',
    data=mean_sender_data_per_second,
    scatter=False,
    color='red'
)

plt.xlabel('Total Packet Send Delay (s)')
plt.ylabel('Huge Frames Sent')
plt.title('Total Packet Send Delay vs. Huge Frames Sent')
plt.grid(True)

# calcolare il ritardo medio di invio dei pacchetti
average_packet_send_delay = mean_sender_data_per_second['totalPacketSendDelay'].max()/N
print(f'Average Total Packet Send Delay: {average_packet_send_delay:.2f} seconds')

plt.tight_layout()
plt.show()



# Grafico per confrontare headerBytesSent con bytesSent
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)

plt.bar(mean_sender_data_per_second.index, mean_sender_data_per_second['bytesSent'], label='Total Bytes Sent')
plt.bar(mean_sender_data_per_second.index, mean_sender_data_per_second['headerBytesSent'], label='Header Bytes Sent')

# Calcolare la percentuale di overhead
mean_sender_data_per_second['headerOverheadPercent'] = (mean_sender_data_per_second['headerBytesSent'] / mean_sender_data_per_second['bytesSent']) * 100
average_overhead_percent = mean_sender_data_per_second['headerOverheadPercent'].mean()

# Aggiungere una annotazione per la media della percentuale di overhead
plt.annotate(f'Avg Header Overhead: {average_overhead_percent:.2f}%', xy=(0.5, 0.95), xycoords='axes fraction', fontsize=12, color='green')
print(f'Average Header Overhead: {average_overhead_percent:.2f}%')

plt.title('Comparison of Header Bytes vs Total Bytes Sent')
plt.xlabel('Secondi')
plt.ylabel('Bytes')
plt.legend(loc='upper left')
plt.grid(True)


# Grafico per confrontare packetsSent con retransmittedPackets
plt.subplot(1, 2, 2)

plt.bar(mean_sender_data_per_second.index, mean_sender_data_per_second['packetsSent'], label='Total Packets Sent')
plt.bar(mean_sender_data_per_second.index, mean_sender_data_per_second['retransmittedPacketsSent'], label='Retransmitted Packets')

# Calcolare la percentuale di pacchetti ritrasmessi
mean_sender_data_per_second['retransmitPercent'] = (mean_sender_data_per_second['retransmittedPacketsSent'] / mean_sender_data_per_second['packetsSent']) * 100
average_retransmit_percent = mean_sender_data_per_second['retransmitPercent'].mean()

# Aggiungere una annotazione per la media della percentuale di pacchetti ritrasmessi
plt.annotate(f'Avg Retransmit Percent: {average_retransmit_percent:.2f}%', xy=(0.5, 0.95), xycoords='axes fraction', fontsize=12, color='green')
print(f'Average Retransmit Percent: {average_retransmit_percent:.2f}%')

plt.title('Comparison of Total Packets vs Retransmitted Packets')
plt.xlabel('Secondi')
plt.ylabel('Packets')
plt.legend(loc='upper left')
plt.grid(True)

plt.tight_layout()
plt.show()

# Dual-Axis Line Chart: Frames Per Second vs. CPU Percent
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
# Primo asse y per Frames Per Second
ax1 = plt.gca()
ax1.plot(mean_sender_data_per_second.index, mean_sender_data_per_second['framesPerSecond'], color='b', label='Frames Per Second')
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

# Calcolare la velocità in bit/s
mean_sender_data_per_second['bitsPerSecond'] = mean_sender_data_per_second['bytesSent'].diff() * 8
mean_sender_data_per_second = mean_sender_data_per_second.dropna(subset=['bitsPerSecond'])

# Line plot per la velocità in bit/s
plt.subplot(2, 1, 2)
plt.plot(mean_sender_data_per_second.index, mean_sender_data_per_second['bitsPerSecond'], color='purple')
plt.title('Bitrate Over Time')
plt.xlabel('Time (s)')
plt.ylabel('Bitrate (bit/s)')
plt.grid(True)

average_bitrate = mean_sender_data_per_second['bitsPerSecond'].mean()
plt.annotate(f'Avg Bitrate: {average_bitrate:.2f} bit/s', xy=(0.5, 0.95), xycoords='axes fraction', fontsize=12, color='green')
print(f'Average Bitrate: {average_bitrate:.2f} bit/s')

plt.tight_layout()
plt.show()


# # Correlation Matrix
# plt.figure(figsize=(10, 6))
# corr = mean_sender_data_per_second.corr()
# sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
# plt.title('Correlation Matrix')
# plt.show()
