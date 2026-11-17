"""Genera memorias y presentaciones desde Markdown sin cargar el modelo ML.

Instalar docs/entrega/requirements-documentacion.txt en un entorno separado.
Los originales, el modelo y los resultados no se escriben desde este script.
"""
from __future__ import annotations

import hashlib
import json
import re
from html import escape
from pathlib import Path

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate, CondPageBreak, Flowable, Frame, Image, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/entrega'
BLUE = colors.HexColor('#123e53')
TEAL = colors.HexColor('#087e83')
LIGHT = colors.HexColor('#edf5f6')


def fonts():
    directory = Path(reportlab.__file__).parent / 'fonts'
    for name, filename in [('Body', 'Vera.ttf'), ('Body-Bold', 'VeraBd.ttf'),
                           ('Body-Italic', 'VeraIt.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(directory / filename)))
    pdfmetrics.registerFontFamily('Body', normal='Body', bold='Body-Bold', italic='Body-Italic')


def inline(text):
    text = escape(text)
    text = re.sub(r'`([^`]+)`', lambda m: '<font color="#125b70">' + m[1] + '</font>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', r'<link href="\2" color="#087e83">\1</link>', text)
    text = re.sub(r'(?<!["=])(https?://[^\s<]+)', lambda m: '<link href="' + m[1].rstrip('.') + '" color="#087e83">' + m[1] + '</link>', text) if '<link' not in text else text
    return text


def style(size=10.4, **kwargs):
    options = dict(fontName='Body', fontSize=size, leading=size * 1.48,
                   textColor=BLUE, spaceAfter=9, alignment=TA_LEFT,
                   splitLongWords=True, allowWidows=0, allowOrphans=0)
    options.update(kwargs)
    return ParagraphStyle('body', **options)


class FlowDiagram(Flowable):
    def __init__(self, labels, width, slide=False):
        super().__init__()
        self.labels, self.width, self.height = labels, width, 140 if slide else 84
        self.slide = slide

    def draw(self):
        c = self.canv
        gap = 13
        n = len(self.labels)
        box = (self.width - gap * (n-1)) / n
        for i, label in enumerate(self.labels):
            x = i * (box + gap)
            c.setFillColor(LIGHT)
            c.setStrokeColor(TEAL)
            c.roundRect(x, 14, box, self.height - 28, 6, fill=1, stroke=1)
            p = Paragraph(inline(label), style(20 if self.slide else 9))
            _, h = p.wrap(box - 14, self.height)
            p.drawOn(c, x + 7, (self.height - h)/2)
            if i < n-1:
                c.setStrokeColor(TEAL)
                c.line(x + box + 2, self.height/2, x + box + gap-2, self.height/2)
                c.line(x + box + gap-5, self.height/2+3, x + box + gap-2, self.height/2)
                c.line(x + box + gap-5, self.height/2-3, x + box + gap-2, self.height/2)


class InfoCards(Flowable):
    """Tarjetas paralelas: cantidades o ideas que se leen de un vistazo."""
    def __init__(self, items, width):
        super().__init__()
        self.items, self.width, self.height = items, width, 190

    def draw(self):
        gap = 18
        box = (self.width - gap * (len(self.items)-1)) / len(self.items)
        for i, item in enumerate(self.items):
            heading, description = item.split('::', 1)
            x = i * (box + gap)
            self.canv.setFillColor(LIGHT)
            self.canv.roundRect(x, 8, box, self.height-16, 9, fill=1, stroke=0)
            numeric = bool(re.fullmatch(r'[\d ,.€%]+', heading.strip()))
            title = Paragraph(inline(heading.strip()), style(42 if numeric else 24, leading=32))
            _, th = title.wrap(box-28, 70)
            title.drawOn(self.canv, x+14, self.height-25-th)
            text = Paragraph(inline(description.strip()), style(19, leading=26))
            _, bh = text.wrap(box-28, 100)
            if 25+th+12+bh > self.height-12:
                raise ValueError('Tarjeta desbordada: ' + item)
            text.drawOn(self.canv, x+14, self.height-25-th-12-bh)


def table(rows, width, slide=False):
    n = len(rows[0])
    if slide:
        widths = [width/n]*n
        size = 17
    else:
        size = 8.2 if n > 5 else 9
        if n >= 6:
            widths = [width*.25] + [width*.75/(n-1)]*(n-1)
        else:
            weights = [min(48, max(16, max(len(r[i]) for r in rows))) for i in range(n)]
            widths = [width*w/sum(weights) for w in weights]
    rendered = [[Paragraph(inline(cell), ParagraphStyle('cell', parent=style(size), spaceAfter=0,
                                          textColor=colors.white if j == 0 else BLUE))
                 for cell in row] for j, row in enumerate(rows)]
    t = Table(rendered, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LINEBELOW', (0, 0), (-1, 0), 1, TEAL),
    ]))
    return t


def blocks(lines, source, width, slide=False):
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i]); i += 1
            for item in code:
                result.append(Paragraph(escape(item) or ' ', ParagraphStyle('code', parent=style(8.2),
                    backColor=LIGHT, borderPadding=5, spaceAfter=4)))
            result.append(Spacer(1, 8))
        elif line.startswith(':::flow '):
            result.append(FlowDiagram([s.strip() for s in line[8:].split('|')], width, slide))
        elif line.startswith(':::cards '):
            result.append(InfoCards([s.strip() for s in line[9:].split('|')], width))
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [s.strip() for s in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+', c) for c in row):
                    rows.append(row)
                i += 1
            result.append(table(rows, width, slide))
            result.append(Spacer(1, 12))
            continue
        elif line.startswith('!['):
            match = re.fullmatch(r'!\[(.*)\]\((.*)\)', line)
            if not match:
                raise ValueError(line)
            path = (source.parent / match[2]).resolve()
            im = Image(str(path))
            ratio = min(width/im.imageWidth, (300 if slide else 350)/im.imageHeight)
            im.drawWidth, im.drawHeight = im.imageWidth*ratio, im.imageHeight*ratio
            im.hAlign = 'LEFT'
            im.keepWithNext = not slide
            result.extend([im, Spacer(1, 6)])
            if not slide:
                caption = Paragraph(inline(match[1]), style(8.5))
                caption.keepWithNext = True
                result.append(caption)
        else:
            para = [line]
            while i+1 < len(lines) and lines[i+1].strip() and not lines[i+1].startswith(('|', '![', ':::', '```', '#')):
                i += 1; para.append(lines[i].strip())
            result.append(Paragraph(inline(' '.join(para)), style(19 if slide else 10.4)))
        i += 1
    return result


class Report(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == 'chapter':
            key = 'section-' + str(self.seq.nextf('heading'))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.getPlainText(), key, 0, False)
            self.notify('TOCEntry', (0, flowable.getPlainText(), self.page, key))


def report(source):
    lines = source.read_text(encoding='utf-8').splitlines()
    title = lines[0].removeprefix('# ')
    target = source.with_suffix('.pdf')
    doc = Report(str(target), pagesize=A4, leftMargin=48, rightMargin=48,
                 topMargin=51, bottomMargin=48, title=title,
                 author='Equipo del proyecto Reto 1')
    def footer(c, d):
        c.setStrokeColor(TEAL); c.line(48, 40, A4[0]-48, 40)
        c.setFont('Body', 8); c.setFillColor(BLUE)
        c.drawString(48, 27, 'Reto 1 · Vivienda en Euskadi')
        c.drawRightString(A4[0]-48, 27, str(d.page))
    doc.addPageTemplates(PageTemplate(id='report', frames=[Frame(48, 48, doc.width, doc.height, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=footer))
    story = [Spacer(1, 70), Paragraph('RETO 1 · ACCESO A LA VIVIENDA', style(12)),
             Paragraph(inline(title), ParagraphStyle('title', parent=style(30), leading=38, spaceAfter=25)),
             Paragraph('Curso de Especialización en Inteligencia Artificial y Big Data', style(13)),
             Spacer(1, 25),
             Paragraph('Repositorio y archivos funcionales', style(11)),
             Paragraph('<link href="https://github.com/markelalvarez0/Reto-1" color="#087e83">https://github.com/markelalvarez0/Reto-1</link>', style(10)),
             PageBreak(), Paragraph('Contenido', style(24))]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle('toc', parent=style(10), leading=15, spaceBefore=4)]
    story.extend([toc, PageBreak()])
    chapter = ParagraphStyle('chapter', parent=style(19), leading=25, spaceBefore=20,
                             spaceAfter=14, keepWithNext=False)
    sections = re.split(r'^## (.+)$', '\n'.join(lines[1:]), flags=re.M)
    for idx in range(1, len(sections), 2):
        story.append(CondPageBreak(130))
        story.append(Paragraph(inline(sections[idx]), chapter))
        story.extend(blocks(sections[idx+1].splitlines(), source, doc.width))
    doc.multiBuild(story)
    return target


def slides(source):
    text = source.read_text(encoding='utf-8')
    sections = re.split(r'^## (.+)$', text, flags=re.M)
    target = source.with_suffix('.pdf')
    c = canvas.Canvas(str(target), pagesize=(960, 540))
    c.setTitle(text.splitlines()[0].removeprefix('# '))
    c.setAuthor('Equipo del proyecto Reto 1')
    total = (len(sections)-1)//2
    for idx in range(1, len(sections), 2):
        c.setFillColor(colors.white); c.rect(0, 0, 960, 540, fill=1, stroke=0)
        c.setFillColor(TEAL); c.rect(0, 525, 960, 15, fill=1, stroke=0)
        title = Paragraph(inline(sections[idx]), style(28, leading=34))
        _, h = title.wrap(856, 100)
        title.drawOn(c, 52, 488-h)
        y = 466-h
        for block in blocks(sections[idx+1].splitlines(), source, 856, True):
            _, bh = block.wrap(856, 450)
            if y-bh < 49:
                raise ValueError(f'Diapositiva desbordada: {source.name}: {sections[idx]}')
            block.drawOn(c, 52, y-bh)
            y -= bh + (12 if isinstance(block, Paragraph) else 8)
        c.setFillColor(BLUE); c.setFont('Body', 9)
        c.drawString(52, 24, 'Reto 1 · Vivienda en Euskadi')
        c.drawRightString(908, 24, f'{(idx+1)//2} / {total}')
        c.showPage()
    c.save()
    return target


def main():
    fonts()
    outputs = []
    sources = sorted(OUT.rglob('*.md'))
    sources += sorted((ROOT / 'docs/paquetes').glob('Instrucciones_*.md'))
    restoration = ROOT / 'data/exportaciones_entrega_2026-11-17/Instrucciones_restauracion.md'
    if restoration.is_file():
        sources.append(restoration)
    for source in sources:
        if source.name == 'README.md':
            continue
        target = slides(source) if source.name.startswith('Presentacion_') else report(source)
        outputs.append({'archivo': str(target.relative_to(ROOT)),
                        'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                        'fuente': str(source.relative_to(ROOT))})
        print(target.relative_to(ROOT))
    (OUT / 'manifest_documentos.json').write_text(json.dumps({
        'base_codigo': '0f990531c86a7b4f247cb80631b02609fed687a0',
        'fecha': '2026-11-17', 'documentos': outputs,
        'modelo_cargado': False, 'test_reevaluado': False,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
