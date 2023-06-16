# 音訊串流與處理

本專案提供實時音訊串流與處理的工具。能夠從麥克風或音訊檔案中讀取音訊，將音訊數據轉換為浮點數組，並經由 WebSocket 傳送。

## 主要檔案

- `client.py`: 主要的客戶端程式碼。包含讀取音訊源，並通過 WebSocket 進行傳送的功能。
- `mic_source.py`: 提供音訊源的類別，包含從檔案或麥克風讀取音訊的功能。
- `requirements.txt`: 本專案所需的 Python 套件列表。

## 環境設置

### 注意事項

- 本程式只是客戶端，需要有一個實際執行辨識的伺服器端才可運行。請確保你已經設置好伺服器端並取得其主機名與端口號。
- 伺服器端必須能夠處理 Base64 編碼的音訊資料，並能夠傳送回音訊分析結果。
- 請確保你的環境中已經安裝了所需的音訊裝置驅動程式，包括麥克風和音訊輸出裝置。

在使用本專案前，請先安裝 Python 3.6 或以上版本，並使用以下指令安裝所需套件：

```shell
pip install -r requirements.txt
```

## 使用方式

以下是使用 `client.py` 的基本命令：

```shell
python client.py "microphone" --host <YOUR_HOST> --port <YOUR_PORT>
```

其中，`<YOUR_HOST>` 與 `<YOUR_PORT>` 為你的伺服器主機與端口。此指令會從麥克風讀取音訊，並將其傳送到指定的 WebSocket 伺服器。

若想從音訊檔案讀取音訊，可以將 `"microphone"` 更換為音訊檔案的路徑。

若想更換音訊串流的參數，可以加入以下參數：

- `--step`: 滑動窗口步長（以秒為單位）。默認為0.5。
- `--sample-rate`: 音訊流的採樣率。默認為16000。
- `--output-file`: 輸出的RTTM文件。默認不寫入文件。

範例：

```shell
python client.py "microphone" --host <YOUR_HOST> --port <YOUR_PORT> --step 1 --sample-rate 32000 --output-file output.txt
```

## 注意事項

本專案為基本的音訊串流工具，並未考慮所有可能的錯誤處理。在實際應用前，可能需要加入更多的錯誤處理與驗證機制。
