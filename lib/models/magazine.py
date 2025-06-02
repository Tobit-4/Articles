# lib/models/magazine.py
from lib.db.connection import get_connection

class Magazine:
    def __init__(self, name, category, id=None,**kwargs):
        self.id = id
        self.name = name
        self.category = category
        self.article_count = kwargs.get("article_count")


    def save(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            if self.id:
                cursor.execute(
                    "UPDATE magazines SET name = ?, category = ? WHERE id = ?",
                    (self.name, self.category, self.id)
                )
            else:
                cursor.execute(
                    "INSERT INTO magazines (name, category) VALUES (?, ?)",
                    (self.name, self.category)
                )
                self.id = cursor.lastrowid
            conn.commit()

    @classmethod
    def find_by_name(cls, name):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM magazines WHERE name = ?", (name,))
            row = cursor.fetchone()
            return cls(**row) if row else None

    @classmethod
    def find_by_category(cls, category):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM magazines WHERE category = ?", (category,))
            return [cls(**row) for row in cursor.fetchall()]

    def articles(self):
        from lib.models.article import Article
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM articles WHERE magazine_id = ?", (self.id,))
            return [Article(**row) for row in cursor.fetchall()]

    def contributors(self):
        from lib.models.author import Author
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT authors.* FROM authors
                JOIN articles ON authors.id = articles.author_id
                WHERE articles.magazine_id = ?
            """, (self.id,))
            return [Author(**row) for row in cursor.fetchall()]

    def article_titles(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM articles WHERE magazine_id = ?", (self.id,))
            return [row['title'] for row in cursor.fetchall()]

    def contributing_authors(self):
        from lib.models.author import Author
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT authors.*, COUNT(articles.id) as article_count
                FROM authors
                JOIN articles ON authors.id = articles.author_id
                WHERE articles.magazine_id = ?
                GROUP BY authors.id
                HAVING article_count > 2
            """, (self.id,))
            return [Author(**row) for row in cursor.fetchall()]

    @classmethod
    def with_multiple_authors(cls):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT magazines.* FROM magazines
                JOIN articles ON magazines.id = articles.magazine_id
                GROUP BY magazines.id
                HAVING COUNT(DISTINCT articles.author_id) >= 2
            """)
            return [cls(**row) for row in cursor.fetchall()]

    @classmethod
    def article_counts(cls):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT magazines.*, COUNT(articles.id) as article_count
                FROM magazines
                LEFT JOIN articles ON magazines.id = articles.magazine_id
                GROUP BY magazines.id
            """)
            results = []
            for row in cursor.fetchall():
                magazine = cls(**row)
                magazine.article_count = row['article_count']
                results.append(magazine)
            return results