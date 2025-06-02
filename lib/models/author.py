# lib/models/author.py
from lib.db.connection import get_connection

class Author:
    def __init__(self, name, id=None,**kwargs):
        self.id = id
        self.name = name
        self.article_count = kwargs.get("article_count")

    def save(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            if self.id:
                cursor.execute("UPDATE authors SET name = ? WHERE id = ?", (self.name, self.id))
            else:
                cursor.execute("INSERT INTO authors (name) VALUES (?)", (self.name,))
                self.id = cursor.lastrowid
            conn.commit()

    @classmethod
    def find_by_name(cls, name):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM authors WHERE name = ?", (name,))
            row = cursor.fetchone()
            return cls(**row) if row else None

    def articles(self):
        from lib.models.article import Article
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM articles WHERE author_id = ?", (self.id,))
            rows = cursor.fetchall()
            return [Article(**row) for row in rows]

    def magazines(self):
        from lib.models.magazine import Magazine
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT magazines.*
                FROM magazines
                JOIN articles ON articles.magazine_id = magazines.id
                WHERE articles.author_id = ?
            """, (self.id,))
            rows = cursor.fetchall()
            return [Magazine(**row) for row in rows]

    def add_article(self, magazine, title):
        from lib.models.article import Article
        article = Article(title=title, author_id=self.id, magazine_id=magazine.id)
        article.save()
        return article

    @classmethod
    def top_author(cls):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT authors.*, COUNT(articles.id) AS article_count
                FROM authors
                JOIN articles ON authors.id = articles.author_id
                GROUP BY authors.id
                ORDER BY article_count DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            return cls(**row) if row else None