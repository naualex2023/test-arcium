import argparse
import asyncio
import os
import ssl
import sys
from aioquic.asyncio import connect, serve
from aioquic.quic.configuration import QuicConfiguration

def log(msg):
    print(msg, flush=True)

async def run_server(host, port):
    log(f"🛠 [Dealer] Загрузка TLS на {host}:{port}...")
    cert_file, key_file = "cert.pem", "key.pem"
    
    if not os.path.exists(cert_file):
        log("❌ [Dealer] КРИТИЧЕСКАЯ ОШИБКА: Файлы .pem не найдены!")
        return

    try:
        configuration = QuicConfiguration(is_client=False)
        configuration.load_cert_chain(cert_file, key_file)
    except Exception as e:
        log(f"💥 [Dealer] Ошибка конфига: {e}")
        return

    async def handle_stream(reader, writer):
        log("📩 [Dealer] Входящий стрим подтвержден!")
        try:
            await reader.read(1024)
            writer.write(b"DATA_START_" + b"A" * 10240 + b"_DATA_END")
            await writer.drain()
            writer.write_eof()
            log("📤 [Dealer] 10KB данных отправлено.")
        except Exception as e:
            log(f"❌ [Dealer] Ошибка при передаче: {e}")

    try:
        await serve(
            host, port, 
            configuration=configuration, 
            stream_handler=lambda r, w: asyncio.create_task(handle_stream(r, w))
        )
        log("🔌 [Dealer] UDP СОКЕТ ОТКРЫТ И СЛУШАЕТ.")
        await asyncio.Future()
    except Exception as e:
        log(f"💥 [Dealer] Ошибка запуска сокета: {e}")

async def run_client(host, port):
    log(f"🤝 [Node] Попытка подключения к {host}:{port}...")
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = ssl.CERT_NONE
    
    # Ждем, пока сервер точно отрапортует об открытии сокета
    await asyncio.sleep(2)
    
    try:
        async with connect(host, port, configuration=configuration) as client:
            log("✨ [Node] QUIC соединение установлено!")
            reader, writer = await client.create_stream()
            writer.write(b"GET")
            
            data = b""
            while True:
                chunk = await asyncio.wait_for(reader.read(4096), timeout=5.0)
                if not chunk: break
                data += chunk
                log(f"📦 [Node] Получено: {len(data)} байт")
            
            log(f"🏁 ТЕСТ ЗАВЕРШЕН: Принято {len(data)} байт.")
    except Exception as e:
        log(f"💥 [Node] Ошибка связи: {type(e).__name__}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["server", "client"])
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8012)
    args = parser.parse_args()

    if args.mode == "server":
        asyncio.run(run_server("0.0.0.0", args.port))
    else:
        asyncio.run(run_client(args.host, args.port))