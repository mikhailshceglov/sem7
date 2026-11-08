#!/usr/bin/env python3
"""Расчёт таблицы дифференциального распределения (DDT) 4x4 S-блока.

Запуск:
    python3 ddt.py                 — S-блок №1 упрощённого шифра (DA_Tutor)
    python3 ddt.py magma           — S-блок №1 шифра «Магма» (ГОСТ Р 34.12-2015)
    python3 ddt.py 12,4,6,2,...    — произвольный S-блок (16 значений через запятую)

DDT[dX][dY] = #{ X : S(X) xor S(X xor dX) = dY },  P(dY|dX) = DDT[dX][dY]/16.
Сильной считается характеристика с P > 0.25.
"""
import sys

# S-блок №1 упрощённого шифра, восстановленный из DDT приложения DA_Tutor
# (см. LOG.md, п. 3: восстановление с точностью до XOR-констант входа/выхода).
SBOX_SIMPLE = [0, 1, 13, 12, 4, 5, 9, 11, 7, 10, 6, 8, 15, 14, 2, 3]

# S-блок №1 шифра «Магма», ГОСТ Р 34.12-2015, таблица пи_0
SBOX_MAGMA = [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1]


def ddt(sbox):
    """Таблица дифференциального распределения 16x16."""
    t = [[0] * 16 for _ in range(16)]
    for dX in range(16):
        for X in range(16):
            dY = sbox[X] ^ sbox[X ^ dX]
            t[dX][dY] += 1
    return t


def strong(t, threshold=0.25):
    """Сильные дифференциальные характеристики: P(dY|dX) > threshold, dX != 0."""
    out = []
    for dX in range(1, 16):
        for dY in range(16):
            p = t[dX][dY] / 16
            if p > threshold:
                out.append((dX, dY, t[dX][dY], p))
    return sorted(out, key=lambda r: -r[3])


def show(t, title):
    print(title)
    print('     ' + ''.join(f'{j:4d}' for j in range(16)))
    print('    +' + '-' * 64)
    for i in range(16):
        print(f'{i:3d} |' + ''.join(f'{v:4d}' for v in t[i]))
    # контроль: каждая строка в сумме даёт 16
    assert all(sum(r) == 16 for r in t), 'нарушен контроль: сумма строки != 16'
    assert t[0][0] == 16, 'нарушен контроль: DDT[0][0] != 16'
    print('\nКонтроль пройден: сумма каждой строки = 16, DDT[0][0] = 16.')

    s = strong(t)
    print(f'\nСильные дифференциальные характеристики (P > 0.25): {len(s)} шт.')
    print('  dX        dY        Кол-во  Вероятность')
    for dX, dY, c, p in s:
        print(f'  {dX:2d} ({dX:04b})  {dY:2d} ({dY:04b})  {c:4d}    {p:.4f}')


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    if arg == 'magma':
        sbox, title = SBOX_MAGMA, 'DDT S-блока №1 шифра «Магма» (ГОСТ Р 34.12-2015)'
    elif ',' in arg:
        sbox = [int(x) for x in arg.split(',')]
        assert sorted(sbox) == list(range(16)), 'S-блок должен быть перестановкой 0..15'
        title = 'DDT заданного S-блока'
    else:
        sbox, title = SBOX_SIMPLE, 'DDT S-блока №1 упрощённого шифра'
    print('S-блок:', sbox, '\n')
    show(ddt(sbox), title)


if __name__ == '__main__':
    main()
