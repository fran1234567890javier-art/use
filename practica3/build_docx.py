# -*- coding: utf-8 -*-
"""Genera Practica3_Tesauros_completa.docx con OOXML puro (sin dependencias)."""
import zipfile, os
from xml.sax.saxutils import escape

BLUE = "2F5496"
RED = "C00000"

def run(text, b=False, i=False, color=None, size=None, hl=False):
    rpr = ""
    if b: rpr += "<w:b/>"
    if i: rpr += "<w:i/>"
    if color: rpr += f'<w:color w:val="{color}"/>'
    if size: rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    if hl: rpr += '<w:highlight w:val="yellow"/>'
    parts = text.split("\n")
    out = ""
    for k, p in enumerate(parts):
        if k: out += "<w:br/>"
        out += f'<w:t xml:space="preserve">{escape(p)}</w:t>'
    return f"<w:r><w:rPr>{rpr}</w:rPr>{out}</w:r>"

def R(x):
    """x: str or list of (text, opts) tuples -> runs"""
    if isinstance(x, str):
        return run(x)
    s = ""
    for item in x:
        if isinstance(item, str):
            s += run(item)
        else:
            s += run(item[0], **item[1])
    return s

def P(x="", style=None, align=None, ind=0, after=None, before=None, keep=False, num=None, pagebreak=False):
    ppr = ""
    if style: ppr += f'<w:pStyle w:val="{style}"/>'
    if keep: ppr += "<w:keepNext/>"
    if num is not None: ppr += f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num}"/></w:numPr>'
    if before is not None or after is not None:
        ppr += f'<w:spacing w:before="{before or 0}" w:after="{after if after is not None else 120}"/>'
    if ind: ppr += f'<w:ind w:left="{ind}"/>'
    if align: ppr += f'<w:jc w:val="{align}"/>'
    br = '<w:r><w:br w:type="page"/></w:r>' if pagebreak else ""
    return f"<w:p><w:pPr>{ppr}</w:pPr>{br}{R(x)}</w:p>"

def PB():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

def cell(content, w, shade=None, bold_all=False):
    tcpr = f'<w:tcW w:w="{w}" w:type="dxa"/>'
    if shade: tcpr += f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>'
    paras = ""
    items = content if isinstance(content, list) and content and isinstance(content[0], list) else [content]
    for it in items:
        if bold_all and isinstance(it, str):
            it = [(it, {"b": True})]
        paras += f'<w:p><w:pPr><w:spacing w:before="20" w:after="20"/></w:pPr>{R(it)}</w:p>'
    return f"<w:tc><w:tcPr>{tcpr}</w:tcPr>{paras}</w:tc>"

def table(rows, widths, header=True, align="center"):
    b = ''.join(f'<w:{s} w:val="single" w:sz="6" w:space="0" w:color="000000"/>' for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    out = f'<w:tbl><w:tblPr><w:tblW w:w="{sum(widths)}" w:type="dxa"/><w:jc w:val="{align}"/><w:tblBorders>{b}</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>{grid}</w:tblGrid>'
    for r_i, row in enumerate(rows):
        trpr = "<w:trPr><w:cantSplit/>" + ("<w:tblHeader/>" if header and r_i == 0 else "") + "</w:trPr>"
        out += f"<w:tr>{trpr}"
        for c_i, c in enumerate(row):
            hdr = header and r_i == 0
            out += cell(c, widths[c_i], shade="E7E6E6" if hdr else None, bold_all=hdr)
        out += "</w:tr>"
    return out + "</w:tbl>" + P("", after=60)

def box(paragraphs, shade=None):
    """Recuadro de respuesta: tabla de una celda."""
    w = 9070
    b = ''.join(f'<w:{s} w:val="single" w:sz="6" w:space="0" w:color="000000"/>' for s in ("top", "left", "bottom", "right"))
    sh = f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>' if shade else ""
    inner = "".join(f'<w:p><w:pPr><w:spacing w:before="40" w:after="80"/><w:jc w:val="both"/></w:pPr>{R(p)}</w:p>' for p in paragraphs)
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{w}" w:type="dxa"/><w:tblBorders>{b}</w:tblBorders><w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:bottom w:w="60" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            f'<w:tblGrid><w:gridCol w:w="{w}"/></w:tblGrid><w:tr><w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{sh}</w:tcPr>{inner}</w:tc></w:tr></w:tbl>' + P("", after=60))

def tree(lines):
    """lines: list of (nivel, texto)"""
    w = 9070
    b = ''.join(f'<w:{s} w:val="single" w:sz="6" w:space="0" w:color="000000"/>' for s in ("top", "left", "bottom", "right"))
    inner = "".join(f'<w:p><w:pPr><w:spacing w:before="0" w:after="20"/><w:ind w:left="{120 + lvl*567}"/></w:pPr>{run(t)}</w:p>' for lvl, t in lines)
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{w}" w:type="dxa"/><w:tblBorders>{b}</w:tblBorders><w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            f'<w:tblGrid><w:gridCol w:w="{w}"/></w:tblGrid><w:tr><w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/></w:tcPr>{inner}</w:tc></w:tr></w:tbl>' + P("", after=60))

B = lambda t: (t, {"b": True})
I = lambda t: (t, {"i": True})
HL = lambda t: (t, {"hl": True, "b": True})

body = []
add = body.append

# ---------------- Portada
for _ in range(6): add(P(""))
add(P([("Práctica 3", {"b": True, "color": RED, "size": 44})], align="center", after=1200))
add(P([("PRÁCTICA 3: Los tesauros: de usarlos a construirlos", {"b": True, "size": 48})], align="center", after=1200))
add(P("Nombre de los componentes del grupo: Jaime, Marta, Anais y Lerybel", align="center"))
add(PB())

# ---------------- Índice
add(P([("Contenido", {"color": BLUE, "size": 32})], after=200))
toc = [("1. Objetivos", 0), ("2. Relación del equipo", 0), ("3. Metodología", 0),
       ("3.1. Conceptos previos: ¿qué es un tesauro?", 1), ("4. Resultados", 0),
       ("4.1. Parte I. Usar un tesauro real (30 min)", 1),
       ("4.2. Parte II. Construir un minitesauro sobre alimentación (45 min)", 1)]
for t, lvl in toc:
    add(P(t, ind=lvl * 284, after=80))
add(PB())

# ---------------- 1. Objetivos
add(P("1. Objetivos", style="Heading1"))
add(P(["Entrar en contacto con uno de los instrumentos principales que se usan para ", B("indizar"),
       " los documentos (describir de qué tratan) y para ", B("recuperar"),
       " información en catálogos y bases de datos: el ", B("tesauro"), "."], align="both"))
add(P(["La práctica tiene ", B("dos partes"), " que siguen un orden lógico: en la ", B("Parte I"),
       " usaréis un tesauro real para entender cómo está construido y para qué sirve; en la ", B("Parte II"),
       " construiréis vosotros un pequeño tesauro aplicando lo que habéis observado."], align="both"))

# ---------------- 2. Equipo
add(P("2. Relación del equipo", style="Heading1"))
add(P(["El grupo se compondrá de un ", B("máximo de cuatro personas"), ". A cada una se le asigna un rol con una tarea específica:"], align="both"))
add(table([
    ["Nombre y apellidos", "Rol", "Tarea"],
    ["Jaime", "Coordinación", "Controla el tiempo y revisa que todo sea coherente al final"],
    ["Marta", "Secretaría", "Escribe las respuestas en este documento"],
    ["Anais", "Búsqueda", "Maneja el tesauro en línea y hace las capturas"],
    ["Lerybel", "Revisión", "Comprueba los símbolos (USE, UP, TG, TE, TR) y la ortografía"],
], [2700, 1900, 4470]))
add(P([("Si sois tres personas, una de ellas asume dos roles. Si sois más personas, dos personas asumirán un mismo rol.", {"i": True, "color": RED})]))

# ---------------- 3. Metodología
add(P("3. Metodología", style="Heading1"))
add(P(["Acceder a un tesauro en línea para conocer su ", B("estructura"), " y las ", B("relaciones semánticas"),
       " entre sus términos, y usarlo para ", B("buscar y recuperar documentos"), ". Después, ",
       B("elaborar un minitesauro"), " sobre alimentación con sus presentaciones jerárquica y alfabética. Las tareas se reparten de la siguiente manera:"], align="both"))
add(table([
    ["Momento", "Qué haréis"],
    [[B("3.1. Conceptos previos")], "Leer qué es un tesauro y cómo se relacionan sus términos"],
    [[B("4.1. Parte I")], "Navegar por el tesauro del Observatorio de la Infancia y buscar documentos con él"],
    [[B("4.2. Parte II")], "Elaborar un minitesauro: agrupar, jerarquizar y ordenar alfabéticamente"],
], [1900, 6200]))

add(P("3.1. Conceptos previos: ¿qué es un tesauro?", style="Heading2"))
add(P(["Un ", B("tesauro"), " es un ", B("vocabulario controlado"),
       ": una lista de términos acordados en la que cada concepto se expresa siempre con el mismo término y en la que se indican las ",
       B("relaciones"), " entre los términos. Lo regula la norma internacional ", B("ISO 25964"), "."], align="both"))
add(P([B("Se usa en dos momentos:")], keep=True))
add(P([B("Al describir los documentos (indización). "), "Quien procesa un documento le asigna términos del tesauro que indican de qué trata. Esos términos pasan a formar parte de sus ",
       B("metadatos"), " (en el campo «Descriptores» o «Materias»)."], num=1, align="both"))
add(P([B("Al buscar información (recuperación). "), "Quien busca usa ", B("el mismo tesauro"),
       " para navegar y elegir los términos con los que localizar los documentos. Como se describieron con esos mismos términos, los encuentra."], num=1, align="both"))
add(P([("Por ejemplo: sin tesauro, un documento descrito como «niños» no aparecería al buscar «infancia». Con el tesauro, ambos se unen en un solo término y no se pierde nada.", {"color": RED})], align="both"))
add(P([B("Se presenta de dos formas:")], keep=True))
add(P([B("Presentación jerárquica (o sistemática): "), "los términos se agrupan en categorías y se ordenan de lo general a lo específico, como un árbol. Facilita ", B("navegar"), " por el tesauro y descubrir términos."], num=2, align="both"))
add(P([B("Presentación alfabética: "), "los términos se ordenan de la A a la Z, cada uno con todas sus relaciones. Facilita ", B("localizar"), " un término determinado."], num=2, align="both"))
add(P([B("Términos y relaciones. "), "Un tesauro tiene ", B("descriptores"), " (términos autorizados o preferentes, los que se usan para indizar) y ",
       B("no descriptores"), " (sinónimos que no se usan, pero que remiten al descriptor). Entre ellos se establecen tres tipos de relaciones semánticas, cada una con sus símbolos:"], align="both"))
add(table([
    ["Relación", "Símbolos", "Qué significa", "Ejemplo"],
    [[B("Sinonimia (equivalencia)")], ["USE", "UP"] and [["USE"], ["UP"]],
     [[B("USE"), " («use»): va en el ", B("no descriptor"), " y remite al descriptor que hay que usar."],
      [B("UP"), " («usado por»): va en el ", B("descriptor"), " e indica los no descriptores que representa."]],
     [["Boquerón USE Anchoa"], ["Anchoa UP Boquerón"]]],
    [[B("Jerarquía")], [["TG"], ["TE"]],
     [[B("TG"), " (término genérico): indica el término ", B("más general"), " del que depende."],
      [B("TE"), " (término específico): indica los términos ", B("más concretos"), " que dependen de él."],
      ["Si A es TG de B, entonces B es TE de A."]],
     [["Anchoa TG Pescado"], ["Pescado TE Anchoa"]]],
    [[B("Asociación")], "TR",
     [[B("TR"), " (término relacionado): une términos que no son sinónimos ni dependen uno del otro, pero que conviene tener en cuenta juntos: causa y efecto, instrumento, materia prima, etc."]],
     "Tarta de queso TR Queso"],
], [1500, 1000, 4300, 2270]))

# ---------------- 4. Resultados
add(PB())
add(P("4. Resultados", style="Heading1"))
add(P("4.1. Parte I. Usar un tesauro real (30 min)", style="Heading2"))
add(P(["Vais a trabajar con el ", B("Tesauro del Observatorio de la Infancia y Adolescencia de Andalucía (OIA-A)"),
       ", que se usa para describir y buscar los documentos de su biblioteca virtual."], align="both"))
add(P([B("Ejercicio 1. Descubrir las relaciones en el tesauro (15 min)")], keep=True))
add(P("Accede a la presentación alfabética del tesauro en la siguiente dirección: https://www.observatoriodelainfancia.es/oia/esp/tesauro_alfabetico.aspx", align="both"))
add(P(["Busca ", B("dos ejemplos"), " de cada relación y cópialos en la tabla. En la última columna, explicad ", B("con vuestras palabras"), " por qué creéis que esos términos están relacionados así."], align="both"))
add(table([
    ["Relación que buscáis", "Ejemplo 1 (término y su relación)", "Ejemplo 2", "¿Por qué están relacionados así?"],
    [["Sinonimia: un término con ", B("USE")], "Escuela secundaria USE Enseñanza secundaria", "Empleo amenazado USE Seguridad en el empleo",
     "Son dos formas de nombrar el mismo concepto. El tesauro elige una como descriptor y, desde la otra, remite a ella para que todos los documentos se describan con el mismo término."],
    [["Sinonimia: un término con ", B("UP")], "Enseñanza secundaria UP Escuela secundaria", "Seguridad en el empleo UP Empleo amenazado",
     "Es la relación inversa de USE: el descriptor indica qué sinónimos no aceptados representa, para que quien busque por ellos llegue también a él."],
    [["Jerarquía: un término con ", B("TG")], "Edad 00-03 TG Desarrollo evolutivo", "Edad 07-12 TG Desarrollo evolutivo",
     "Cada tramo de edad es una etapa concreta dentro de un concepto más amplio, el desarrollo evolutivo."],
    [["Jerarquía: un término con ", B("TE")], "Desarrollo evolutivo TE Edad 00-03", "Deficiencia sensorial TE Deficiencia visual",
     "El término más amplio agrupa a otros más concretos: la deficiencia visual es un tipo de deficiencia sensorial, igual que la edad 00-03 es una etapa del desarrollo evolutivo."],
    [["Asociación: un término con ", B("TR")], "Enfermedades TR Medicina", "Deficiencia visual TR Ceguera",
     "No son sinónimos ni uno es un tipo del otro, pero conviene tenerlos en cuenta juntos: la medicina estudia y trata las enfermedades, y la ceguera es el grado más grave de la deficiencia visual. Quien busca uno puede necesitar también el otro."],
    [["Un término que tenga ", B("a la vez"), " USE o UP, TG, TE y TR"],
     [[B("Deficiencia sensorial")], ["UP Discapacidad sensorial"], ["TG Deficiencia, discapacidad, minusvalía, necesidades especiales"], ["TE Deficiencia auditiva"], ["TE Deficiencia visual"], ["TR Atención temprana"]],
     [[B("Seguridad en el empleo")], ["UP Empleo amenazado"], ["TG Empleo"], ["TE Estabilidad laboral"], ["TR Desempleo"]],
     "Son términos situados en el centro de la estructura: tienen sinónimos que remiten a ellos (UP), un término más general por encima (TG), otros más concretos por debajo (TE) y términos asociados (TR). Por eso enlazan con muchas partes del tesauro."],
], [1650, 2350, 2350, 2720]))

add(P([B("Ejercicio 2. Usar el tesauro para encontrar documentos")], keep=True, before=120))
add(P(["Ahora vais a comprobar para qué sirve todo lo anterior: ", B("encontrar documentos"), ". Imaginad que tenéis que hacer un trabajo sobre la ", B("deficiencia visual"), "."], align="both"))
steps = [
    ["Accede al Observatorio de la Infancia y Adolescencia de Andalucía: https://www.observatoriodelainfancia.es/oia/esp/index.aspx"],
    ["Pulsa en ", B("«Biblioteca virtual»"), " y después en ", B("«Documentos»"), ". Leerás que «la sección de Documentación también puede consultarse navegando a través del Tesauro del OIA-A, tanto en su versión alfabética como jerárquica»."],
    ["Pulsa el botón «Buscar en Tesauro» para entrar en el tesauro."],
    ["Abre el ", B("índice jerárquico"), ". Revisa los grandes campos temáticos y decide en cuál podría estar el término ", B("«deficiencia visual»"), ". Ve bajando por la jerarquía hasta encontrarlo."],
    ["A la derecha del término verás «ver término» y el ", B("número de documentos"), " que tiene asignados. Pulsa en ese número: obtendrás la lista de documentos que recupera el sistema."],
    ["Abre uno de los documentos que te llame la atención e ", B("inserta aquí una captura de pantalla"), " con todos sus metadatos descriptivos."],
]
for s in steps:
    add(P(s, num=3, align="both"))

add(P([I("Metadatos del documento seleccionado")], before=120, keep=True))
add(box([[HL("[Pegad aquí vuestra captura de pantalla original y borrad esta línea. Debajo dejamos transcritos los metadatos por si la captura no se lee bien.]")]]))
add(table([
    ["Campo", "Valor"],
    [[B("Título")], "Escuchando a los niños: testimonios de menores ciegos de todo el mundo"],
    [[B("Año")], "2009"],
    [[B("Autor")], "Peláez Narváez, Ana (dir. y coord.)"],
    [[B("Otros autores")], "Stirton, David (trad.)"],
    [[B("Lugar de edición")], "Madrid"],
    [[B("Editorial")], "Comité Español de Representantes de Personas con Discapacidad (CERMI): Ediciones Cinca"],
    [[B("Tipo")], "Estudios"],
    [[B("Páginas")], "284 p."],
    [[B("Serie")], "Cermi.es; 41"],
    [[B("Idioma")], "Español"],
    [[B("Fuente")], "Comité Español de Representantes de Personas con Discapacidad (CERMI)"],
    [[B("Formato")], "Web"],
    [[B("Temáticas")], "Necesidades especiales o discapacidad"],
    [[B("Descriptores")], "deficiencia visual, ceguera, adolescentes, ONCE"],
    [[B("Resumen")], "Selección de historias de niños y niñas con discapacidad visual de distintos países y de sus familias, colegios y comunidades. Recoge testimonios diversos de superación personal como adolescentes con discapacidad (resumen del propio documento, abreviado)."],
], [2200, 6870]))

add(P("Responded a estas preguntas:", keep=True))
add(P([B("a) "), "¿En qué campo temático y bajo qué término genérico (TG) habéis encontrado «deficiencia visual»? Escribid el camino completo, de lo general a lo específico."], align="both", keep=True))
add(box([
    "Hemos encontrado el término «deficiencia visual» en el campo temático «Deficiencia, discapacidad, minusvalía, necesidades especiales». Su término genérico (TG) es «deficiencia sensorial».",
    ["El camino completo, de lo general a lo específico, es: ", B("Deficiencia, discapacidad, minusvalía, necesidades especiales → Deficiencia sensorial → Deficiencia visual"), "."],
    "Para llegar hasta él entramos en el índice jerárquico y vimos que el campo más adecuado era el de deficiencia y discapacidad. Al desplegarlo apareció «deficiencia sensorial», que agrupa las deficiencias relacionadas con los sentidos. Dentro de ella encontramos «deficiencia visual», junto a «deficiencia auditiva», que es otro término específico del mismo nivel.",
]))
add(P([B("b) "), "Revisad el metadato ", B("«Descriptores»"), " del documento seleccionado. ¿Aparece el término «deficiencia visual»? ¿Qué otros descriptores tiene?"], align="both", keep=True))
add(box([
    "Sí. En el metadato «Descriptores» del documento «Escuchando a los niños: testimonios de menores ciegos de todo el mundo» (CERMI, 2009) aparece «deficiencia visual». Sus otros descriptores son «ceguera», «adolescentes» y «ONCE».",
]))
add(P([B("c) "), "Explicad en dos o tres líneas qué relación hay entre el tesauro, los descriptores del documento y el hecho de que lo hayáis encontrado."], align="both", keep=True))
add(box([
    "Cuando se catalogó el documento, se le asignaron términos del tesauro en el campo «Descriptores», entre ellos «deficiencia visual». Al buscar desde el tesauro con ese mismo término, el sistema recupera todos los documentos que lo tienen asignado. Lo hemos encontrado porque la descripción y la búsqueda usan el mismo vocabulario controlado.",
]))

# ---------------- 4.2 Parte II
add(PB())
add(P("4.2. Parte II. Construir un minitesauro sobre alimentación (45 min)", style="Heading2"))
add(P(["Ya habéis visto cómo funciona un tesauro por dentro. Ahora vais a construir una parte de uno sobre ", B("ALIMENTACIÓN"),
       ", siguiendo los ", B("mismos pasos"), " que siguen los profesionales: primero se ", B("agrupan"),
       " los términos en grandes temas; después se ordenan de lo general a lo específico (", B("presentación jerárquica"),
       "); por último, se redacta la lista de la A a la Z con todas las relaciones (", B("presentación alfabética"), ")."], align="both"))
add(P([B("Los términos con los que trabajaréis. "), "Son 38. Los que llevan un sinónimo entre paréntesis con el signo = tienen dos formas: la primera será el ",
       B("descriptor"), " y la del paréntesis, el ", B("no descriptor"), "."], align="both"))
col1 = "almejas\nanchoa (= boquerón)\narroz\nbebida de soja (= bebida de soya)\nbizcochos\ncarne de bovino (= carne de vacuno)\ncarne de porcino\ncarnes\ncebolla\ncereal (= grano)\nchocolate\nchocolate blanco\nchocolate negro"
col2 = "frutas\nhortalizas\nhuevos\nleche\nleche de vaca\nlegumbres\nmantequilla\nmaracuyá (= fruta de la pasión)\nmarisco\nmejillones\nnata\npastel de maracuyá\npasteles"
col3 = "pescado\npez espada (= emperador)\nqueso\nqueso de oveja\ntarta de queso\ntartas\ntocino de cielo (= tocinillos)\ntomate\ntrigo\nuva\nyogur (= yogurt)\nyogur griego"
add(table([[col1, col2, col3]], [3023, 3023, 3024], header=False))

add(P([B("Paso 1. Agrupar los términos en campos temáticos (10 min)")], keep=True, before=120))
add(P(["Colocad ", B("cada término en uno de los cuatro campos"), " de la Tabla 1. Truco: cortad y pegad los términos de la lista anterior hasta que no quede ninguno; así sabréis que no os habéis dejado ninguno."], align="both"))
add(box([[B("Dos decisiones que tenéis que tomar, como haría cualquier profesional: "), "(1) los ", B("productos lácteos"), " también son de origen animal, pero como tienen su propio campo, colocadlos ", B("solo en «Productos lácteos»"), ": en un tesauro un término no se repite en dos lugares. (2) Si un término os genera dudas (por ejemplo, ¿la bebida de soja es un lácteo?), decidid entre todos dónde va y anotad por qué. Lo comentaremos en clase."]], shade="F2F2F2"))
add(P([("Tabla 1. Agrupación de términos en campos temáticos", {"color": "595959", "size": 18})], align="center", keep=True))
add(table([
    ["CAMPOS TEMÁTICOS", "TÉRMINOS"],
    [[B("PRODUCTOS DE REPOSTERÍA")], "bizcochos, chocolate, chocolate blanco, chocolate negro, pasteles, pastel de maracuyá, tartas, tarta de queso, tocino de cielo"],
    [[B("PRODUCTOS DE ORIGEN ANIMAL")], "carnes, carne de bovino, carne de porcino, pescado, anchoa, pez espada, marisco, almejas, mejillones, huevos"],
    [[B("PRODUCTOS DE ORIGEN VEGETAL")], "cereal, arroz, trigo, frutas, maracuyá, uva, hortalizas, cebolla, tomate, legumbres, bebida de soja"],
    [[B("PRODUCTOS LÁCTEOS")], "leche, leche de vaca, mantequilla, nata, queso, queso de oveja, yogur, yogur griego"],
], [2800, 6270]))
add(P([I("Comprobación: 9 + 10 + 11 + 8 = 38 términos. Los no descriptores no se colocan en los campos porque no son términos de indización.")], align="both"))
add(P("Decisiones dudosas y por qué las habéis tomado:", keep=True))
add(box([
    [B("Bebida de soja → origen vegetal. "), "No es un lácteo, porque no procede de un animal: se elabora con soja, que es una legumbre. La relacionamos con «leche» (TR) porque se usa como alternativa a ella, y con «legumbres» (TR) por su materia prima."],
    [B("Chocolate → repostería. "), "El cacao es de origen vegetal, pero el chocolate es un producto elaborado que se usa sobre todo en repostería."],
    [B("Tarta de queso, pastel de maracuyá y tocino de cielo → repostería. "), "Llevan queso, maracuyá o huevo, pero son dulces elaborados. La relación con sus ingredientes la expresamos con TR."],
    [B("Tomate → hortalizas. "), "Botánicamente es un fruto, pero en alimentación se clasifica y se consume como hortaliza."],
    [B("Mantequilla y nata → lácteos, al mismo nivel que «leche». "), "Se obtienen de la leche, pero no son un tipo de leche, así que no pueden ser TE de «leche». Las unimos con TR."],
    [B("Huevos → origen animal. "), "No son carne, pescado ni marisco, así que van directamente bajo el campo."],
    [B("Marisco y pescado → separados. "), "El marisco no es un tipo de pescado."],
]))

add(P([B("Paso 2. Elaborar la presentación jerárquica")], keep=True, before=120))
add(P(["Dentro de cada campo, ordenad los términos ", B("de lo general a lo específico"), " con sangrías, como en un árbol. Revisad atentamente estos dos ejemplos de tesauros reales:"], align="both"))
add(P([B("Ejemplo 1. Presentación jerárquica:")], keep=True))
add(tree([(0,"Administración"),(1,"Administración del personal"),(2,"Promoción del personal"),(2,"Recursos humanos"),(1,"Gestión"),(2,"Autogestión"),(0,"Ambiente demográfico"),(1,"Composición de la población"),(2,"Distribución por edades"),(3,"Adultos"),(3,"Ancianos"),(3,"Jóvenes"),(3,"Niñas"),(3,"Niños"),(2,"Distribución por sexos"),(3,"Hombres"),(3,"Mujeres")]))
add(P([B("Ejemplo 2. Presentación jerárquica:")], keep=True))
add(tree([(0,"VIDA POLÍTICA"),(1,"Marco político"),(2,"Ideología política"),(3,"Liberalismo"),(3,"Marxismo"),(3,"Anarquismo"),(3,"Comunismo"),(3,"Socialismo"),(1,"Partido político"),(2,"Organización de los partidos"),(3,"Financiación de los partidos"),(3,"Constitución de un partido"),(2,"Tendencia política"),(3,"Izquierda política"),(3,"Centro político"),(3,"Derecha política"),(3,"Extrema izquierda"),(3,"Extrema derecha")]))
add(P([B("Cómo se leen: "), "cada sangría es un nivel más concreto. En el ejemplo 1, «Distribución por sexos» es más específico que «Composición de la población», y «Hombres» y «Mujeres» son más específicos que «Distribución por sexos»."], align="both"))
add(P([B("Pista: "), "algunos de vuestros términos son generales y agrupan a otros (por ejemplo, «marisco» agrupa a «almejas» y «mejillones»). ", B("Los sinónimos no aparecen"), " en la presentación jerárquica: solo los descriptores."], align="both"))
add(P("Elaborad la presentación jerárquica de los cuatro campos temáticos a partir de vuestra Tabla 1:", align="both"))
trees = [
    ("Productos de repostería", [(0, "Bizcochos"), (0, "Chocolate"), (1, "Chocolate blanco"), (1, "Chocolate negro"), (0, "Pasteles"), (1, "Pastel de maracuyá"), (0, "Tartas"), (1, "Tarta de queso"), (0, "Tocino de cielo")]),
    ("Productos de origen animal", [(0, "Carnes"), (1, "Carne de bovino"), (1, "Carne de porcino"), (0, "Huevos"), (0, "Marisco"), (1, "Almejas"), (1, "Mejillones"), (0, "Pescado"), (1, "Anchoa"), (1, "Pez espada")]),
    ("Productos de origen vegetal", [(0, "Bebida de soja"), (0, "Cereal"), (1, "Arroz"), (1, "Trigo"), (0, "Frutas"), (1, "Maracuyá"), (1, "Uva"), (0, "Hortalizas"), (1, "Cebolla"), (1, "Tomate"), (0, "Legumbres")]),
    ("Productos lácteos", [(0, "Leche"), (1, "Leche de vaca"), (0, "Mantequilla"), (0, "Nata"), (0, "Queso"), (1, "Queso de oveja"), (0, "Yogur"), (1, "Yogur griego")]),
]
for title, lines in trees:
    add(P([B(title)], keep=True, before=60))
    add(tree(lines))

add(P([B("Paso 3. Elaborar la presentación alfabética")], keep=True, before=120))
add(P("La presentación alfabética contiene todos los términos ordenados de la A a la Z con sus relaciones. Debéis incluir:", align="both"))
add(P(["los ", B("descriptores"), " en negrita, con la relación de sinonimia (", B("UP"), "), de jerarquía (", B("TG"), "/", B("TE"), ") y de asociación (", B("TR"), ");"], num=2))
add(P(["los ", B("no descriptores"), " (sinónimos) también en su lugar alfabético, solo con ", B("USE"), " y el descriptor al que remiten."], num=2))
add(P("Así se ve en un tesauro real:", keep=True))
add(table([["Aberración cromosómica", "USE Aberración cromopática"],
           [[B("Aberración cromopática")], "UP Aberración cromosómica"],
           [[B("Abogados")], "TG Profesiones"],
           [[B("Aborto")], [["UP Interrupción del embarazo"], ["TG Control de natalidad"], ["TE Aborto ilegal"], ["TR Intervención"]]],
           [[B("Aborto ilegal")], "TG Aborto"],
           ["Abuso de poder", "USE Abuso de superioridad"],
           [[B("Abuso de superioridad")], [["UP Abuso de poder"], ["TG Abusos"]]]], [3400, 5670], header=False))
add(box([[B("Cómo repartiros el trabajo: "), "dividid el alfabeto entre los miembros del grupo, por ejemplo, A–C, Ch–M y N–Y. ", B("Comprobación final (muy importante): "), "las relaciones son ", B("recíprocas"), ". Si en «Almejas» escribís «TG Marisco», en «Marisco» tiene que aparecer «TE Almejas»; si en «Boquerón» pone «USE Anchoa», en «Anchoa» tiene que aparecer «UP Boquerón»; y si «Tarta de queso» lleva «TR Queso», «Queso» debe llevar «TR Tarta de queso». La persona coordinadora revisa que todo cuadre. Incluid al menos ", B("cuatro relaciones TR"), "."]], shade="F2F2F2"))
add(P(["Os damos hechos los tres primeros términos. Continuad a partir de ", B("Bebida de soja"), " hasta llegar a ", B("Yogur griego"), ":"], align="both"))
alpha = [
    ("Almejas", True, ["TG Marisco"]),
    ("Anchoa", True, ["UP Boquerón", "TG Pescado"]),
    ("Arroz", True, ["TG Cereal"]),
    ("Bebida de soja", True, ["UP Bebida de soya", "TR Leche", "TR Legumbres"]),
    ("Bebida de soya", False, ["USE Bebida de soja"]),
    ("Bizcochos", True, ["TR Huevos", "TR Trigo"]),
    ("Boquerón", False, ["USE Anchoa"]),
    ("Carne de bovino", True, ["UP Carne de vacuno", "TG Carnes"]),
    ("Carne de porcino", True, ["TG Carnes"]),
    ("Carne de vacuno", False, ["USE Carne de bovino"]),
    ("Carnes", True, ["TE Carne de bovino", "TE Carne de porcino"]),
    ("Cebolla", True, ["TG Hortalizas"]),
    ("Cereal", True, ["UP Grano", "TE Arroz", "TE Trigo"]),
    ("Chocolate", True, ["TE Chocolate blanco", "TE Chocolate negro"]),
    ("Chocolate blanco", True, ["TG Chocolate"]),
    ("Chocolate negro", True, ["TG Chocolate"]),
    ("Emperador", False, ["USE Pez espada"]),
    ("Fruta de la pasión", False, ["USE Maracuyá"]),
    ("Frutas", True, ["TE Maracuyá", "TE Uva"]),
    ("Grano", False, ["USE Cereal"]),
    ("Hortalizas", True, ["TE Cebolla", "TE Tomate"]),
    ("Huevos", True, ["TR Bizcochos", "TR Tocino de cielo"]),
    ("Leche", True, ["TE Leche de vaca", "TR Bebida de soja", "TR Mantequilla", "TR Nata"]),
    ("Leche de vaca", True, ["TG Leche"]),
    ("Legumbres", True, ["TR Bebida de soja"]),
    ("Mantequilla", True, ["TR Leche"]),
    ("Maracuyá", True, ["UP Fruta de la pasión", "TG Frutas", "TR Pastel de maracuyá"]),
    ("Marisco", True, ["TE Almejas", "TE Mejillones"]),
    ("Mejillones", True, ["TG Marisco"]),
    ("Nata", True, ["TR Leche"]),
    ("Pastel de maracuyá", True, ["TG Pasteles", "TR Maracuyá"]),
    ("Pasteles", True, ["TE Pastel de maracuyá"]),
    ("Pescado", True, ["TE Anchoa", "TE Pez espada"]),
    ("Pez espada", True, ["UP Emperador", "TG Pescado"]),
    ("Queso", True, ["TE Queso de oveja", "TR Tarta de queso"]),
    ("Queso de oveja", True, ["TG Queso"]),
    ("Tarta de queso", True, ["TG Tartas", "TR Queso"]),
    ("Tartas", True, ["TE Tarta de queso"]),
    ("Tocinillos", False, ["USE Tocino de cielo"]),
    ("Tocino de cielo", True, ["UP Tocinillos", "TR Huevos"]),
    ("Tomate", True, ["TG Hortalizas"]),
    ("Trigo", True, ["TG Cereal", "TR Bizcochos"]),
    ("Uva", True, ["TG Frutas"]),
    ("Yogur", True, ["UP Yogurt", "TE Yogur griego"]),
    ("Yogur griego", True, ["TG Yogur"]),
    ("Yogurt", False, ["USE Yogur"]),
]
rows = [["Término", "Relaciones"]]
for term, desc, rels in alpha:
    rows.append([[B(term)] if desc else term, [[r] for r in rels]])
add(table(rows, [3400, 5670]))
add(box([
    [B("Comprobación final (coordinación). "), "Todas las relaciones son recíprocas: cada TG tiene su TE correspondiente, cada USE su UP y cada TR aparece en los dos términos. La lista tiene 46 entradas: 38 descriptores y 8 no descriptores, y 8 relaciones TR (se pedían al menos 4)."],
    [B("Orden alfabético. "), "Seguimos la norma actual de la RAE, en la que la «ch» se ordena dentro de la «c» (después de «ce»). Se ordena palabra por palabra, por eso «Carne de vacuno» va antes que «Carnes» y «Leche de vaca» antes que «Legumbres»."],
    [B("Términos de primer nivel. "), "Los términos que encabezan cada campo (por ejemplo, Carnes, Huevos o Leche) no llevan TG porque los campos temáticos son categorías de agrupación, no descriptores de la lista."],
], shade="F2F2F2"))

# ---------------- package
sect = ('<w:sectPr><w:headerReference w:type="default" r:id="rIdH1"/><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1418" w:right="1418" w:bottom="1418" w:left="1418" w:header="709" w:footer="709" w:gutter="0"/></w:sectPr>')
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
document = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {NS}><w:body>{"".join(body)}{sect}</w:body></w:document>'

header = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:hdr {NS}><w:p><w:pPr><w:jc w:val="right"/></w:pPr>'
          f'{run("Information Science", size=20)}</w:p></w:hdr>')

styles = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {NS}>
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" w:cs="Calibri"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="es-ES"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:keepNext/><w:spacing w:before="240" w:after="120"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:color w:val="{BLUE}"/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:keepNext/><w:spacing w:before="200" w:after="100"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:color w:val="4472C4"/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr></w:style>
</w:styles>'''

def absnum(i, fmt, txt):
    return (f'<w:abstractNum w:abstractNumId="{i}"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/>'
            f'<w:numFmt w:val="{fmt}"/><w:lvlText w:val="{txt}"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>')
numbering = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:numbering {NS}>'
             + absnum(1, "decimal", "%1.") + absnum(2, "bullet", "●") + absnum(3, "decimal", "%1.")
             + '<w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num><w:num w:numId="2"><w:abstractNumId w:val="2"/></w:num><w:num w:numId="3"><w:abstractNumId w:val="3"/></w:num></w:numbering>')

content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>'''
rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>'''
doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rIdH1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
</Relationships>'''
core = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>Práctica 3. Los tesauros: de usarlos a construirlos</dc:title><dc:language>es-ES</dc:language></cp:coreProperties>'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Practica3_Tesauros_completa.docx")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types)
    z.writestr("_rels/.rels", rels)
    z.writestr("word/document.xml", document)
    z.writestr("word/_rels/document.xml.rels", doc_rels)
    z.writestr("word/styles.xml", styles)
    z.writestr("word/numbering.xml", numbering)
    z.writestr("word/header1.xml", header)
    z.writestr("docProps/core.xml", core)
print(out)
