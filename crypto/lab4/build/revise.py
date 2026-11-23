import zipfile,xml.etree.ElementTree as E,io
from PIL import Image
p='lab4/Щеглов_3381_ЛР4.odp';src='/home/misha/Downloads/крипта4_УАА.odp'
ns={'office':'urn:oasis:names:tc:opendocument:xmlns:office:1.0','draw':'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0','text':'urn:oasis:names:tc:opendocument:xmlns:text:1.0','svg':'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0','xlink':'http://www.w3.org/1999/xlink'}
for k,v in ns.items():E.register_namespace(k,v)
def q(s):a,b=s.split(':');return '{'+ns[a]+'}'+b
z=zipfile.ZipFile(p); original=zipfile.ZipFile(src); root=E.fromstring(z.read('content.xml')); sr=E.fromstring(original.read('content.xml'));body=root.find('.//'+q('office:presentation'));source=sr.find('.//'+q('office:presentation'));old=list(body);first=source[0]
for para in first.iter(q('text:p')):
 for node in para.iter():
  if node.text:node.text=node.text.replace('Студентка группы 3381:', 'Студент группы 3381:').replace('Уфимцева Алиса Александровна','Щеглов Михаил Алексеевич')
body.remove(old[0]);body.insert(0,first)
# insert two additional slides per algorithm, covering the remaining ten screenshots
for idx in reversed(range(7,11)):
 slide=old[idx]; sourcepage=source[idx-1]; images=sourcepage.findall('.//'+q('draw:image'))[:11]
 for group in reversed(range(2)):
  import copy
  new=copy.deepcopy(slide)
  for child in list(new):new.remove(child)
  new.set(q('draw:name'),'Лавинный эффект: серия')
  for k,im in enumerate(images[1+group*5:1+(group+1)*5]):
   href=im.get(q('xlink:href')); a=Image.open(io.BytesIO(original.read(href))); x=0.6+(k%3)*9.1;y=1.6+(k//3)*6.8;w=8.7;h=6.2;scale=min(w/a.width,h/a.height);ww=a.width*scale;hh=a.height*scale
   f=E.SubElement(new,q('draw:frame'),{q('svg:x'):f'{x+(w-ww)/2}cm',q('svg:y'):f'{y+(h-hh)/2}cm',q('svg:width'):f'{ww}cm',q('svg:height'):f'{hh}cm'});E.SubElement(f,q('draw:image'),{q('xlink:href'):href,q('xlink:type'):'simple',q('xlink:show'):'embed',q('xlink:actuate'):'onLoad'})
  f=E.SubElement(new,q('draw:frame'),{q('draw:style-name'):'Plain',q('svg:x'):'1cm',q('svg:y'):'0.3cm',q('svg:width'):'26cm',q('svg:height'):'1cm'});box=E.SubElement(f,q('draw:text-box'));t=E.SubElement(box,q('text:p'),{q('text:style-name'):'Title'});t.text=['SHA-1','SHA-256','SHA-512','SHA-3'][idx-7]+' — изменения '+str(1+group*5)+'–'+str(5+group*5)
  body.insert(list(body).index(slide)+1,new)
with zipfile.ZipFile(p+'.tmp','w',zipfile.ZIP_DEFLATED) as out:
 for name in z.namelist():out.writestr(name,E.tostring(root,encoding='utf-8',xml_declaration=True) if name=='content.xml' else z.read(name))
import os
os.replace(p+'.tmp',p)
