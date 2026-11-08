// Простой генератор блок-схем (ГОСТ 19.701-90) из нативных фигур PowerPoint.
// Элементы:  ['term', t] ['io', t] ['proc', t]
//            ['loop', заголовок, [тело], текст_конца]      — граница цикла (начало/конец)
//            ['if', условие, [ветка «да» справа]]          — ветвление с возвратом
//            ['guard', условие, [ветка «нет» справа]]      — проверка с выходом по ошибке
// opts.split = [i, ...] — разбить схему на колонки перед элементами с этими индексами
// (индексы в «плоском» списке, где цикл развёрнут в loopS … loopE); колонки
// соединяются соединителями-окружностями А, Б, …

const FS = 10;                       // базовый кегль, pt
const W = 2.9, WB = 2.1, WT = 1.5;   // ширина: основная, ветки, терминатора
const G = 0.15;                      // вертикальный зазор
const CR = 0.32;                     // диаметр соединителя
const lineH = (fs) => fs * 1.22 / 72;
const charW = (fs) => fs * 0.62 / 72;

function nLines(text, widthIn, fs) {
  const per = Math.max(4, Math.floor(widthIn / charW(fs)));
  let lines = 0;
  for (const para of String(text).split('\n')) {
    let cur = 0, l = 1;
    for (const word of para.split(' ')) {
      const len = word.length + (cur ? 1 : 0);
      if (cur + len > per && cur > 0) { l++; cur = word.length; } else cur += len;
    }
    lines += l;
  }
  return lines;
}

function nodeSize(type, text, w) {
  if (type === 'term') return { w: WT, h: 0.3 };
  if (type === 'conn') return { w: CR, h: CR };
  const tw = { proc: w - 0.16, io: w * 0.74 - 0.1, loopS: w - 0.45, loopE: w - 0.45, dec: w * 0.56 }[type];
  const n = nLines(text, tw, FS);
  if (type === 'dec') return { w, h: Math.max(0.56, n * lineH(FS) * 2 + 0.12) };
  return { w, h: Math.max(0.3, n * lineH(FS) + 0.12) };
}

function flatten(items) {
  const out = [];
  for (const it of items) {
    if (it[0] === 'loop') out.push(['loopS', it[1]], ...flatten(it[2]), ['loopE', it[3]]);
    else if (it[0] === 'if' || it[0] === 'guard') out.push([it[0], it[1], flatten(it[2])]);
    else out.push(it);
  }
  return out;
}

function layoutSeq(items, ax, y0, w, P) {
  let exit = null;
  for (const it of items) {
    let top = y0;
    if (exit !== null) { top = exit + G; P.push({ k: 'line', x1: ax, y1: exit, x2: ax, y2: top, arrow: true }); }
    exit = layoutItem(it, ax, top, w, P);
  }
  return exit === null ? y0 : exit;
}

function node(P, type, text, ax, top, w) {
  const s = nodeSize(type, text, w);
  P.push({ k: 'node', type, text, x: ax - s.w / 2, y: top, w: s.w, h: s.h });
  return top + s.h;
}

function layoutItem(it, ax, top, w, P) {
  const [kind] = it;
  if (['term', 'io', 'proc', 'loopS', 'loopE', 'conn'].includes(kind)) return node(P, kind, it[1], ax, top, w);
  if (kind === 'if' || kind === 'guard') {
    const s = nodeSize('dec', it[1], w);
    const dBot = node(P, 'dec', it[1], ax, top, w);
    const cy = top + s.h / 2;
    const bx = ax + w / 2 + 0.25 + WB / 2;
    const bTop = cy + 0.25;
    P.push({ k: 'line', x1: ax + w / 2, y1: cy, x2: bx, y2: cy, arrow: false });
    P.push({ k: 'line', x1: bx, y1: cy, x2: bx, y2: bTop, arrow: true });
    const yes = kind === 'if' ? 'да' : 'нет', no = kind === 'if' ? 'нет' : 'да';
    P.push({ k: 'label', x: ax + w / 2 + 0.03, y: cy - 0.22, text: yes });
    P.push({ k: 'label', x: ax + 0.07, y: dBot - 0.02, text: no });
    const bExit = layoutSeq(it[2], bx, bTop, WB, P);
    if (kind === 'guard') {
      P.push({ k: 'line', x1: ax, y1: dBot, x2: ax, y2: dBot + 0.12, arrow: false });
      return dBot + 0.12;
    }
    const yj = Math.max(bExit + G, dBot + G + 0.05);
    P.push({ k: 'line', x1: bx, y1: bExit, x2: bx, y2: yj, arrow: false });
    P.push({ k: 'line', x1: bx, y1: yj, x2: ax, y2: yj, arrow: true });
    P.push({ k: 'line', x1: ax, y1: dBot, x2: ax, y2: yj, arrow: false });
    return yj;
  }
  throw new Error('unknown item ' + kind);
}

function bounds(P) {
  let minX = Infinity, maxX = -Infinity, maxY = 0;
  for (const p of P) {
    if (p.k === 'node') { minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x + p.w); maxY = Math.max(maxY, p.y + p.h); }
    if (p.k === 'line') { minX = Math.min(minX, p.x1, p.x2); maxX = Math.max(maxX, p.x1, p.x2); maxY = Math.max(maxY, p.y1, p.y2); }
  }
  return { minX, maxX, maxY };
}

// раскладка с колонками; возвращает все примитивы в общей системе координат
function layout(items, split = []) {
  const flat = flatten(items);
  const cuts = [0, ...split, flat.length];
  const letters = 'АБВГД';
  const all = [];
  let x = 0, maxY = 0;
  for (let c = 0; c < cuts.length - 1; c++) {
    let seg = flat.slice(cuts[c], cuts[c + 1]);
    if (c > 0) seg = [['conn', letters[c - 1]], ...seg];
    if (c < cuts.length - 2) seg = [...seg, ['conn', letters[c]]];
    const P = [];
    layoutSeq(seg, 0, 0, W, P);
    const b = bounds(P);
    const dx = x - b.minX;
    for (const p of P) {
      if (p.k === 'node' || p.k === 'label') p.x += dx;
      if (p.k === 'line') { p.x1 += dx; p.x2 += dx; }
      all.push(p);
    }
    x += b.maxX - b.minX + 0.6;
    maxY = Math.max(maxY, b.maxY);
  }
  const b = bounds(all);
  return { P: all, minX: b.minX, maxX: b.maxX, maxY };
}

// Нарисовать схему на слайде, вписав в прямоугольник box = {x, y, w, h}
function draw(pres, slide, items, box, opts = {}) {
  const L = layout(items, opts.split || []);
  const bw = L.maxX - L.minX, bh = L.maxY;
  const s = Math.min(opts.maxScale || 1.15, box.w / bw, box.h / bh);
  const ox = box.x + (box.w - bw * s) / 2 - L.minX * s;
  const oy = box.y;
  const X = (v) => ox + v * s, Y = (v) => oy + v * s;
  const fs = Math.max(7, +(FS * s).toFixed(1));
  const stroke = { color: '000000', width: 1 };
  const shapeOf = {
    term: pres.shapes.FLOWCHART_TERMINATOR, io: pres.shapes.FLOWCHART_DATA,
    proc: pres.shapes.RECTANGLE, dec: pres.shapes.FLOWCHART_DECISION, conn: pres.shapes.OVAL,
  };
  for (const p of L.P) {
    if (p.k === 'node') {
      const o = {
        x: X(p.x), y: Y(p.y), w: p.w * s, h: p.h * s, fill: { color: 'FFFFFF' }, line: { ...stroke },
        fontFace: 'Arial', fontSize: fs, color: '000000', align: 'center', valign: 'middle', margin: 0.06,
      };
      if (p.type === 'loopS' || p.type === 'loopE') {
        const w = p.w * s, h = p.h * s, c = Math.min(0.16, h * 0.45);
        o.shape = pres.shapes.CUSTOM_GEOMETRY;
        o.points = p.type === 'loopS'
          ? [{ x: c, y: 0 }, { x: w - c, y: 0 }, { x: w, y: c }, { x: w, y: h }, { x: 0, y: h }, { x: 0, y: c }, { close: true }]
          : [{ x: 0, y: 0 }, { x: w, y: 0 }, { x: w, y: h - c }, { x: w - c, y: h }, { x: c, y: h }, { x: 0, y: h - c }, { close: true }];
      } else o.shape = shapeOf[p.type];
      if (p.type === 'conn') o.margin = 0;
      slide.addText(p.text, o);
    } else if (p.k === 'line') {
      const x1 = X(p.x1), y1 = Y(p.y1), x2 = X(p.x2), y2 = Y(p.y2);
      const o = {
        x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
        line: { ...stroke, ...(p.arrow ? { endArrowType: 'triangle' } : {}) },
      };
      if (x2 < x1) o.flipH = true;
      if (y2 < y1) o.flipV = true;
      slide.addShape(pres.shapes.LINE, o);
    } else if (p.k === 'label') {
      slide.addText(p.text, {
        x: X(p.x), y: Y(p.y), w: 0.4 * s + 0.1, h: 0.22 * s, fontFace: 'Arial', fontSize: fs, color: '000000',
        margin: 0, align: 'left', valign: 'middle', isTextBox: true,
      });
    }
  }
  return { scale: s, fs, height: bh * s, width: bw * s };
}

module.exports = { draw, layout, flatten };
