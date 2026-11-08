"""Лабораторная работа 3: вариант 3, константы Кузнечика и опыты с AES-CBC.

Требуется Python 3 и пакет cryptography. Запуск: python3 lab3.py all
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import statistics
import time
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7


EXAMPLE_STATE = [50, 55, 49, 56, 50, 56, 49, 56, 50, 56, 52, 53, 57, 48, 52, 53]
WEIGHTS = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 6, 3]
KUZ_COEFF = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]
KUZ_POLY = 0xC3  # x^8 + x^7 + x^6 + x + 1, младшие 8 бит


def toy_step(state: list[int], weights: list[int] = WEIGHTS) -> list[int]:
    """Один шаг именно варианта 3: сумма произведений mod 256, сдвиг влево."""
    if len(state) != 16 or len(weights) != 16:
        raise ValueError("Нужны 16 байт состояния и 16 весов")
    if any(not 0 <= x <= 255 for x in state) or any(not 1 <= x <= 255 for x in weights):
        raise ValueError("Недопустимый байт")
    feedback = sum((a * w) % 256 for a, w in zip(state, weights)) % 256
    return state[1:] + [feedback]


def toy_transform(state: list[int], weights: list[int] = WEIGHTS) -> list[list[int]]:
    states = [state[:]]
    for _ in range(16):
        states.append(toy_step(states[-1], weights))
    return states


def gf_mul(a: int, b: int) -> int:
    out = 0
    for _ in range(8):
        if b & 1:
            out ^= a
        carry = a & 0x80
        a = (a << 1) & 0xFF
        if carry:
            a ^= KUZ_POLY
        b >>= 1
    return out


def kuz_r(state: bytes) -> bytes:
    if len(state) != 16:
        raise ValueError("Блок должен содержать 16 байт")
    feedback = 0
    for a, c in zip(state, KUZ_COEFF):
        feedback ^= gf_mul(a, c)
    return bytes([feedback]) + state[:15]


def kuz_l(state: bytes) -> bytes:
    for _ in range(16):
        state = kuz_r(state)
    return state


def kuz_constant(number: int) -> bytes:
    if not 1 <= number <= 32:
        raise ValueError("Номер константы должен быть от 1 до 32")
    return kuz_l(bytes(15) + bytes([number]))


def aes_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    padder = PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return enc.update(padded) + enc.finalize()


def aes_decrypt_raw(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    return dec.update(ciphertext) + dec.finalize()


def entropy(data: bytes) -> float:
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    length = len(data)
    return -sum((count / length) * math.log2(count / length)
                for count in counts if count)


def candidate_worker(args: tuple[int, int, bytes, bytes, bytes, float]):
    start, end, prefix, iv, ciphertext, threshold = args
    best = (float("inf"), None)
    for suffix in range(start, end):
        key = prefix + suffix.to_bytes(2, "big")
        raw = aes_decrypt_raw(key, iv, ciphertext)
        score = entropy(raw)
        if score < best[0]:
            best = score, suffix
    return best


def benchmark(key: bytes, iv: bytes, ciphertext: bytes, cores: int, repeats: int = 2):
    prefix = key[:14]
    tasks = [(a, min(a + 2048, 65536), prefix, iv, ciphertext, 5.6)
             for a in range(0, 65536, 2048)]
    measurements = []
    best = None
    for _ in range(repeats):
        start = time.perf_counter()
        if cores == 1:
            scores = list(map(candidate_worker, tasks))
        else:
            with mp.Pool(cores) as pool:
                scores = pool.map(candidate_worker, tasks)
        measurements.append(time.perf_counter() - start)
        best = min(scores)
    return {"cores": cores, "seconds": measurements,
            "median_seconds": statistics.median(measurements),
            "best_entropy": best[0], "found_key_suffix": f"{best[1]:04x}"}


class PaddingOracle:
    def __init__(self, key: bytes):
        self.key = key
        self.queries = 0

    def valid(self, previous: bytes, target: bytes) -> bool:
        self.queries += 1
        raw = aes_decrypt_raw(self.key, previous, target)
        pad = raw[-1]
        return 1 <= pad <= 16 and raw[-pad:] == bytes([pad]) * pad


def attack_block(oracle: PaddingOracle, previous: bytes, target: bytes):
    # Фаза 1: первое изменение справа, нарушающее исходное дополнение.
    phase1_start = oracle.queries
    padding_length = None
    for i in range(16):
        altered = bytearray(previous)
        altered[i] ^= 1
        if not oracle.valid(bytes(altered), target):
            padding_length = 16 - i
            break
    if padding_length is None:
        raise RuntimeError("Не удалось определить длину дополнения")
    phase1_queries = oracle.queries - phase1_start

    # Фаза 2: восстановление последнего байта промежуточного состояния.
    intermediate = [0] * 16
    phase2_start = oracle.queries
    for guess in range(256):
        crafted = bytearray(previous)
        crafted[15] = guess
        if oracle.valid(bytes(crafted), target):
            # Отсекаем случайную валидность из-за дополнения длиной > 1.
            crafted[14] ^= 1
            if oracle.valid(bytes(crafted), target):
                intermediate[15] = guess ^ 1
                break
    else:
        raise RuntimeError("Не удалось восстановить последний байт")
    phase2_queries = oracle.queries - phase2_start

    # Фаза 3: остальные байты, справа налево.
    phase3_start = oracle.queries
    for pad in range(2, 17):
        pos = 16 - pad
        crafted = bytearray(previous)
        for j in range(pos + 1, 16):
            crafted[j] = intermediate[j] ^ pad
        for guess in range(256):
            crafted[pos] = guess
            if oracle.valid(bytes(crafted), target):
                intermediate[pos] = guess ^ pad
                break
        else:
            raise RuntimeError(f"Не удалось восстановить байт {pos}")
    phase3_queries = oracle.queries - phase3_start
    plain = bytes(a ^ b for a, b in zip(intermediate, previous))
    return {"padding_length": padding_length,
            "phase_queries": [phase1_queries, phase2_queries, phase3_queries],
            "total_queries": oracle.queries, "plaintext_hex": plain.hex(),
            "plaintext_repr": repr(plain), "success": plain.endswith(bytes([padding_length]) * padding_length)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["all", "toy", "constant", "benchmark", "oracle"])
    parser.add_argument("--n", type=int, default=28, help="Две последние цифры студенческого билета")
    parser.add_argument("--cores", default="1,2,4")
    parser.add_argument("--output", default="results.json")
    args = parser.parse_args()
    output = {}
    if args.command in ("all", "toy"):
        states = toy_transform(EXAMPLE_STATE)
        assert states[1][-1] == 227
        output["toy"] = {"input": states[0], "weights": WEIGHTS, "after_one": states[1],
                         "after_sixteen": states[-1], "states": states}
    if args.command in ("all", "constant"):
        assert kuz_constant(1).hex() == "6ea276726c487ab85d27bd10dd849401"
        c = kuz_constant(args.n + 2)
        output["constant"] = {"N": args.n, "number": args.n + 2,
                              "rfc_hex": c.hex(), "habr_byte_order_hex": c[::-1].hex(),
                              "c1_rfc_check": True}
    if args.command in ("all", "benchmark"):
        # 1000 знаков английского текста и фиксированные воспроизводимые параметры.
        phrase = ("Cryptography protects data when keys remain secret and implementations "
                  "handle errors without leaking information. ")
        plaintext = (phrase * 12)[:1000].encode("ascii")
        key = bytes.fromhex("00112233445566778899aabbccdda73b")
        iv = bytes.fromhex("102030405060708090a0b0c0d0e0f000")
        ciphertext = aes_encrypt(key, iv, plaintext)
        cores = [int(x) for x in args.cores.split(",")]
        rows = [benchmark(key, iv, ciphertext, c) for c in cores]
        assert all(x["found_key_suffix"] == "a73b" for x in rows)
        one_core = next(x["median_seconds"] for x in rows if x["cores"] == 1)
        output["benchmark"] = {"plaintext_length": len(plaintext), "plaintext": plaintext.decode(),
                               "key_hex": key.hex(), "iv_hex": iv.hex(),
                               "ciphertext_hex": ciphertext.hex(), "measurements": rows,
                               "estimated_one_core_seconds": {
                                   "2_unknown_bytes": one_core,
                                   "4_unknown_bytes": one_core * 65536,
                                   "6_unknown_bytes": one_core * 65536**2,
                               },
                               "method": "Полный просмотр 2^16 ключей; энтропия полного расшифрованного текста; 2 повтора. Для 2^32/2^48 — линейная экстраполяция, не измерение."}
    if args.command in ("all", "oracle"):
        key = bytes.fromhex("00112233445566778899aabbccddeeff")
        iv = bytes.fromhex("102030405060708090a0b0c0d0e0f000")
        first = b"LAB3 CBC DEMO:  "
        second = b"Shcheglov M.A.!"  # 15 байт, во втором блоке; PKCS#7 добавит 01.
        assert len(first) == 16 and len(second) == 15
        ciphertext = aes_encrypt(key, iv, first + second)
        oracle = PaddingOracle(key)
        attack = attack_block(oracle, ciphertext[:16], ciphertext[16:32])
        assert bytes.fromhex(attack["plaintext_hex"]) == second + b"\x01"
        output["oracle"] = {"name_original": "Щеглов М.А.", "name_translit": "Shcheglov M.A.",
                            "first_block": first.decode(), "second_block": second.decode(),
                            "key_hex": key.hex(), "iv_hex": iv.hex(),
                            "ciphertext_hex": ciphertext.hex(), **attack}
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, data in output.items():
        if name == "toy":
            print("L1:", data["after_one"], "\nL16:", data["after_sixteen"])
        elif name == "constant":
            print(f"C{data['number']} (RFC): {data['rfc_hex']}")
            print(f"C{data['number']} (порядок статьи): {data['habr_byte_order_hex']}")
        elif name == "benchmark":
            for row in data["measurements"]:
                print(f"{row['cores']} ядер: {row['seconds']}, ключ {row['found_key_suffix']}")
        else:
            print("Padding Oracle:", data)


if __name__ == "__main__":
    mp.freeze_support()
    main()
