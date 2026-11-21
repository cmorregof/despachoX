from pptx import Presentation
from pptx.util import Emu, Inches
from pptx.text.text import _Paragraph
from PIL import Image
import copy, sys
from lxml import etree
SRC='/home/claude/kit/pptx/plantilla.pptx'
R='/home/claude/despachox/'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
p=Presentation(SRC)
S={i+1:s for i,s in enumerate(p.slides)}
def sh(slide,sid):
    for x in slide.shapes:
        if x.shape_id==sid: return x
    raise KeyError(sid)
def settext(shape, texts):
    if isinstance(texts,str): texts=[texts]
    para=shape.text_frame.paragraphs[0]
    for i,r in enumerate(para.runs): r.text=texts[i] if i<len(texts) else ''
    for extra in shape.text_frame.paragraphs[1:]: extra._p.getparent().remove(extra._p)
def setbody(shape, lines):
    p0=shape.text_frame.paragraphs[0]._p
    end=p0.find('{%s}endParaRPr'%A)
    def fill(pel,text):
        e=pel.find('{%s}endParaRPr'%A)
        r=etree.SubElement(pel,'{%s}r'%A); rpr=copy.deepcopy(e); rpr.tag='{%s}rPr'%A; rpr.set('lang','es-CO')
        r.append(rpr); t=etree.SubElement(r,'{%s}t'%A); t.text=text
        pel.remove(e); pel.append(e)
    tmpl=copy.deepcopy(p0); prev=p0; fill(p0,lines[0])
    for l in lines[1:]:
        n=copy.deepcopy(tmpl); prev.addnext(n); fill(n,l); prev=n
    for pel in shape.text_frame._txBody.findall('{%s}p'%A):
        ppr=pel.find('{%s}pPr'%A); sa=etree.SubElement(ppr,'{%s}spcAft'%A); etree.SubElement(sa,'{%s}spcPts'%A).set('val','900')
        ppr.remove(sa); ppr.insert(1 if ppr.find('{%s}lnSpc'%A) is not None else 0, sa)
def notes(slide,t): slide.notes_slide.notes_text_frame.text=t

s=S[1]
settext(sh(s,7),'SEMIFINAL – HACKATHON UNAL 2026 · EQUIPO 19')
settext(sh(s,8),'Convite')
settext(sh(s,9),'Que la comida llegue aunque la vía se cierre. Mesa de despacho de ayuda alimentaria para Manizales.')
notes(s,'Portada. Equipo 19: Samuel Rosso (líder), Carlos Orrego, Jacobo Vasco, Nicolás Ramírez y José Manuel Aristizábal.')

s=S[3]
settext(sh(s,3),'Seis días después del sismo, los bancos de alimentos tenían 404 toneladas en acopio y habían entregado 41.')
settext(sh(s,4),['Fuente: Portafolio, 16 de agosto de 2026 ','· cifras de los Bancos de Alimentos'])
notes(s,'Después del sismo, la comida llegó a Manizales. Lo que se atascó fue despacharla. Seis días después, los bancos de alimentos tenían 404 toneladas en acopio y habían entregado 41. Piensen en quien despacha ese día. Tiene un teléfono que no para de sonar y unas vías que se cierran sin avisar. Repartir veinte pedidos lo hace cualquiera con oficio. La ayuda hace falta cuando llegan miles.\n\nCifras exactas: 404.587 kg en acopio, 157.164 kg en tránsito y 41.163 kg entregados. Son de los Bancos de Alimentos, no solo de Manizales. «Seis días después» es cálculo nuestro con la fecha de la nota.')

s=S[7]
settext(sh(s,6),'Convite, la mesa de despacho')
settext(sh(s,7),'El sistema lee cada mensaje y calcula las rutas. Decide una persona.')
im=Image.open(R+'recursos/marca/hero_convite_caseta.jpg'); w,h=im.size; nh=int(w*9/16); top=(h-nh)//2
im.crop((0,top,w,top+nh)).save('caseta169.jpg',quality=90)
pic=s.shapes.add_picture('caseta169.jpg',0,0,p.slide_width,p.slide_height)
pic.name='Ilustración: vecinos reunidos en una caseta de un barrio de ladera'
sh(s,2)._element.addnext(pic._element)
notes(s,'Convite es la mesa de despacho para ese día. Los barrios y las veredas piden por chat o por SMS, con sus palabras. El sistema lee cada mensaje y calcula las rutas. La decisión la toma una persona.\n\nIlustración generada con IA.')

s=S[6]
settext(sh(s,2),'UN DÍA EN LA MESA'); settext(sh(s,3),'Cuando llegan miles de pedidos')
settext(sh(s,5),'15.000'); settext(sh(s,6),'mensajes a la vez en una prueba de carga. Ninguno perdido')
settext(sh(s,8),'6 h'); settext(sh(s,9),'de silencio en un punto crítico, y la mesa avisa para verificar')
settext(sh(s,11),'< 10 s'); settext(sh(s,12),'para recalcular las rutas cuando el despachador confirma un cierre')
from pptx.util import Pt
for i in (6,9,12):
    x=sh(s,i); x.width=Inches(3.3); x.height=Inches(1.4); x.top=Inches(3.65)
    for r in x.text_frame.paragraphs[0].runs: r.font.size=Pt(17)
    pp=x.text_frame.paragraphs[0]._p.find('{%s}pPr'%A)
    if pp is not None:
        for ls in pp.findall('{%s}lnSpc'%A): pp.remove(ls)
notes(s,'Les contamos tres momentos de ese día. El primero es la avalancha. En una prueba de carga le mandamos 15.000 mensajes a la vez. No se perdió ninguno, y todos quedaron en cola, en su orden. El segundo es el barrio que no escribe. Después de un desastre, puede ser el que se quedó sin señal. Si un punto crítico lleva seis horas sin pedir, Convite le avisa al despachador para que mande a alguien a verificar. Así el que no puede escribir tampoco se queda por fuera. El tercero es la vía. Un conductor escribe que hay un derrumbe. Convite no cierra la vía por un mensaje, porque puede ser un error o un rumor. La deja reportada hasta que el despachador la confirma. Cuando la confirma, el plan se recalcula en menos de diez segundos, y el pedido que iba en camión pasa a un campero, que sí entra.\n\nLa prueba de 15.000 fue en local, con un modelo simulado de 1,8 s, sin Telegram ni Railway (entrada/ESCALA.md).')

s=S[5]
settext(sh(s,2),'EVIDENCIA EN SIMULACIÓN'); settext(sh(s,3),'Pedidos críticos que llegan a tiempo')
settext(sh(s,5),'BASE'); settext(sh(s,6),'40,5 %'); settext(sh(s,7),'Despacho por orden de llegada')
settext(sh(s,9),'CONVITE'); settext(sh(s,10),'98,4 %')
for i in (6,10):
    x=sh(s,i); x.height=Inches(1.0)
    for r in x.text_frame.paragraphs[0].runs: r.font.size=Pt(54)
    pp=x.text_frame.paragraphs[0]._p.find('{%s}pPr'%A)
    if pp is not None:
        for ls in pp.findall('{%s}lnSpc'%A): pp.remove(ls)
for i in (7,11):
    x=sh(s,i); x.top=Inches(4.45); x.height=Inches(1.2)
    for r in x.text_frame.paragraphs[0].runs: r.font.size=Pt(16)
settext(sh(s,11),'Carga alta, 30 jornadas por política. Diferencia de 57,9 puntos, con intervalo del 95 % de 52,7 a 63,1')
notes(s,'¿Y sirve? Lo medimos en simulación, con 30 jornadas por política y carga alta. Si se despacha por orden de llegada, el 40,5 % de los pedidos críticos llega a tiempo. Con Convite llega el 98,4 %.\n\nFuente: despacho/sim/resultados_velocidades/tablas.md y docs/SIMULACION.md, sección 9. Frente a un despachador con oficio, la ventaja en críticos con carga alta es de 2,8 a 6,5 puntos, según la velocidad que se suponga en las vías.')

s=S[4]
settext(sh(s,2),'PILOTO DE 90 DÍAS'); settext(sh(s,3),'Se queda en Manizales')
b=sh(s,4); b.height=Inches(3.6)
setbody(b,['En la rutina del Banco Arquidiocesano de Alimentos, con la Unidad de Gestión del Riesgo.',
           'Empieza en Ciudadela del Norte y El Manantial.',
           'Cada 30 días suma una zona, si la anterior cumplió.',
           'Pedimos un despachador del Banco y 30 días trabajando a su lado.'])
box=sh(s,6); fig=R+'figuras_pitch/png/'+(sys.argv[1] if len(sys.argv)>1 else 'a_territorios_piloto')+'.png'
_im=Image.open(fig).convert('RGB'); _im=_im.crop((0,0,int(_im.size[0]*0.56),_im.size[1])); _im.save('mapa_piloto.jpg',quality=92); fig='mapa_piloto.jpg'
iw,ih=_im.size; H=box.height-Inches(0.3); W=int(H*iw/ih)
pc=s.shapes.add_picture(fig, box.left+(box.width-W)//2, box.top+Inches(0.15), W, H)
pc.name='Mapa del piloto: empieza en Ciudadela del Norte y El Manantial'
box._element.addnext(pc._element)
notes(s,'Esto se queda en Manizales. El piloto dura 90 días en la rutina del Banco Arquidiocesano de Alimentos, con la Unidad de Gestión del Riesgo. Empieza en Ciudadela del Norte y El Manantial, y cada 30 días suma una zona si la anterior cumplió. Para empezar necesitamos un despachador del Banco y 30 días trabajando a su lado.\n\nDía 30: La Macarena y El Tablazo. Día 60: Atardeceres y Kilómetro 41. Cada zona entra solo si la anterior cumplió y el Banco lo confirma (docs/PLAN_30_90.md).')

s=S[9]
settext(sh(s,5),'CONVITE · EQUIPO 19')
settext(sh(s,7),'En el Eje Cafetero, el convite era la forma en que los vecinos se juntaban para abrir un camino.')
settext(sh(s,8),'conviteman.up.railway.app'); settext(sh(s,9),'t.me/despachox_bot')
notes(s,'Somos Convite. En el Eje Cafetero, el convite era la forma en que los vecinos se juntaban para abrir un camino.\n\nTablero: conviteman.up.railway.app (pide clave). Bot de prueba: t.me/despachox_bot. Código: github.com/cmorregof/despachoX.')

s=S[2]
for x in s.shapes:
    if x.has_text_frame and 'rea Libre' in x.text_frame.text:
        settext(x,'Aquí va el video')
        from pptx.util import Pt as _Pt
        for r in x.text_frame.paragraphs[0].runs: r.font.size=_Pt(40)
notes(s,'Diapositiva para el video sin audio. En PowerPoint: Insertar > Video > Este dispositivo, y ajustarlo al recuadro. En Reproducción: iniciar automáticamente, repetir hasta su interrupción y sin sonido. Después se borra el texto del recuadro. Mientras corre, se dice el bloque «Un día en la mesa». Antes de grabar: reiniciar la base, entrar al tablero para que la clave no salga y no abrir la pestaña Informe.')
# orden y borrado
lst=p.slides._sldIdLst; ids=list(lst)
order=[1,3,7,2,6,5,4,9]
for el in ids: lst.remove(el)
for n in order: lst.append(ids[n-1])
for n in (8,10):
    p.part.drop_rel(ids[n-1].rId)
p.save('Convite_pitch_semifinal.pptx')
