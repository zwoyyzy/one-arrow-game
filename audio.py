"""游戏音频管理器。

所有声音都由 Python 在内存中合成，不依赖网络下载或外部素材，
因此不会产生版权和资源路径问题。音频设备不可用时会自动静音。
"""

import math
import random
from array import array

import pygame


SAMPLE_RATE = 44100


def _sound_from_samples(samples):
    """把 -1.0 到 1.0 的浮点采样转换为 Pygame Sound。"""
    pcm = array("h")
    for sample in samples:
        value = max(-1.0, min(1.0, sample))
        pcm.append(int(value * 32767))
    return pygame.mixer.Sound(buffer=pcm.tobytes())


def _tone(frequency, duration, volume=0.4, wave="sine", fade=0.04):
    """生成带淡出的单音。"""
    count = int(SAMPLE_RATE * duration)
    samples = []
    for index in range(count):
        time = index / SAMPLE_RATE
        phase = 2 * math.pi * frequency * time
        if wave == "square":
            raw = 1.0 if math.sin(phase) >= 0 else -1.0
        elif wave == "triangle":
            raw = 2 / math.pi * math.asin(math.sin(phase))
        else:
            raw = math.sin(phase)
        envelope = min(1.0, index / max(1, SAMPLE_RATE * 0.008))
        envelope *= min(1.0, (count - index) / max(1, SAMPLE_RATE * fade))
        samples.append(raw * envelope * volume)
    return samples


def _mix(*tracks):
    """混合多条不同长度的音轨。"""
    length = max(len(track) for track in tracks)
    result = [0.0] * length
    for track in tracks:
        for index, value in enumerate(track):
            result[index] += value
    return result


def _sequence(notes, gap=0.0):
    """按顺序拼接 (频率, 时长, 音量, 波形) 音符。"""
    result = []
    for frequency, duration, volume, wave in notes:
        result.extend(_tone(frequency, duration, volume, wave))
        result.extend([0.0] * int(SAMPLE_RATE * gap))
    return result


def _wooden_arrow_release():
    """生成轻木扣击加柔和空气振动的木质箭矢飞出音效。"""
    duration = 0.24
    count = int(SAMPLE_RATE * duration)
    samples = []
    phase = 0.0
    for index in range(count):
        progress = index / count
        # 木质共鸣控制在中低频，避免尖锐的高频扫频。
        frequency = 170 + 360 * progress
        phase += 2 * math.pi * frequency / SAMPLE_RATE
        noise = random.uniform(-1, 1) * 0.025
        envelope = math.sin(math.pi * progress) * (1 - progress * 0.25)
        samples.append((math.sin(phase) * 0.13 + noise) * envelope)
    return samples


class AudioManager:
    """集中管理背景音乐与游戏反馈音效。"""

    def __init__(self):
        self.enabled = False
        self.music_on = True
        self.fly_sfx_on = True
        self.sounds = {}
        self.bgm_channel = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=SAMPLE_RATE,
                    size=-16,
                    channels=1,
                    buffer=512,
                )

            self.sounds = {
                "click": _sound_from_samples(
                    _sequence(((720, 0.055, 0.28, "triangle"),))
                ),
                "fly": _sound_from_samples(
                    _mix(
                        # 轻木块扣击作为起音，再接短促的箭矢空气振动。
                        _mix(
                            _tone(235, 0.055, 0.20, "triangle"),
                            _tone(470, 0.035, 0.06, "sine"),
                        ),
                        [0.0] * int(SAMPLE_RATE * 0.025)
                        + _wooden_arrow_release(),
                    )
                ),
                "block": _sound_from_samples(
                    _mix(
                        _tone(145, 0.18, 0.45, "triangle"),
                        _tone(92, 0.14, 0.22, "sine"),
                    )
                ),
                "clear": _sound_from_samples(
                    _sequence(
                        (
                            (523, 0.10, 0.27, "triangle"),
                            (659, 0.10, 0.27, "triangle"),
                            (784, 0.11, 0.28, "triangle"),
                            (1047, 0.25, 0.30, "sine"),
                        ),
                        gap=0.025,
                    )
                ),
                "fail": _sound_from_samples(
                    _sequence(
                        (
                            (330, 0.15, 0.30, "triangle"),
                            (247, 0.17, 0.32, "triangle"),
                            (165, 0.30, 0.36, "sine"),
                        ),
                        gap=0.02,
                    )
                ),
            }

            # 柔和的马林巴式循环和弦，低音量播放。
            bgm_notes = (
                (262, 0.22, 0.10, "sine"),
                (330, 0.22, 0.09, "sine"),
                (392, 0.22, 0.09, "sine"),
                (330, 0.22, 0.09, "sine"),
                (294, 0.22, 0.10, "sine"),
                (349, 0.22, 0.09, "sine"),
                (440, 0.22, 0.09, "sine"),
                (349, 0.22, 0.09, "sine"),
            )
            self.sounds["bgm"] = _sound_from_samples(
                _sequence(bgm_notes, gap=0.10)
            )
            self.sounds["bgm"].set_volume(0.20)
            self.enabled = True
        except pygame.error:
            # 没有声卡、远程桌面或 CI 环境中自动静音。
            self.enabled = False

    def play(self, name):
        if name == "fly" and not self.fly_sfx_on:
            return
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def start_bgm(self):
        if self.enabled and self.music_on and self.bgm_channel is None:
            self.bgm_channel = self.sounds["bgm"].play(loops=-1)

    def stop_bgm(self):
        if self.bgm_channel is not None:
            self.bgm_channel.stop()
            self.bgm_channel = None

    def toggle_bgm(self):
        """切换背景音乐，保留点击、飞出和碰撞等反馈音效。"""
        self.music_on = not self.music_on
        if self.music_on:
            self.start_bgm()
        else:
            self.stop_bgm()
        return self.music_on

    def toggle_fly_sfx(self):
        """切换箭头飞出音效。"""
        self.fly_sfx_on = not self.fly_sfx_on
        if not self.fly_sfx_on and self.enabled:
            # 如果关闭时已有飞出音效正在播放，立即停止它。
            self.sounds.get("fly").stop()
        return self.fly_sfx_on
