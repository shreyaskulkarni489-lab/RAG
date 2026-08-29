import os
from typing import List, Dict, Any

class DocumentParser:
    @staticmethod
    def parse_file(file_path: str) -> List[Dict[str, Any]]:
        """
        Parses PDF, DOCX, or TXT file and returns a list of pages with page numbers and text.
        Returns: [{"page_number": int, "text": str}]
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return DocumentParser._parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return DocumentParser._parse_docx(file_path)
        elif ext in [".txt", ".md", ".csv", ".json"]:
            return DocumentParser._parse_txt(file_path)
        else:
            return DocumentParser._parse_txt(file_path)

    @staticmethod
    def _parse_pdf(file_path: str) -> List[Dict[str, Any]]:
        pages = []
        try:
            import fitz # PyMuPDF
            doc = fitz.open(file_path)
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                text = page.get_text()
                if text.strip():
                    pages.append({
                        "page_number": page_idx + 1,
                        "text": text.strip()
                    })
            doc.close()
        except Exception as e:
            print(f"[DocumentParser] PyMuPDF extraction warning: {e}. Trying fallback text read.")
            return DocumentParser._parse_txt(file_path)
        return pages if pages else [{"page_number": 1, "text": "Document content could not be extracted as text."}]

    @staticmethod
    def _parse_docx(file_path: str) -> List[Dict[str, Any]]:
        try:
            import docx
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text.strip())

            combined = "\n\n".join(full_text)
            return [{"page_number": 1, "text": combined}] if combined else []
        except Exception as e:
            print(f"[DocumentParser] docx extraction warning: {e}. Trying fallback text read.")
            return DocumentParser._parse_txt(file_path)

    @staticmethod
    def _parse_txt(file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return [{"page_number": 1, "text": text.strip()}] if text.strip() else []
        except Exception as e:
            print(f"[DocumentParser] txt read error: {e}")
            return []

