#!/usr/bin/env python3
"""Пункт 3 задания (методичка, с. 21, пп. 1-4):

  1) создать картинку со своими ФИО в формате BMP;
  2) зашифровать её шифром DES в режиме ECB;
  3) зашифровать её же шифром DES в режиме CBC с тем же ключом;
  4) сохранить шифровки в виде картинок для отчёта.

Шифруется массив пикселей, заголовок BMP (54 байта) остаётся открытым —
иначе файл перестанет быть картинкой. Именно так это делает и CrypTool.

DES берётся из OpenSSL (legacy-провайдер); корректность проверяется
эталонным тест-вектором 133457799BBCDFF1 / 0123456789ABCDEF -> 85E813540F0AB405.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / 'img' / 'modes'

W, H = 600, 400           # 600*3 = 1800 байт на строку (кратно 4), 1800*400 кратно 8
HEADER = 54               # BMP: 14 байт file header + 40 байт DIB header
KEY = '0123456789ABCDEF'  # ключ DES, 64 бита (hex)
IV = '0001020304050607'   # вектор инициализации для CBC, 64 бита (hex)

FIO = 'Щеглов М.А.'
FONT_PATHS = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
]


def openssl_des(data: bytes, mode: str) -> bytes:
    """DES в режиме ecb/cbc через OpenSSL с legacy-провайдером, без дополнения."""
    cmd = ['openssl', 'enc', f'-des-{mode}', '-nopad',
           '-provider', 'legacy', '-provider', 'default', '-K', KEY]
    if mode == 'cbc':
        cmd += ['-iv', IV]
    p = subprocess.run(cmd, input=data, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode())
    return p.stdout


def self_test():
    """Проверка DES по эталонному тест-вектору."""
    got = openssl_des(bytes.fromhex('0123456789ABCDEF'), 'ecb')
    key_backup = KEY
    assert key_backup is not None
    expected = '85E813540F0AB405'
    # тест-вектор задан для ключа 133457799BBCDFF1, поэтому вызываем напрямую
    p = subprocess.run(
        ['openssl', 'enc', '-des-ecb', '-nopad', '-provider', 'legacy',
         '-provider', 'default', '-K', '133457799BBCDFF1'],
        input=bytes.fromhex('0123456789ABCDEF'), capture_output=True)
    assert p.stdout.hex().upper() == expected, 'DES работает неверно!'
    print(f'  self-test DES: {p.stdout.hex().upper()} == {expected}  OK')
    return got


def make_source():
    """п.1 — картинка со своими ФИО."""
    img = Image.new('RGB', (W, H), (91, 141, 199))          # синяя рамка
    d = ImageDraw.Draw(img)
    d.rectangle([48, 40, W - 48, H - 40], fill=(255, 255, 255))   # белое поле
    font = None
    for fp in FONT_PATHS:
        if Path(fp).exists():
            font = ImageFont.truetype(fp, 54)
            break
    if font is None:
        font = ImageFont.load_default()
    box = d.textbbox((0, 0), FIO, font=font)
    d.text(((W - (box[2] - box[0])) / 2, (H - (box[3] - box[1])) / 2 - 10),
           FIO, fill=(0, 0, 0), font=font)
    path = OUT / 'src_fio.bmp'
    img.save(path)
    return path


def encrypt_bmp(src: Path, mode: str, dst_bmp: Path):
    """пп.2-3 — зашифрование массива пикселей, заголовок не трогаем."""
    raw = src.read_bytes()
    head, body = raw[:HEADER], raw[HEADER:]
    tail = len(body) % 8
    core, rest = (body, b'') if tail == 0 else (body[:-tail], body[-tail:])
    enc = openssl_des(core, mode) + rest
    assert len(enc) == len(body), 'длина данных изменилась'
    dst_bmp.write_bytes(head + enc)
    return dst_bmp


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print('Проверка DES:')
    self_test()

    src = make_source()
    print(f'\nп.1  Исходная картинка с ФИО: {src.name}  ({W}x{H}, 24 бита)')

    for mode in ('ecb', 'cbc'):
        bmp = encrypt_bmp(src, mode, OUT / f'enc_{mode}.bmp')
        png = OUT / f'enc_{mode}.png'
        Image.open(bmp).save(png)
        n = 2 if mode == 'ecb' else 3
        print(f'п.{n}  DES в режиме {mode.upper()}: {bmp.name} -> {png.name}')

    Image.open(src).save(OUT / 'src_fio.png')
    print('\nп.4  Шифровки сохранены как картинки (PNG) для отчёта.')
    print(f'     Ключ DES: {KEY}' + (f', IV: {IV}' if True else ''))


if __name__ == '__main__':
    sys.exit(main())
