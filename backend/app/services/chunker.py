from typing import List, Dict, Any

class RecursiveChunker:
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        Splits text recursively prioritizing paragraphs, sentences, and words.
        """
        if not text:
            return []

        # Split on paragraph boundaries first
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    # compute overlap from the end of current_chunk
                    overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                    current_chunk = overlap_text + "\n\n" + para if len(para) <= self.chunk_size else ""

                # If paragraph itself is too large, split by lines or sentences
                if len(para) > self.chunk_size:
                    sentences = para.replace(". ", ".\n").split("\n")
                    sub_chunk = ""
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        if len(sub_chunk) + len(sent) + 1 <= self.chunk_size:
                            sub_chunk += (" " if sub_chunk else "") + sent
                        else:
                            if sub_chunk:
                                chunks.append(sub_chunk)
                            sub_chunk = sent
                    if sub_chunk:
                        current_chunk = sub_chunk

        if current_chunk and current_chunk not in chunks:
            chunks.append(current_chunk)

        return chunks

    def chunk_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunks parsed pages retaining page_number metadata.
        Returns: [{"chunk_text": str, "page_number": int, "chunk_index": int}]
        """
        all_chunks = []
        chunk_idx = 0
        for page in pages:
            page_num = page.get("page_number", 1)
            text = page.get("text", "")
            raw_chunks = self.split_text(text)
            for c in raw_chunks:
                if c.strip():
                    all_chunks.append({
                        "chunk_text": c.strip(),
                        "page_number": page_num,
                        "chunk_index": chunk_idx
                    })
                    chunk_idx += 1
        return all_chunks
