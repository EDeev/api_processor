import base64
import csv
from html import escape
from io import StringIO

import docx
import pdfplumber

# сигнатуры форматов: картинка из PDF — это сырой поток, не обязательно PNG
IMAGE_SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"GIF8": "image/gif",
}


def image_mime(data: bytes):
    for signature, mime in IMAGE_SIGNATURES.items():
        if data.startswith(signature):
            return mime
    return None


def img_tag(data: bytes, mime: str) -> str:
    return f'<img src="data:{mime};base64,{base64.b64encode(data).decode("utf-8")}"/>'


def table_to_pre(rows) -> str:
    csv_output = StringIO()
    csv.writer(csv_output).writerows([[cell if cell is not None else "" for cell in row] for row in rows])
    return f"<pre>{escape(csv_output.getvalue())}</pre>"


def extract_text_tables(file_path: str) -> str:
    """Текст, таблицы (CSV) и изображения документа одной HTML-строкой.
    Текст экранируется: иначе содержимое документа становится разметкой (XSS у потребителя)"""
    result = ""
    path = file_path.lower()  # раньше файл «.PDF» молча давал пустой результат

    if path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    result += "".join(f"<p>{escape(line)}</p>" for line in text.split("\n"))

                for table in page.extract_tables() or []:
                    result += table_to_pre(table)

                # Извлечение изображений — только тех, что лежат в PDF готовым файлом (PNG/JPEG)
                for img in page.images:
                    data = img["stream"].get_data()
                    mime = image_mime(data)
                    if mime:
                        result += img_tag(data, mime)

    elif path.endswith(".docx"):
        doc = docx.Document(file_path)

        result += "".join(f"<p>{escape(para.text)}</p>" for para in doc.paragraphs if para.text.strip())
        result += "".join(table_to_pre([[cell.text.strip() for cell in row.cells] for row in table.rows])
                          for table in doc.tables)

        # Извлечение изображений с их настоящим типом
        for rel in doc.part.rels.values():
            if "image" in rel.reltype and not rel.is_external:
                part = rel.target_part
                result += img_tag(part.blob, part.content_type)

    return result
