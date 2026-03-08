# backend/document_processor.py
import docx
import io
from typing import List, Dict

# =====================================================================
#                        CONFIGURAÇÕES GERAIS
# =====================================================================

REQUIRED_TAGS: List[str] = [
    "[NOME DO COLABORADOR]",
    "[NÚMERO DA CARTEIRA]",
    "[DIA, MÊS E ANO]",
]

# =====================================================================
#                        VALIDAÇÃO E PROCESSAMENTO EM RAM
# =====================================================================


def check_tags_in_docx(file_stream: io.BytesIO) -> List[str]:
    """
    Lê um fluxo binário de arquivo .docx direto da RAM e verifica as tags.
    """
    doc = docx.Document(file_stream)
    full_text: List[str] = []

    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    full_text.append(cell.text)

    full_text_str = " ".join(full_text)

    missing_tags = [tag for tag in REQUIRED_TAGS if tag not in full_text_str]
    return missing_tags


def fill_contract(file_stream: io.BytesIO, context: Dict[str, str]) -> io.BytesIO:
    """
    Abre o modelo binário, substitui as chaves e devolve um novo fluxo de memória.
    NENHUM arquivo é salvo no disco rígido.
    """
    doc = docx.Document(file_stream)

    def replace_text_in_paragraphs(paragraphs) -> None:
        for para in paragraphs:
            for key, value in context.items():
                if key in para.text:
                    for run in para.runs:
                        if key in run.text:
                            run.text = run.text.replace(key, value)

                    if key in para.text:
                        para.text = para.text.replace(key, value)

    replace_text_in_paragraphs(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                replace_text_in_paragraphs(cell.paragraphs)

    # Cria um novo arquivo binário na memória RAM para devolver ao usuário
    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)

    return output_stream
