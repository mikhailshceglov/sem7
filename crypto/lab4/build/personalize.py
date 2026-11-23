from pathlib import Path
p=Path('lab4/build/make.py')
s=p.read_text()
start=s.index("slide('Keccak: выбор параметров'")
end=s.index("\nslide(",start+1)
s=s[:start]+"slide('Keccak: параметры варианта 28','l = 28 mod 7 = 0.\u005cnРазмер состояния: b = 25 · 2⁰ = 25 бит, массив 5 × 5 × 1.\u005cnЧисло раундов: nr = 12 + 2l = 12.\u005cnУчебный набор: r = 1 бит, c = 24 бита, d = 24 бита. Условие r + c = b выполняется.\u005cnПри минимальном положительном r ёмкость максимальна. Общая оценка стойкости к коллизиям ограничена min(d/2, c/2) = 12 битами.\u005cnДля состояния 25 бит практически безопасного набора нет. Вариант подходит только для изучения перестановки.','', 'Скриншоты предыдущего слайда сохранены из примера и относятся к состоянию 200 бит.')".replace('\n','\\n')+s[end:]
start=s.index("slide('Персональный ключ'")
end=s.index("\nslide(",start+1)
s=s[:start]+'''slide('Персональный ключ PBKDF-1',f'Пароль P (UTF-8): Щеглов Михаил Алексеевич 18.02.2005.\\nСоль S (HEX): {salt.hex().upper()}, 8 байт.\\nHash = SHA-1, c = 1000, dkLen = 20 байт.\\nDK (HEX):\\n{key.hex().upper()[:20]} {key.hex().upper()[20:]}\\nКлюч сохранён в pbkdf1_key.hex и используется обеими сторонами HMAC.\\nПерсональные данные предсказуемы: длина ключа 160 бит не означает стойкость пароля 160 бит.','', 'Персональный расчёт выполнен программно. Скриншоты CrypTool 2 сохранены из исходного примера.')'''+s[end:]
s=s.replace("slide('HMAC: протокол контроля целостности'","hs=slide('HMAC: протокол контроля целостности'")
marker="slide('DH: получение ключа длиной 256 бит'"
pos=s.index(marker)
s=s[:pos]+'''text(hs, 'Персональный DK: HMAC-SHA-1 для Hello world!\\n' + tag.hex().upper() + '   Совпадение: True', 1, 12, 26, 1.6, 'Body')
'''+s[pos:]
s=s.replace('Обе стороны используют один DK из PBKDF-1. Получатель принимает M*, если HMACК(M*) = MAC.','Схемы из примера. Ниже результат программной проверки с персональным ключом PBKDF-1.')
s=s.replace('PBKDF-1 и HMAC: рассмотрены получение ключа из пароля и проверка целостности с общим ключом.','PBKDF-1 и HMAC: из персонального пароля получен и сохранён 160-битный ключ. Программная проверка HMAC подтвердила совпадение кодов.')
s=s.replace('Стойкость зависит от ёмкости и длины выхода.','Для варианта 28 состояние имеет 25 бит и не обеспечивает практической безопасности.')
s='''import hashlib,hmac,json
from pathlib import Path
password='Щеглов Михаил Алексеевич 18.02.2005'
salt=bytes.fromhex('b90d72e4a36f851c')
key=hashlib.sha1(password.encode('utf-8')+salt).digest()
for _ in range(999):key=hashlib.sha1(key).digest()
tag=hmac.new(key,b'Hello world!',hashlib.sha1).digest()
assert hmac.compare_digest(tag,hmac.new(bytes.fromhex(key.hex()),b'Hello world!',hashlib.sha1).digest())
Path('lab4/pbkdf1_key.hex').write_text(key.hex().upper()+'\\n')
Path('lab4/pbkdf1_parameters.json').write_text(json.dumps(dict(password=password,encoding='UTF-8',salt_hex=salt.hex(),hash='SHA-1',iterations=1000,dkLen=20,key_hex=key.hex(),message='Hello world!',hmac_sha1=tag.hex()),ensure_ascii=False,indent=2)+'\\n')
'''+s
p.write_text(s)
