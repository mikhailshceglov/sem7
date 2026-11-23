import hashlib,hmac,json
from pathlib import Path
password='Щеглов Михаил Алексеевич 18.02.2005'
salt=bytes.fromhex('b90d72e4a36f851c')
key=hashlib.sha1(password.encode('utf-8')+salt).digest()
for _ in range(999):key=hashlib.sha1(key).digest()
tag=hmac.new(key,b'Hello world!',hashlib.sha1).digest()
assert hmac.compare_digest(tag,hmac.new(bytes.fromhex(key.hex()),b'Hello world!',hashlib.sha1).digest())
Path('lab4/pbkdf1_key.hex').write_text(key.hex().upper()+'\n')
Path('lab4/pbkdf1_parameters.json').write_text(json.dumps(dict(password=password,encoding='UTF-8',salt_hex=salt.hex(),hash='SHA-1',iterations=1000,dkLen=20,key_hex=key.hex(),message='Hello world!',hmac_sha1=tag.hex()),ensure_ascii=False,indent=2)+'\n')
import zipfile,xml.etree.ElementTree as E,glob,io
from PIL import Image
N={'office':'urn:oasis:names:tc:opendocument:xmlns:office:1.0','style':'urn:oasis:names:tc:opendocument:xmlns:style:1.0','text':'urn:oasis:names:tc:opendocument:xmlns:text:1.0','draw':'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0','fo':'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0','svg':'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0','xlink':'http://www.w3.org/1999/xlink','presentation':'urn:oasis:names:tc:opendocument:xmlns:presentation:1.0'}
for k,v in N.items():E.register_namespace(k,v)
def q(k):a,b=k.split(':');return '{'+N[a]+'}'+b
def el(p,t,attrs={},txt=None):
 e=E.SubElement(p,q(t),{q(k):str(v) for k,v in attrs.items()});e.text=txt;return e
z=zipfile.ZipFile('/home/misha/Downloads/крипта4_УАА.odp');root=E.fromstring(z.read('content.xml'));auto=root.find(q('office:automatic-styles'));body=root.find('.//'+q('office:presentation'));old=list(body)
imgs={}
for i,s in enumerate(old,1):imgs[i]=[a.get(q('xlink:href')) for a in s.findall('.//'+q('draw:image'))]
for s in old:body.remove(s)
for name,size,color in [('Title',27,'#202020'),('Body',18,'#252525'),('Small',11,'#666666'),('Cover',32,'#202020')]:
 st=el(auto,'style:style',{'style:name':name,'style:family':'paragraph'});el(st,'style:text-properties',{'fo:font-size':str(size)+'pt','fo:color':color,'fo:font-family':'Liberation Sans'});el(st,'style:paragraph-properties',{'fo:margin-bottom':'0.28cm'})
st=el(auto,'style:style',{'style:name':'White','style:family':'drawing-page'});el(st,'style:drawing-page-properties',{'draw:fill':'solid','draw:fill-color':'#ffffff','presentation:background-visible':'true','presentation:background-objects-visible':'false'})
st=el(auto,'style:style',{'style:name':'Plain','style:family':'graphic'});el(st,'style:graphic-properties',{'draw:stroke':'none','draw:fill':'none','fo:padding':'0cm','draw:textarea-vertical-align':'top'})
def text(s,txt,x,y,w,h,sty='Body'):
 f=el(s,'draw:frame',{'draw:style-name':'Plain','svg:x':f'{x}cm','svg:y':f'{y}cm','svg:width':f'{w}cm','svg:height':f'{h}cm'});b=el(f,'draw:text-box')
 for line in txt.split('\n'):el(b,'text:p',{'text:style-name':sty},line)
def pic(s,i,j,x,y,w,h):
 p=imgs[i][j];a=Image.open(io.BytesIO(z.read(p)));ratio=min(w/a.width,h/a.height);ww=a.width*ratio;hh=a.height*ratio
 f=el(s,'draw:frame',{'svg:x':f'{x+(w-ww)/2}cm','svg:y':f'{y+(h-hh)/2}cm','svg:width':f'{ww}cm','svg:height':f'{hh}cm'});el(f,'draw:image',{'xlink:href':p,'xlink:type':'simple','xlink:show':'embed','xlink:actuate':'onLoad'})
def slide(title,txt='',pictures=[],note=''):
 s=el(body,'draw:page',{'draw:name':f'Слайд {len(body)+1}','draw:style-name':'White','draw:master-page-name':old[0].get(q('draw:master-page-name'))});text(s,title,1,0.65,26,1.6,'Title')
 if txt:text(s,txt,1,2.6,26 if not pictures else 12,11)
 for args in pictures:pic(s,*args)
 text(s,str(len(body)),26,14.7,1,0.5,'Small')
 if note:text(s,note,1,14.4,24,0.7,'Small')
 return s
s=slide('Лабораторная работа № 4');text(s,'Хэш-функции, коды аутентификации\nи управление симметричными ключами',1,4,26,3,'Cover');text(s,'Щеглов Михаил Алексеевич\nГруппа 3381\nРуководитель: Племянников Александр Кимович',1,9,25,3);text(s,'Санкт-Петербургский государственный электротехнический университет «ЛЭТИ»\nСанкт-Петербург, 2026',1,13.2,25,1.2,'Small')
slide('Цель работы','Приобретение теоретических знаний и практических навыков в области устройства и криптоанализа функций хэширования, построения имитовставок, диверсификации и согласования ключей.\nЗадачи работы:\n1. Изучить MD5 и атаку расширением сообщения на MAC.\n2. Сравнить лавинный эффект SHA-1, SHA-256, SHA-512 и SHA-3.\n3. Рассмотреть перестановку Keccak и выбор её параметров.\n4. Изучить получение ключа с помощью PBKDF-1.\n5. Рассмотреть протокол контроля целостности на основе HMAC.\n6. Получить 256-битный ключ в DH и разобрать атаку посредником.')
slide('MD5: схема Меркла — Дамгарда','Сообщение дополняется единицей, нулями и 64-битным представлением исходной длины.\nБлоки Yq имеют длину 512 бит.\nMDq+1 = HMD5(MDq, Yq).\nНачальное состояние задаётся IV. Итоговый MDL имеет длину 128 бит.\nФункция сжатия выполняет 4 цикла по 16 шагов.',[(3,0,14,2.8,13,10)],'Обозначения и схема: лекция 8, раздел «Хэш-функция MD5».')
slide('Атака расширением сообщения','Уязвимая конструкция: MAC = MD5(K || M).\nНарушитель знает M, MAC и длину K либо подбирает её.\nОн использует MAC как состояние MD5 и продолжает хэширование добавления X.\nM′ = M || pad(K || M) || X.\nНовый MAC вычисляется без знания K, с учётом полной длины данных.',[(4,0,16,2.5,9,11)])
slide('MAC: отправитель и получатель','',[(6,0,1,2.5,12.7,9.5),(6,1,14.2,2.5,12.7,9.5)],'Скриншоты из примера: M = some message, K = secretkey, добавление &admin=true. Справа результат True.')
slide('Результат атаки на MAC','Получатель вычисляет MD5(K || M′) и сравнивает результат с поддельным MAC.\nНа скриншоте Stream Comparator возвращает True: изменённое сообщение принято.\nПродолжение MD5 с подменой внутренних регистров выполнено программой из примера. CrypTool 2 используется для формирования и проверки MAC.\nПричина уязвимости: открытый дайджест раскрывает состояние итерационной функции. Для контроля целостности следует использовать HMAC.')
slide('Лавинный эффект: методика','Исходный текст: Hello world!\nДля всех функций используется одна последовательность 10 изменений: 1ello world!, 12llo world!, …, 1234567890d!.\nНа каждом шаге сравниваются хэши исходного и изменённого сообщений.\nAᵢ = 100% · dH(H(M), H(Mᵢ)) / n.\nСреднее: A = (A₁ + … + A₁₀) / 10.\nВ схеме SHA-3 оба хэш-блока заменяются на Keccak с одинаковым профилем SHA-3 и длиной выхода.','', 'Экспериментальные скриншоты и округлённые средние перенесены из предоставленного примера.')
for i,name in [(7,'SHA-1'),(8,'SHA-256'),(9,'SHA-512'),(10,'SHA-3')]:
 slide('Лавинный эффект '+name,'',[(i,0,1,2.5,13,9),(i,11,15,3,12,8)],'Слева схема CrypTool 2, справа результаты 10 изменений из примера.')
s=slide('Средняя величина лавинного эффекта')
for j,(name,val) in enumerate([('SHA-1',48.0),('SHA-256',50.8),('SHA-512',49.6),('SHA-3',49.6)]):
 x=3+j*6;h=val/60*8
 st=el(auto,'style:style',{'style:name':'Bar'+str(j),'style:family':'graphic'});el(st,'style:graphic-properties',{'draw:fill':'solid','draw:fill-color':'#305875','draw:stroke':'none'})
 el(s,'draw:rect',{'draw:style-name':'Bar'+str(j),'svg:x':f'{x}cm','svg:y':f'{11-h}cm','svg:width':'3cm','svg:height':f'{h}cm'});text(s,f'{val:.1f} %',x,10-h,4,1);text(s,name,x,11.4,4,1)
text(s,'Средние близки к 50%. Это характеризует диффузию, но не доказывает криптостойкость.',1,13,25,1);text(s,'Данные примера, округление до 0,1 %. Высота столбцов отсчитывается от нуля.',1,14.4,24,.6,'Small')
slide('Keccak: конструкция «губка»','Состояние S состоит из открытой части SA длиной r и скрытой части SC длиной c.\nb = r + c = 25 · 2ˡ.\nВпитывание: блок pi складывается с SA по XOR, затем перестановка f преобразует всё состояние.\nОтжатие: выходные блоки zi считываются из SA. При необходимости снова применяется f.\nСкрытая часть SC не входит в выход Z.',[(11,0,17,2.5,7,11)],'Схема и обозначения: лекция 8, раздел «Хэш-функция Keccak».')
slide('Перестановка Keccak-f','Состояние a[x][y][z]: 5 × 5 × 2ˡ бит.\nЧисло раундов: nr = 12 + 2l.\nКаждый раунд включает пять преобразований:\nθ — перемешивание чётности столбцов.\nρ — циклические сдвиги проходов.\nπ — перестановка проходов.\nχ — нелинейное преобразование строк.\nι — сложение с раундовой константой.')
slide('Keccak: протокол работы из примера','',[(12,0,1,2.6,12,9),(12,1,14,2.6,12,9)],'Параметры примера: l = 3, b = 200, r = 40, c = 160, выход 40 бит, 18 раундов.')
slide('Keccak: параметры варианта 28','l = 28 mod 7 = 0.\nРазмер состояния: b = 25 · 2⁰ = 25 бит, массив 5 × 5 × 1.\nЧисло раундов: nr = 12 + 2l = 12.\nУчебный набор: r = 1 бит, c = 24 бита, d = 24 бита. Условие r + c = b выполняется.\nПри минимальном положительном r ёмкость максимальна. Общая оценка стойкости к коллизиям ограничена min(d/2, c/2) = 12 битами.\nДля состояния 25 бит практически безопасного набора нет. Вариант подходит только для изучения перестановки.','', 'Скриншоты предыдущего слайда сохранены из примера и относятся к состоянию 200 бит.')
slide('PBKDF-1: диверсификация ключа','DK = PBKDF1(P, S, c, dkLen).\nP — пароль, S — соль, c — число итераций.\nT₁ = Hash(P || S).\nTᵢ = Hash(Tᵢ₋₁), i = 2, …, c.\nDK — первые dkLen байт Tc.\nДля SHA-1: dkLen ≤ 20 байт.\nСоль препятствует повторному использованию предварительных таблиц. Итерации замедляют перебор.',[(14,0,16,2.6,9,11)])
slide('PBKDF-1: схема CrypTool 2','',[(15,0,1,2.5,12.5,9),(15,1,14,2.5,12.5,9)],'Исходный пример: SHA-1, 1000 итераций, соль salt. Пароль и ключ на скриншоте принадлежат примеру.')
slide('Персональный ключ PBKDF-1',f'Пароль P (UTF-8): Щеглов Михаил Алексеевич 18.02.2005.\nСоль S (HEX): {salt.hex().upper()}, 8 байт.\nHash = SHA-1, c = 1000, dkLen = 20 байт.\nDK (HEX):\n{key.hex().upper()[:20]} {key.hex().upper()[20:]}\nКлюч сохранён в pbkdf1_key.hex и используется обеими сторонами HMAC.\nПерсональные данные предсказуемы: длина ключа 160 бит не означает стойкость пароля 160 бит.','', 'Персональный расчёт выполнен программно. Скриншоты CrypTool 2 сохранены из исходного примера.')
slide('HMAC: алгоритм вычисления','HMACК(M) = H((K₀ ⊕ opad) ||\n                    H((K₀ ⊕ ipad) || M)).\nK₀ имеет длину блока b бит. Длинный ключ сначала хэшируется, затем дополняется нулями справа.\nipad: повторяющийся байт 0x36.\nopad: повторяющийся байт 0x5C.\nВложенное хэширование предотвращает рассмотренную атаку расширением.',[(16,0,16,2.5,10,11)],'Обозначения: лекция 8. b — длина блока в битах, b/8 — длина в байтах.')
hs=slide('HMAC: протокол контроля целостности','',[(17,0,1,2.5,12.5,9),(17,1,14,2.5,12.5,9)],'Схемы из примера. Ниже результат программной проверки с персональным ключом PBKDF-1.')
text(hs, 'Персональный DK: HMAC-SHA-1 для Hello world!\n' + tag.hex().upper() + '   Совпадение: True', 1, 12, 26, 1.6, 'Body')
slide('DH: получение ключа длиной 256 бит','Открытые параметры: простое p и генератор g.\nСекреты сторон: x и y.\nR₁ = gˣ mod p, R₂ = gʸ mod p.\nK = R₂ˣ mod p = R₁ʸ mod p.\nK₂₅₆ = SHA-256(Encode(K)).\nОбе стороны должны одинаково кодировать K. Длина результата 32 байта не увеличивает энтропию исходного секрета.',[(18,0,14,3,13,8)],'Скриншот модифицированной схемы из примера: общий секрет, Converter, SHA-256.')
slide('DH: атака посредником','Нарушитель подменяет открытые значения R₁ и R₂ своим R₃ = gᶻ mod p.\nСторона A получает K₁ = gˣᶻ mod p, сторона B получает K₂ = gʸᶻ mod p.\nПосредник знает оба ключа и может расшифровывать и изменять сообщения.\nЗащита: аутентификация обмена ключами, например подпись передаваемых параметров.',[(19,0,14,2.5,13,10)])
slide('Заключение','В ходе работы рассмотрены устройство хэш-функций, построение имитовставок, диверсификация и согласование ключей.\nMD5: схема Меркла — Дамгарда допускает атаку расширением на MAC вида MD5(K || M). В примере получатель принял изменённое сообщение.\nЛавинный эффект: средние значения SHA-1, SHA-256, SHA-512 и SHA-3 близки к 50%, что характеризует диффузию.\nKeccak: изучены впитывание, отжатие и пять преобразований раунда. Для варианта 28 состояние имеет 25 бит и не обеспечивает практической безопасности.\nPBKDF-1 и HMAC: из персонального пароля получен и сохранён 160-битный ключ. Программная проверка HMAC подтвердила совпадение кодов.\nDH: хэширование общего секрета даёт ключ длиной 256 бит. Для защиты от посредника требуется аутентификация сторон.')
with zipfile.ZipFile('lab4/Щеглов_3381_ЛР4.odp','w',zipfile.ZIP_DEFLATED) as out:
 for f in z.namelist():out.writestr(f,E.tostring(root,encoding='utf-8',xml_declaration=True) if f=='content.xml' else z.read(f))
print('slides',len(body))
