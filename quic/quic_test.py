import argparse
import asyncio
import os
import ssl
from aioquic.asyncio import connect, serve
from aioquic.quic.configuration import QuicConfiguration

def get_certs():
    cert_file, key_file = "cert.pem", "key.pem"
    if not os.path.exists(cert_file):
        print("🛠 Генерируем сертификат (4096 бит)...")
        os.system(f"openssl req -x509 -newkey rsa:4096 -keyout {key_file} -out {cert_file} -nodes -days 365 -subj '/CN=trusted-dealer'")
    return cert_file, key_file

async def run_server(host, port):
    cert, key = get_certs()
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain(cert, key)

    # Внутренняя логика обработки стрима
    async def handle_stream(reader, writer):
        print(f"✅ [Dealer] Соединение установлено. Ожидаю запрос...")
        try:
            data = await reader.read(1024 * 5) # Читаем запрос от ноды
            print(f"📥 [Dealer] Получено от ноды: {len(data)} байт")
            
            # ТЕСТ НА 10 КБ: Это проверит ту самую "Checksum error"
            heavy_data = b"TRUSTED_SECRET_PAYLOAD_" + os.urandom(1024 * 10)
            print(f"📤 [Dealer] Отправляю тяжелый ответ (10240 байт)...")
            writer.write(heavy_data)
            # В aioquic writer.write не блокирующий, но мы можем подождать
        except Exception as e:
            print(f"❌ Ошибка в стриме: {e}")

    # Это тот самый хендлер, который вызывает библиотека
    def stream_handler(reader, writer):
        # Мы создаем задачу, чтобы корутина handle_stream выполнилась
        asyncio.create_task(handle_stream(reader, writer))

    print(f"🚀 [Dealer] Слушает на {host}:{port} (QUIC/UDP)")
    await serve(host, port, configuration=configuration, stream_handler=stream_handler)
    await asyncio.Future()

async def run_client(host, port):
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = ssl.CERT_NONE
    
    print(f"🤝 [Node] Пытаюсь подключиться к Дилеру {host}:{port}...")
    try:
        async with connect(host, port, configuration=configuration) as client:
            reader, writer = await client.create_stream()
            print(f"✨ [Node] TLS 1.3 Handshake OK!")
            
            # Отправляем небольшой запрос
            writer.write(b"GIVE_ME_KEY")
            
            # Ждем тяжелый ответ
            print(f"⏳ [Node] Ожидаю данные от дилера...")
            response = await asyncio.wait_for(reader.read(15000), timeout=10.0)
            print(f"📥 [Node] УСПЕХ! Получено {len(response)} байт без ошибок контрольной суммы.")
    except Exception as e:
        print(f"💥 [Node] Ошибка связи или дешифровки: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["server", "client"])
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8012)
    args = parser.parse_args()
    
    if args.mode == "server":
        asyncio.run(run_server(args.host, args.port))
    else:
        asyncio.run(run_client("172.20.0.99", 8012))