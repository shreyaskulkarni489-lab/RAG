import os
import sys
import glob
import json
import uuid

# Ensure backend root is on sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.document import Document, DocumentChunk, DocStatus
from app.security.pwd import get_password_hash
from app.services.parser import DocumentParser
from app.services.chunker import RecursiveChunker
from app.services.embedder import embedding_service

def seed():
    print("[Seeder] Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create Admin user
        admin = db.query(User).filter(User.email == "admin@campusmind.edu").first()
        if not admin:
            admin = User(
                id=str(uuid.uuid4()),
                name="Campus Admin",
                email="admin@campusmind.edu",
                password_hash=get_password_hash("admin123"),
                role=UserRole.admin
            )
            db.add(admin)
            print("[Seeder] Created default admin: admin@campusmind.edu / admin123")
        else:
            # Update password hash in case hashing algorithm changed
            admin.password_hash = get_password_hash("admin123")
            admin.role = UserRole.admin

        # Create Student user
        student = db.query(User).filter(User.email == "student@campusmind.edu").first()
        if not student:
            student = User(
                id=str(uuid.uuid4()),
                name="Jane Doe (Student)",
                email="student@campusmind.edu",
                password_hash=get_password_hash("student123"),
                role=UserRole.student
            )
            db.add(student)
            print("[Seeder] Created default student: student@campusmind.edu / student123")
        else:
            # Update password hash in case hashing algorithm changed
            student.password_hash = get_password_hash("student123")
            student.role = UserRole.student

        db.commit()

        # Ingest Seed Documents from seed_data/ directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        seed_dir = os.path.join(project_root, "seed_data")
        files = glob.glob(os.path.join(seed_dir, "*.*"))

        for file_path in files:
            filename = os.path.basename(file_path)
            title = filename.replace("_", " ").replace(".txt", "").replace(".pdf", "")

            # Check if document already exists
            existing_doc = db.query(Document).filter(Document.filename == filename).first()
            if existing_doc:
                print(f"[Seeder] Document already seeded: {filename}")
                continue

            print(f"[Seeder] Processing and embedding: {filename}...")
            doc_id = str(uuid.uuid4())
            doc = Document(
                id=doc_id,
                title=title,
                filename=filename,
                file_path=file_path,
                department="General",
                collection="Campus Information",
                uploaded_by=admin.id,
                status=DocStatus.processing,
                version=1
            )
            db.add(doc)
            db.commit()

            # Parse and Chunk
            pages = DocumentParser.parse_file(file_path)
            chunker = RecursiveChunker()
            chunks = chunker.chunk_pages(pages)

            # Embed
            texts = [c["chunk_text"] for c in chunks]
            embeddings = embedding_service.embed_batch(texts)

            for chunk_data, emb in zip(chunks, embeddings):
                chunk_obj = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=doc.id,
                    chunk_text=chunk_data["chunk_text"],
                    chunk_index=chunk_data["chunk_index"],
                    page_number=chunk_data["page_number"],
                    embedding_json=json.dumps(emb)
                )
                db.add(chunk_obj)

            doc.status = DocStatus.processed
            db.commit()
            print(f"[Seeder] Successfully indexed {len(chunks)} chunks for {filename}.")

        print("[Seeder] Database seeding finished successfully!")

    except Exception as e:
        print(f"[Seeder] Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
