from queue import SimpleQueue
from typing import Text, Optional, Union, Tuple

import sounddevice as sd
from rx.subject import Subject

class AudioSource:
    """代表音訊來源的類別，可以通過 `stream` 屬性開始串流。

    Parameters
    ----------
    uri: Text
        音訊來源的唯一標識符。
    sample_rate: int
        音訊來源的取樣率。
    """
    def __init__(self, uri: Text, sample_rate: int):
        self.uri = uri
        self.sample_rate = sample_rate
        self.stream = Subject()

    @property
    def duration(self) -> Optional[float]:
        """如果已知，則返回串流的持續時間。默認為 None（未知持續時間）。
        """
        return None

    def read(self):
        """開始讀取音訊來源並透過串流發送音訊樣本。"""
        raise NotImplementedError

    def close(self):
        """停止讀取音訊來源並關閉所有打開的串流。"""
        raise NotImplementedError


class MicrophoneAudioSource(AudioSource):
    """與本地麥克風相關的音訊來源。

    Parameters
    ----------
    sample_rate: int
        每個音訊區塊的取樣率。
    block_size: int
        每個區塊中的音訊樣本數。默認為 1000。
    device: int | str | (int, str) | None
        sounddevice 等效的設備標識符。
        如果為 None，則使用默認設備。
        默認為 None。
    """

    def __init__(
        self,
        sample_rate: int,
        block_size: int = 1000,
        device: Optional[Union[int, Text, Tuple[int, Text]]] = None,
    ):
        super().__init__("live_recording", sample_rate)
        self.block_size = block_size
        self._mic_stream = sd.InputStream(
            channels=1,
            samplerate=sample_rate,
            latency=0,
            blocksize=self.block_size,
            callback=self._read_callback,
            device=device,
        )
        self._queue = SimpleQueue()

    def _read_callback(self, samples, *args):
        self._queue.put_nowait(samples[:, [0]].T)

    def read(self):
        self._mic_stream.start()
        while self._mic_stream:
            try:
                while self._queue.empty():
                    if self._mic_stream.closed:
                        break
                self.stream.on_next(self._queue.get_nowait())
            except BaseException as e:
                self.stream.on_error(e)
                break
        self.stream.on_completed()
        self.close()

    def close(self):
        self._mic_stream.stop()
        self._mic_stream.close()
