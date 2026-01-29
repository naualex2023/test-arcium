import argparse
import asyncio
import os
import ssl
import time
from aioquic.asyncio import connect, serve
from aioquic.quic.configuration import QuicConfiguration

def get_certs():
    cert_file, key_file = "cert.pem", "key.pem"
    if not os.path.exists(cert_file):
        print("🛠 Генерируем сертификаты (это может занять время)...")
        os.system(f"openssl req -x509 -newkey rsa:4096 -keyout {key_file} -out {cert_file} -nodes -days 365 -subj '/CN=arcium-test'")
    return cert_file, key_file

async def run_server(host, port):
    cert, key = get_certs()
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain(cert, key)
    
    async def handler(reader, writer):
        print(f"✅ [Server] TLS 1.3 Handshake SUCCESS!")
        while True:
            data = await reader.read(10000)
            if not data: break
            print(f"📥 [Server] Received {len(data)} bytes.")
            writer.write(f"ACK-{len(data)}".encode())

    print(f"🚀 [Server] Listening on {host}:{port}...")
    await serve(host, port, configuration=configuration, stream_handler=handler)
    await asyncio.Future()

async def run_client(host, port):
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = ssl.CERT_NONE
    
    # Цикл попыток подключения (ждем сервер)
    for attempt in range(1, 11):
        try:
            print(f"🤝 [Client] Попытка {attempt}/10: Подключение к {host}:{port}...")
            async with connect(host, port, configuration=configuration) as client:
                print(f"✨ [Client] TLS 1.3 Connection Established!")
                reader, writer = await client.create_stream()
                
                for size in [2448, 5000, 7000]:
                    print(f"📤 [Client] Sending payload: {size} bytes...")
                    writer.write(os.urandom(size))
                    response = await asyncio.wait_for(reader.read(100), timeout=5.0)
                    print(f"📥 [Client] Server confirmed: {response.decode()}")
                    await asyncio.sleep(1)
                return # Успех, выходим
        except Exception as e:
            print(f"⏳ Сервер еще не готов или ошибка: {e}")
            await asyncio.sleep(3)
    print("💥 Все попытки исчерпаны.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["server", "client"])
    args = parser.parse_args()
    if args.mode == "server":
        asyncio.run(run_server("0.0.0.0", 8001))
    else:
        asyncio.run(run_client("172.20.0.101", 8001))