import argparse
import base64
from pathlib import Path
from threading import Thread
from typing import Optional, Text

import mic_source as src
import numpy as np
import rx.operators as ops
from websocket import WebSocket


def encode_audio(waveform: np.ndarray) -> Text:
    # 將音頻數據轉換為浮點型並轉換為字節數據
    data = waveform.astype(np.float32).tobytes()
    # 使用Base64編碼將字節數據轉換為文本字符串
    return base64.b64encode(data).decode("utf-8")


def send_audio(ws: WebSocket, source: Text, step: float, sample_rate: int):
    # 創建音頻源
    block_size = int(np.rint(step * sample_rate))
    source_components = source.split(":")
    if source_components[0] != "microphone":
        # 音頻來源是一個文件
        audio_source = src.FileAudioSource(source, sample_rate)
    else:
        # 音頻來源是麥克風
        device = int(source_components[1]) if len(source_components) > 1 else None
        audio_source = src.MicrophoneAudioSource(sample_rate, block_size, device)

    # 編碼音頻數據，然後通過WebSocket發送
    audio_source.stream.pipe(
        ops.map(encode_audio)
    ).subscribe_(ws.send)

    # 開始讀取音頻
    audio_source.read()


def receive_audio(ws: WebSocket, output: Optional[Path]):
    while True:
        # 接收從WebSocket接收到的音頻消息並打印
        message = ws.recv()
        print(message, end="")

        if output is not None:
            # 如果提供了輸出路徑，則將音頻消息寫入文件
            with open(output, "a") as file:
                file.write(message)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=str, help="'microphone' | 'microphone:<DEVICE_ID>'")
    parser.add_argument("--host", required=True, type=str, help="伺服器主機")
    parser.add_argument("--port", required=True, type=int, help="伺服器端口")
    parser.add_argument("--step", default=0.5, type=float, help="滑動窗口步長（以秒為單位）。默認為0.5")
    parser.add_argument("-sr", "--sample-rate", default=16000, type=int, help="音頻流的採樣率。默認為16000")
    parser.add_argument("-o", "--output-file", type=Path, help="輸出的RTTM文件。默認不寫入文件")
    args = parser.parse_args()

    # 運行WebSocket客戶端
    ws = WebSocket()
    ws.connect(f"ws://{args.host}:{args.port}")
    sender = Thread(target=send_audio, args=[ws, args.source, args.step, args.sample_rate])
    receiver = Thread(target=receive_audio, args=[ws, args.output_file])
    sender.start()
    receiver.start()


if __name__ == "__main__":
    run()
