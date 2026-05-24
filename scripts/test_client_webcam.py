import asyncio
import cv2
import websockets
import json
import base64
import argparse
import sys
import subprocess
import tempfile
import platform

def play_audio(audio_bytes: bytes):
    """
    Riproduce i byte audio WAV ricevuti dal server in modo non bloccante.
    """
    try:
        # Creiamo un file temporaneo WAV per salvare l'audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            temp_wav.write(audio_bytes)
            temp_path = temp_wav.name

        # Determina il riproduttore audio nativo in base al sistema operativo
        current_os = platform.system()
        if current_os == "Darwin":  # macOS
            # afplay è integrato su macOS e riproduce audio in background senza bloccare python
            subprocess.Popen(["afplay", temp_path])
        elif current_os == "Linux":
            # Tenta di usare paplay (Pulse/Pipewire) o aplay (ALSA) su Linux
            try:
                subprocess.Popen(["paplay", temp_path])
            except FileNotFoundError:
                subprocess.Popen(["aplay", temp_path])
        else:
            print("[Client] Riproduzione audio non supportata nativamente su questo OS.")
    except Exception as e:
        print(f"[Client] Errore durante la riproduzione audio: {e}")

async def send_frames(websocket, cap, mode):
    """
    Invia i frame catturati dalla webcam del Mac al server via WebSocket.
    """
    print("[Client] Avvio dello streaming video...")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.03)
                continue

            # Ridimensioniamo il frame per risparmiare banda di rete (es. 640x480)
            frame_resized = cv2.resize(frame, (640, 480))
            
            # Mostra la finestra video locale
            cv2.imshow("Webcam Mac (Premi 'q' per uscire)", frame_resized)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[Client] Interruzione manuale da tastiera.")
                break

            # Codifica del frame in JPEG
            _, buffer = cv2.imencode(".jpg", frame_resized)
            
            # Conversione in Base64
            image_base64 = base64.b64encode(buffer).decode("utf-8")

            # Payload JSON per il server
            payload = {
                "image": image_base64,
                "caption_mode": mode,
                "pointing_coordinates": None
            }

            # Invio del JSON via WebSocket
            await websocket.send(json.dumps(payload))
            
            # Invio di circa 10 frame al secondo
            await asyncio.sleep(0.1)
            
    except asyncio.CancelledError:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()

async def receive_audio(websocket):
    """
    Riceve le risposte audio in formato WAV dal server e le riproduce.
    """
    print("[Client] In ascolto per risposte audio dal server...")
    try:
        async for message in websocket:
            # Il server restituisce l'audio come dati binari (bytes)
            if isinstance(message, bytes):
                print(f"[Client] Ricevuto audio WAV dal server ({len(message)} byte). Riproduzione...")
                play_audio(message)
    except websockets.exceptions.ConnectionClosed:
        print("[Client] Connessione chiusa dal server.")
    except Exception as e:
        print(f"[Client] Errore di ricezione: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Webcam Client per vision-caption")
    parser.add_argument("--host", default="localhost", help="IP/Host del server WebSocket (es. IP della macchina Linux)")
    parser.add_argument("--port", type=int, default=8765, help="Porta del server WebSocket")
    parser.add_argument("--mode", default="AUTO", choices=["AUTO", "POINTING"], help="Modalità di acquisizione")
    args = parser.parse_args()

    uri = f"ws://{args.host}:{args.port}/ws/vision"
    print(f"[Client] Tentativo di connessione a: {uri}...")

    # Apertura della fotocamera (webcam di default del Mac)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[Client] Errore: Impossibile accedere alla webcam.")
        sys.exit(1)

    try:
        async with websockets.connect(uri) as websocket:
            print("[Client] Connessione stabilita con successo!")
            
            # Avvio dei due task paralleli per invio e ricezione
            send_task = asyncio.create_task(send_frames(websocket, cap, args.mode))
            receive_task = asyncio.create_task(receive_audio(websocket))
            
            # Restiamo in attesa finché uno dei due non termina
            done, pending = await asyncio.wait(
                [send_task, receive_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in pending:
                task.cancel()
                
    except Exception as e:
        print(f"[Client] Connessione fallita: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[Client] Client terminato.")
