import asyncio
import websockets
import json
import psutil
from playwright.async_api import async_playwright

# Funzione per ottenere il PID del processo principale di Chromium lanciato da Playwright
def get_browser_pid():
    # Cerca il processo Chromium con il flag --remote-debugging-port=9222
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'chrome' in proc.info['name'].lower() or 'chromium' in proc.info['name'].lower():
                if '--remote-debugging-port=9222' in proc.info['cmdline']:
                    return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

# Funzione per ottenere l'utilizzo della CPU di un processo specifico
def get_cpu_usage(pid):
    try:
        process = psutil.Process(pid)
        cpu_percent = process.cpu_percent(interval=1)
        mem_info = process.memory_info()
        cpu_times = process.cpu_times()
        cpu_info = {
            'cpu_percent': cpu_percent,
            'rss': mem_info.rss,
            'vms': mem_info.vms,
            'user': cpu_times.user,
            'system': cpu_times.system,
            'children_user': cpu_times.children_user,
            'children_system': cpu_times.children_system
        }
        csv_string = f"{cpu_info['cpu_percent']},{cpu_info['rss']},{cpu_info['vms']},{cpu_info['user']},{cpu_info['system']},{cpu_info['children_user']},{cpu_info['children_system']}\n"
        return csv_string
    except psutil.NoSuchProcess:
        return None

# Funzione per monitorare l'utilizzo della CPU ogni secondo per 10 secondi
async def monitor_cpu_usage(pid, file_path, duration):
    with open(file_path, 'w') as file:
        file.write("CPU Percent,RSS,VMS,User,System,Children User,Children System\n")
        for _ in range(duration):
            cpu_usage = get_cpu_usage(pid)
            if cpu_usage is not None:
                file.write(f"{cpu_usage}")
                print(f"CPU Usage {_}: {cpu_usage}")
            else:
                file.write("Process not found.\n")
    print(f"Monitoraggio CPU completato. Risultati salvati in {file_path}")

async def wait_receiver(playwright):
    i = 0

    async with websockets.connect('ws://192.168.56.212:8080') as websocket:
        print("Connesso al WebSocket server. Attendo il segnale 'READY' dal receiver.")
        async for message in websocket:
            received_data = json.loads(message)
            if received_data == 'READY':
                i += 1
                print(f"Segnale 'READY' ricevuto dal receiver. Avvio il test {i}.")
                await websocket.send(json.dumps('START'))
                await start_test(playwright, i)
                print(f'Finito test {i}, in attesa del receiver')
            elif received_data == 'FINISH':
                print("Segnale 'FINISH' ricevuto dal receiver. Test completato.")
                break

async def start_test(playwright, test_number):

    browser = await playwright.chromium.launch(
        executable_path='/home/fhrvatin/hrvatin_webrtc_test/chrome/opt/google/chrome/google-chrome',
        headless=True, 
        args=['--no-sandbox', '--disable-setuid-sandbox', '--remote-debugging-port=9222']
    )

    context = await browser.new_context(accept_downloads=True)
    try:
        sender_page = await context.new_page()
        
        print("Apro la pagina del sender...")
        await sender_page.goto('http://192.168.56.212:8000/sender/index.html')


        # Ottieni il PID del processo browser
        pid = get_browser_pid()
        if pid:
            print(f"Chrome PID: {pid}")
        else:
            print("Unable to find Chrome PID.")

        # Avvia il monitoraggio della CPU in parallelo
        print("Avvio il monitoraggio della CPU...")
        file_path = f'./downloads/cpu_usage/cpu_usage_test_sender_{test_number}.csv'
        cpu_monitor_task = asyncio.create_task(monitor_cpu_usage(pid, file_path, duration=40))


        print("Clicco sul pulsante 'Connetti'...")
        await sender_page.click('#connect')


        # Gestisci il download del sender
        sender_download = await sender_page.wait_for_event('download')
        sender_download_path = f'./downloads/communication/test_sender_{test_number}.csv'
        await sender_download.save_as(sender_download_path)
        print(f'File scaricato dal sender: {sender_download_path}')

        # Aspetta che il monitoraggio della CPU sia completato
        await cpu_monitor_task

    except Exception as e:
        print(f'Errore durante il test sender: {e}')
    finally:
        await context.close()
        await browser.close()

async def main():
    async with async_playwright() as playwright:
        await wait_receiver(playwright)

if __name__ == "__main__":
    asyncio.run(main())
