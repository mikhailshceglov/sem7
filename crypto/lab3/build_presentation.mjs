import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const root='/home/misha/leti/sem7/crypto/lab3';
const skill='/home/misha/.codex/plugins/cache/openai-primary-runtime/presentations/26.1105.12137/skills/presentations';
const results=JSON.parse(await fs.readFile(path.join(root,'results.json'),'utf8'));
const out=path.join(root,'output');
const build=path.join(root,'.presentation-build');
await fs.mkdir(out,{recursive:true}); await fs.mkdir(build,{recursive:true});
const P=Presentation.create({slideSize:{width:1280,height:720}});
const C={ink:'#15202B',muted:'#536273',blue:'#215D88',cyan:'#DCEEF5',teal:'#087E83',light:'#F5F8FA',white:'#FFFFFF',orange:'#E39B3C',red:'#B95355',line:'#B8C9D3',green:'#23806F'};

function sh(slide,text,x,y,w,h,size=23,color=C.ink,bold=false,fill='none',align='left'){
  const s=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:'none',width:0}});
  s.text=text; s.text.style={fontFamily:'Arial',fontSize:size,color,bold,alignment:align,verticalAlignment:'middle',wrap:true};
  return s;
}
function box(slide,x,y,w,h,fill=C.light,stroke=C.line,r=14){
  return slide.shapes.add({geometry:'roundRect',position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:1.5},borderRadius:r});
}
function line(slide,x1,y1,x2,y2,color=C.line,width=2){
  return slide.shapes.add({geometry:'line',position:{left:x1,top:y1,width:x2-x1,height:y2-y1},fill:'none',line:{style:'solid',fill:color,width}});
}
function arrow(slide,x1,y1,x2,y2,color=C.blue){line(slide,x1,y1,x2,y2,color,3);sh(slide,'›',x2-12,y2-19,25,35,31,color,true,'none','center');}
function slide(title,section='Лабораторная работа № 3'){
  const s=P.slides.add();s.background.fill=C.white;
  sh(s,section.toUpperCase(),56,28,850,24,13,C.teal,true);
  sh(s,title,56,66,1168,74,36,C.ink,true);
  sh(s,String(P.slides.items.length).padStart(2,'0'),1172,666,52,30,16,C.muted,false,'none','right');
  return s;
}
function para(s,t,x,y,w,h,size=22,color=C.ink){return sh(s,t,x,y,w,h,size,color,false);}
function footer(s,t){sh(s,t,56,659,1080,28,13,C.muted);}
function note(s,t){s.speakerNotes.text=t;}
function card(s,num,title,body,x,y,w,h){box(s,x,y,w,h);sh(s,num,x+18,y+15,56,48,31,C.teal,true);sh(s,title,x+82,y+18,w-100,30,21,C.ink,true);sh(s,body,x+24,y+65,w-48,h-78,18,C.muted);}

// 1
{
 const s=P.slides.add();s.background.fill=C.ink;
 sh(s,'Криптография · лабораторная работа № 3',70,92,1010,46,22,'#84D0D3',true);
 sh(s,'AES, CBC и шифр\n«Кузнечик»',70,160,1060,190,54,C.white,true);
 sh(s,'Вариант 3 · Щеглов М.А. · 2026',70,505,900,45,23,C.white);
 sh(s,'Измерения, демонстрация атаки и программа преобразований',70,557,1030,50,19,'#B8CBD6');
 note(s,'Основание: задание пользователя, методическое пособие (с. 28, 30), файл «Задачи к заданию №3.pdf», вариант 3.');
}
// 2
{
 const s=slide('Объект и порядок исследования');
 card(s,'01','AES и CBC','Раундовые преобразования; атака перебором при частично известном ключе.',56,170,548,180);
 card(s,'02','Padding Oracle','Три фазы атаки на CBC с наблюдением ответа о корректности PKCS#7.',626,170,598,180);
 card(s,'03','«Кузнечик»','Стандартные X, S, L; учебное преобразование варианта 3.',56,374,548,180);
 card(s,'04','Расписание ключа','Расчёт C₃₀ из N = 28; сверка с эталоном статьи и RFC 7801.',626,374,598,180);
 footer(s,'Измеренные времена и модельные оценки разделены на диаграммах.');
 note(s,'Задание пользователя; методическое пособие: с. 28, 30; «Задачи к заданию №3.pdf», с. 3–4.');
}
// 3
{
 const s=slide('AES-128: раунд зашифрования');
 para(s,'Блок 128 бит · ключ 128 бит · 10 раундов · состояние 4 × 4 байта',58,145,1100,50,24);
 const xs=[80,315,550,785,1020], labels=['State','SubBytes','ShiftRows','MixColumns','AddRoundKey'];
 xs.forEach((x,i)=>{box(s,x,295,180,100,i===0?C.cyan:C.light);sh(s,labels[i],x+9,323,162,42,21,C.ink,true,'none','center');if(i<4)arrow(s,x+184,345,xs[i+1]-7,345);});
 sh(s,'Перед раундом: AddRoundKey с исходным ключом',80,445,500,50,22,C.blue,true);
 sh(s,'В 10-м раунде MixColumns отсутствует',675,445,505,50,22,C.blue,true);
 footer(s,'SubBytes — нелинейная замена; ShiftRows и MixColumns — рассеивание; AddRoundKey — XOR.');
 note(s,'NIST FIPS 197 (обновление 2023): https://csrc.nist.gov/pubs/fips/197/final');
}
// 4
{
 const s=slide('AES Visualization в CrypTool 2');
 const add=await fs.readFile(path.join(root,'aes_ct2_addroundkey.png'));
 const sub=await fs.readFile(path.join(root,'aes_ct2_subbytes.png'));
 s.images.add({blob:add.buffer.slice(add.byteOffset,add.byteOffset+add.byteLength),contentType:'image/png',alt:'CrypTool 2 AddRoundKey',fit:'contain',position:{left:56,top:190,width:564,height:341}});
 s.images.add({blob:sub.buffer.slice(sub.byteOffset,sub.byteOffset+sub.byteLength),contentType:'image/png',alt:'CrypTool 2 SubBytes',fit:'contain',position:{left:658,top:190,width:566,height:341}});
 sh(s,'AddRoundKey: побайтовый XOR',58,547,562,35,20,C.blue,true);
 sh(s,'SubBytes: замена по S-box',658,547,566,35,20,C.blue,true);
 footer(s,'Скриншоты взяты из предоставленного примера; это иллюстрация интерфейса, не новый запуск CT2.');
 note(s,'Источник изображений: предоставленный файл «крипта3.pdf», с. 12. Доступность шаблона подтверждена перечнем CrypTool: https://www.cryptool.org/en/functions/');
}
// 5
{
 const s=slide('AES-128-CBC: исходные данные опыта');
 card(s,'P','Открытый текст','1000 ASCII-символов английского текста. Энтропия считается для всего расшифрованного блока данных.',56,166,548,225);
 card(s,'K','Ключ','00112233445566778899AABBCCDDA73B; меняются последние 2 байта.',626,166,598,225);
 box(s,56,423,1168,139,C.cyan,C.cyan);
 sh(s,'CBC: Cᵢ = Eₖ(Pᵢ ⊕ Cᵢ₋₁), C₀ = IV',80,449,1090,48,28,C.ink,true);
 sh(s,'IV = 102030405060708090A0B0C0D0E0F000 · PKCS#7',80,507,1080,33,19,C.muted);
 footer(s,'Оценка кандидата: энтропия полного расшифрованного текста; правильный суффикс A73B найден.');
 note(s,'Данные и расчёт: lab3.py, results.json. Методическое пособие, с. 28, пункты 1–4. Оценка энтропией соответствует смыслу шаблона CT2, но измерения выполнены локальной программой, не CrypTool 2.');
}
// 6
{
 const s=slide('Время перебора и известные байты ключа');
 const b=results.benchmark;const t=b.estimated_one_core_seconds;
 const rows=[['14',t['2_unknown_bytes'],'2ⁱ⁶','измерено'],['12',t['4_unknown_bytes'],'2³²','оценка'],['10',t['6_unknown_bytes'],'2⁴⁸','оценка']];
 sh(s,'log₁₀(секунд), 1 ядро',65,151,470,35,20,C.muted);
 const x0=128,y0=572,w=990,h=345;
 [0,2,4,6,8,10].forEach(v=>{const y=y0-v/12*h;line(s,x0,y,x0+w,y,C.line,1);sh(s,String(v),75,y-16,45,28,14,C.muted,false,'none','right');});
 line(s,x0,y0,x0+w,y0,C.ink,2);
 rows.forEach((r,i)=>{
  const x=x0+170+i*350;const val=Math.log10(r[1]);const y=y0-val/12*h;
  box(s,x,y,170,y0-y,i===0?C.teal:C.blue,i===0?C.teal:C.blue,4);
  sh(s,`${r[0]} байт`,x-10,585,190,33,18,C.ink,true,'none','center');
  sh(s,r[3],x-10,617,190,25,15,i===0?C.teal:C.blue,false,'none','center');
  sh(s,i===0?'2,75 с':i===1?'≈ 50 ч':'≈ 374 года',x-16,y-43,200,35,19,C.ink,true,'none','center');
 });
 footer(s,'Оценки для 4 и 6 неизвестных байт = измеренное время × 2¹⁶ и × 2³². Полный перебор не запускался.');
 note(s,'Результаты локального эксперимента из results.json. Для 14 известных байт полный просмотр 2^16 кандидатов, медиана двух повторов; для 12 и 10 байт расчётная экстраполяция при той же скорости.');
}
// 7
{
 const s=slide('Время полного просмотра 2¹⁶ ключей');
 const b=results.benchmark.measurements;
 const max=3.0;const x0=160,y0=565;
 [0,1,2,3].forEach(v=>{const y=y0-v/max*350;line(s,x0,y,1140,y,C.line,1);sh(s,`${v} с`,78,y-12,65,26,15,C.muted,false,'none','right');});
 b.forEach((r,i)=>{const x=255+i*330,y=y0-r.median_seconds/max*350;box(s,x,y,190,y0-y,C.teal,C.teal,4);sh(s,`${r.median_seconds.toFixed(2)} с`,x,y-43,190,35,23,C.ink,true,'none','center');sh(s,`${r.cores} ${r.cores===1?'ядро':'ядра'}`,x-2,579,194,35,20,C.ink,true,'none','center');});
 footer(s,'Медиана двух запусков; конкретные времена зависят от CPU и загрузки системы.');
 note(s,'Данные results.json; 2 запуска на конфигурацию, полный просмотр всех 65536 суффиксов ключа; локальная программа Python, не CrypTool 2.');
}
// 8
{
 const s=slide('CBC и оракул дополнения');
 box(s,69,215,242,95,C.cyan);sh(s,'Cᵢ',96,238,185,45,33,C.ink,true,'none','center');
 box(s,374,215,242,95,C.light);sh(s,'Dₖ(Cᵢ)',391,236,209,48,29,C.ink,true,'none','center');
 box(s,682,215,242,95,C.cyan);sh(s,'⊕ Cᵢ₋₁',699,236,209,48,29,C.ink,true,'none','center');
 box(s,985,215,230,95,C.light);sh(s,'Pᵢ',1011,237,177,48,32,C.ink,true,'none','center');
 arrow(s,315,262,367,262);arrow(s,619,262,675,262);arrow(s,929,262,977,262);
 box(s,118,408,1028,131,'#FCEFE5','#E8C89C');
 sh(s,'Нарушитель меняет Cᵢ₋₁ → сервер проверяет PKCS#7 → ответ «да/нет» раскрывает байты Dₖ(Cᵢ).',151,435,961,85,23,C.ink,true);
 footer(s,'Pᵢ = Dₖ(Cᵢ) ⊕ Cᵢ₋₁. Уязвим ответ о проверке дополнения, а не сам AES.');
 note(s,'Методическое пособие, с. 29–30; CrypTool Padding Oracle template: https://www.cryptool.org/en/functions/ ; принцип атаки также разобран в https://www.cryptool.org/media/publications/theses/BA_Juettner_Padding-Oracle-Attack.pdf');
}
// 9
{
 const s=slide('Три фазы атаки на второй блок');
 const o=results.oracle;
 card(s,'1','Длина дополнения',`Изменение C₁ выявило один байт PKCS#7: 01. Запросов: ${o.phase_queries[0]}.`,56,174,362,254);
 card(s,'2','Подбор байта',`Подбор маски для последнего байта промежуточного состояния. Запросов: ${o.phase_queries[1]}.`,459,174,362,254);
 card(s,'3','Расшифрование',`Остальные 15 байт восстановлены справа налево. Запросов: ${o.phase_queries[2]}.`,862,174,362,254);
 box(s,56,461,1168,119,C.cyan,C.cyan);
 sh(s,'Результат: Shcheglov M.A.! | 01',78,482,1100,40,27,C.ink,true);
 sh(s,`Совпадение с исходным блоком · всего ${o.total_queries} запросов`,78,528,1100,34,20,C.teal,true);
 footer(s,'Имя «Щеглов М.А.» транслитерировано для размещения во втором 16-байтном блоке.');
 note(s,'Локальная демонстрация из lab3.py/results.json. Фазы соответствуют постановке методического пособия, с. 30; это не скриншоты трёх фаз CrypTool 2. Исходный второй блок 15 байт плюс 01 PKCS#7.');
}
// 10
{
 const s=slide('«Кузнечик»: раундовые преобразования');
 para(s,'Блок 128 бит · ключ 256 бит · 10 раундовых ключей',57,145,1120,42,24);
 const xs=[95,385,675,965], labels=['X','S','L','K'];const desc=['XOR с ключом','S-box для каждого байта','16 шагов R в GF(2⁸)','следующий раунд'];
 xs.forEach((x,i)=>{box(s,x,270,213,105,i%2?C.cyan:C.light);sh(s,labels[i],x+15,285,180,48,36,C.teal,true,'none','center');sh(s,desc[i],x-3,391,220,66,19,C.muted,false,'none','center');if(i<3)arrow(s,x+216,322,xs[i+1]-11,322);});
 sh(s,'Раунды 1–9: L(S(Xₖ(состояние)))',96,498,530,45,23,C.blue,true);
 sh(s,'Раунд 10: только Xₖ₁₀',676,498,480,45,23,C.blue,true);
 footer(s,'Учебная модель варианта 3 отличается от стандартного L-преобразования.');
 note(s,'RFC 7801 §§4.2–4.4: https://www.rfc-editor.org/rfc/rfc7801.html ; разбор и константы: https://habr.com/ru/articles/459004/');
}
// 11
{
 const s=slide('Вариант 3: учебный регистр с обратной связью');
 box(s,57,171,546,322,C.light);box(s,627,171,596,322,C.cyan,C.cyan);
 sh(s,'Учебное преобразование',82,195,480,42,25,C.ink,true);
 sh(s,'f = Σ(Lᵢ · Wᵢ mod 256) mod 256',82,258,487,54,23,C.teal,true);
 para(s,'Сдвиг влево на байт; f записывается справа. Повторить 16 раз.',82,330,480,104,21);
 sh(s,'Стандартный «Кузнечик»',652,195,535,42,25,C.ink,true);
 sh(s,'f = ⊕ GF(2⁸)(aᵢ · cᵢ)',652,258,535,54,23,C.blue,true);
 para(s,'Сдвиг и коэффициенты заданы RFC 7801. Здесь операции выполняются в поле, а не mod 256.',652,330,535,104,21);
 footer(s,'Сходство структуры не делает учебную функцию реализацией стандартного шифра.');
 note(s,'Формулировка варианта 3: «Задачи к заданию №3.pdf», с. 3–4. Стандарт: RFC 7801, §§4.2–4.3.');
}
// 12
{
 const s=slide('Блок-схема алгоритма варианта 3');
 const ys=[153,235,317,399,481,563], labels=['Ввести L₀, W; проверить 16 байт','i = 0','f = (Σ (Lⱼ·Wⱼ mod 256)) mod 256','L ← L[1:16] || f; i ← i + 1','Если i < 16 — повторить вычисление f','Вывести L₁₆'];
 ys.forEach((y,i)=>{box(s,214,y,852,57,i===5?C.cyan:C.light);sh(s,labels[i],238,y+11,804,36,i===2?20:21,C.ink,i===5,'none','center');if(i<5)arrow(s,640,y+58,640,ys[i+1]-4);});
 note(s,'Блок-схема соответствует точному условию варианта 3, «Задачи к заданию №3.pdf», с. 3–4.');
}
// 13
{
 const s=slide('Код учебного преобразования');
 box(s,57,161,1166,405,'#17222C','#17222C');
 const code=`def toy_step(state, weights):\n    if len(state) != 16 or len(weights) != 16:\n        raise ValueError("Нужны 16 байт")\n    feedback = sum((a * w) % 256\n                   for a, w in zip(state, weights)) % 256\n    return state[1:] + [feedback]\n\ndef toy_transform(state, weights):\n    for _ in range(16):\n        state = toy_step(state, weights)\n    return state`;
 sh(s,code,87,185,1100,356,23,'#E9F4F7',false);
 footer(s,'Полный исполняемый исходный код: lab3.py · Запуск: python3 lab3.py all');
 note(s,'Полный исходный код находится рядом с презентацией: lab3.py. Основная функция приведена на слайде.');
}
// 14
{
 const s=slide('Контрольный пример варианта 3');
 sh(s,'L₀',58,163,60,38,27,C.teal,true);
 sh(s,results.toy.input.join(', '),128,163,1050,67,22,C.ink);
 sh(s,'W',58,250,60,38,27,C.teal,true);
 sh(s,results.toy.weights.join(', '),128,250,1050,67,22,C.ink);
 box(s,56,349,1168,211,C.cyan,C.cyan);
 sh(s,'f₀ = Σ(L₀ᵢ · Wᵢ) mod 256 = 227',82,376,1100,42,25,C.ink,true);
 sh(s,'L₁ = '+results.toy.after_one.join(', '),82,432,1100,44,21,C.ink);
 sh(s,'L₁₆ = '+results.toy.after_sixteen.join(', '),82,488,1100,44,21,C.ink,true);
 footer(s,'Первый шаг совпал с контрольным примером задания: последний байт 227.');
 note(s,'Контрольный пример: «Задачи к заданию №3.pdf», с. 3–4. Расчёт: lab3.py, results.json.');
}
// 15
{
 const s=slide('Развёртывание ключа «Кузнечика»');
 card(s,'1','Исходный ключ','256 бит разбиваются на K₁ и K₂ по 128 бит.',56,171,360,205);
 card(s,'2','Константы','Cᵢ = L(00…00 || i), i = 1…32. В статье байты записаны в обратном порядке.',460,171,360,205);
 card(s,'3','Сеть Фейстеля','32 шага с X, S, L; после каждых 8 шагов — следующая пара ключей.',864,171,360,205);
 box(s,56,421,1168,143,C.cyan,C.cyan);
 sh(s,'N = 28  →  N + 2 = 30  →  C₃₀',82,446,1100,45,30,C.ink,true);
 sh(s,'Вычисление выполняет kuz_constant(30) в lab3.py',82,505,1080,31,21,C.muted);
 footer(s,'Константа C₃₀ — материал для шага расписания, не самостоятельный раундовый ключ.');
 note(s,'RFC 7801 §4.4: https://www.rfc-editor.org/rfc/rfc7801.html ; статья: https://habr.com/ru/articles/459004/');
}
// 16
{
 const s=slide('Константа C₃₀: расчёт и эталон');
 const c=results.constant;
 sh(s,'RFC 7801, порядок байт',57,163,700,39,21,C.muted);
 box(s,56,205,1168,84,C.light);sh(s,c.rfc_hex.toUpperCase(),79,226,1120,42,25,C.ink,true);
 sh(s,'Статья на Хабре, обратный порядок байт',57,325,900,39,21,C.muted);
 box(s,56,369,1168,84,C.cyan,C.cyan);sh(s,c.habr_byte_order_hex.toUpperCase(),79,389,1120,43,25,C.ink,true);
 sh(s,'Эталон C₃₀ в статье: 1E80A3E223281C394E257C42D5ADA17E',58,495,1160,63,22,C.teal,true);
 footer(s,'Байты после разворота полностью совпадают; C₁ также проверена по RFC 7801.');
 note(s,'Эталон C30 прямо приведён в https://habr.com/ru/articles/459004/ ; RFC 7801 C1 и направление байт: https://www.rfc-editor.org/rfc/rfc7801.html . Вычисление: lab3.py/results.json.');
}
// 17
{
 const s=slide('Код вычисления константы C₃₀');
 box(s,57,161,1166,409,'#17222C','#17222C');
 const code=`KUZ_COEFF = [148,32,133,16,194,192,1,251,\n             1,192,194,16,133,32,148,1]\n\ndef kuz_constant(i):\n    state = bytes(15) + bytes([i])\n    for _ in range(16):\n        feedback = 0\n        for a, c in zip(state, KUZ_COEFF):\n            feedback ^= gf_mul(a, c)\n        state = bytes([feedback]) + state[:15]\n    return state\n\nprint(kuz_constant(30).hex())`;
 sh(s,code,87,185,1100,360,22,'#E9F4F7');
 footer(s,'gf_mul реализует GF(2⁸) по x⁸ + x⁷ + x⁶ + x + 1; полная реализация — lab3.py.');
 note(s,'Код из lab3.py. Коэффициенты и преобразование R — RFC 7801 §§4.2–4.3: https://www.rfc-editor.org/rfc/rfc7801.html');
}
// 18
{
 const s=slide('Выводы и воспроизводимость');
 card(s,'✓','AES-CBC','Полный перебор 2¹⁶ кандидатов нашёл суффикс A73B. Время снизилось с 2,75 до 0,84 с при 1→4 ядрах.',56,170,548,168);
 card(s,'✓','Padding Oracle','Второй блок восстановлен без ключа через ответы о дополнении: 2111 запросов.',626,170,598,168);
 card(s,'✓','Вариант 3','Регистр реализован по условию; контрольный f₀ = 227, получен L₁₆.',56,360,548,168);
 card(s,'✓','Ключевое расписание','C₃₀ = 1E80…A17E в порядке статьи; совпадение с эталоном.',626,360,598,168);
 footer(s,'Исходный код и численные результаты: lab3.py, results.json. Скриншоты CT2 взяты из примера.');
 note(s,'Источники: NIST FIPS 197 https://csrc.nist.gov/pubs/fips/197/final ; RFC 7801 https://www.rfc-editor.org/rfc/rfc7801.html ; CrypTool https://www.cryptool.org/en/functions/ ; статья https://habr.com/ru/articles/459004/ ; локальные методические PDF и результаты программы.');
}

for(let i=0;i<P.slides.items.length;i++){
 const png=await P.export({slide:P.slides.items[i],format:'png',scale:0.6});
 await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const candidate=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(P)).save(candidate);
const final=path.join(out,'Лабораторная_работа_3_Щеглов_вариант_3_готово.pptx');
const res=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,
 pythonExecutable:'/home/misha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(build,'validation-ready.json')});
console.log(JSON.stringify({slides:P.slides.items.length,final,result:res},null,2));
