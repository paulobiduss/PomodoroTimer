"""Gera o som de notificacao (assets/notify.wav).

1. Intencao: Produzir um alerta suave, sem susto, para o fim de cada bloco.
2. Transformacao: Sintetiza duas notas de sino (senoide + parciais leves) com
   ataque gradual e decaimento exponencial, em volume moderado.
3. Destino: Escreve um WAV mono 16 bits / 44.1 kHz em assets/notify.wav.

Uso: python tools/generate_notify_sound.py
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44100
BIT_DEPTH_MAX = 32767

# Pico bem abaixo do full scale: o som antigo tocava em 0 dBFS e assustava.
PEAK_AMPLITUDE = 0.30

# Duas notas descendentes (E5 -> C5): intervalo consonante e acolhedor.
NOTES = (
    # (frequencia_hz, inicio_s, duracao_s, ganho_relativo)
    (659.26, 0.00, 1.60, 1.00),
    (523.25, 0.28, 1.90, 0.85),
)

# Parciais suaves: dao corpo de sino sem brilho agressivo.
PARTIALS = ((1.0, 1.00), (2.0, 0.22), (3.0, 0.07))

ATTACK_S = 0.020  # ataque curto, mas nao instantaneo (evita o "click" seco)
DECAY_TAU_S = 0.45  # constante de decaimento exponencial
RELEASE_S = 0.12  # fade-out final para nao cortar a cauda


def _envelope(t: float, duration: float) -> float:
    """Envelope ataque-decaimento-release normalizado entre 0 e 1."""
    if t < 0.0 or t > duration:
        return 0.0
    if t < ATTACK_S:
        # Ataque em cosseno: mais macio que uma rampa linear.
        attack = 0.5 - 0.5 * math.cos(math.pi * t / ATTACK_S)
    else:
        attack = 1.0
    decay = math.exp(-(t - ATTACK_S) / DECAY_TAU_S) if t > ATTACK_S else 1.0
    remaining = duration - t
    release = min(1.0, remaining / RELEASE_S) if RELEASE_S > 0 else 1.0
    return attack * decay * release


def _render() -> list[float]:
    total_s = max(start + duration for _, start, duration, _ in NOTES)
    total_frames = int(total_s * SAMPLE_RATE)
    samples = [0.0] * total_frames

    for freq, start, duration, gain in NOTES:
        start_frame = int(start * SAMPLE_RATE)
        note_frames = int(duration * SAMPLE_RATE)
        for i in range(note_frames):
            index = start_frame + i
            if index >= total_frames:
                break
            t = i / SAMPLE_RATE
            value = 0.0
            for ratio, weight in PARTIALS:
                value += weight * math.sin(2.0 * math.pi * freq * ratio * t)
            samples[index] += gain * value * _envelope(t, duration)

    peak = max((abs(s) for s in samples), default=0.0)
    if peak > 0.0:
        scale = PEAK_AMPLITUDE / peak
        samples = [s * scale for s in samples]
    return samples


def write_wav(destination: Path) -> Path:
    samples = _render()
    frames = struct.pack(
        "<%dh" % len(samples),
        *[max(-BIT_DEPTH_MAX, min(BIT_DEPTH_MAX, int(round(s * BIT_DEPTH_MAX)))) for s in samples],
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(frames)
    return destination


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "assets" / "notify.wav"
    write_wav(output)
    print(f"Som gerado em: {output}")
