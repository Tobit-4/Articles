# lib/models/article.py
from lib.db.connection import get_connection

class Article:
    def __init__(self, title, author_id, magazine_id, id=None):
        self.id = id
        self.title = title
        self.author_id = author_id
        self.magazine_id = magazine_id

    def save(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            if self.id:
                cursor.execute("""
                    UPDATE articles SET 
                    title = ?, author_id = ?, magazine_id = ? 
                    WHERE id = ?
                """, (self.title, self.author_id, self.magazine_id, self.id))
            else:
                cursor.execute("""
                    INSERT INTO articles (title, author_id, magazine_id)
                    VALUES (?, ?, ?)
                """, (self.title, self.author_id, self.magazine_id))
                self.id = cursor.lastrowid
            conn.commit()

    @classmethod
    def find_by_title(cls, title):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM articles WHERE title = ?", (title,))
            row = cursor.fetchone()
            return cls(**row) if row else None

    def author(self):
        from lib.models.author import Author
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM authors WHERE id = ?", (self.author_id,))
            row = cursor.fetchone()
            return Author(**row) if row else None

    def magazine(self):
        from lib.models.magazine import Magazine
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM magazines WHERE id = ?", (self.magazine_id,))
            row = cursor.fetchone()
            return Magazine(**row) if row else None