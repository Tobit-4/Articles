# Auto-generated absolute class imports
from lib.models.author import Author
from lib.models.magazine import Magazine
from lib.models.article import Article

from lib.db.connection import get_connection
import sqlite3
import pytest
import os
from faker import Faker
from random import random

if not callable(globals().get("get_connection")):
    from lib.db.connection import get_connection

def insert_values(tbl, vals={}):
    conn = get_connection()
    cursor = conn.cursor()

    info = cursor.execute(f"SELECT name, type FROM pragma_table_info('{tbl}')")
    for i in info:
        col, type = i
        if col in vals or col.count("_id") > 0 or col == 'id': continue
        if hasattr(Faker, col):
            vals[col] = getattr(Faker(), col)
        elif type == "TEXT":
            vals[col] = Faker().text(max_nb_chars=10)
        else:
            vals[col] = int(random())

    cols = ",".join(vals.keys())
    q = f"INSERT INTO {tbl} ({cols}) VALUES ({'?,'*(len(vals.keys())-1)}?)"
    print(q)
    cursor.execute(q, (*vals.values(), ))
    conn.commit()
    conn.close()

def init_schema():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in filenames:
            if filename == "schema.sql":
                full_path = os.path.join(dirpath, filename)           
                with open(full_path) as f:
                    conn.executescript(f.read())

    cursor = conn.cursor()
    cursor.execute("DELETE FROM authors")
    cursor.execute("DELETE FROM magazines")
    cursor.execute("DELETE FROM articles")
    conn.commit()
    conn.close()

@pytest.fixture(scope="session", autouse=True)
def setup_before_all_tests():
    init_schema()

    insert_values("authors", {"name":'Alice'})
    insert_values("authors", {"name":'Bob'})
    
    insert_values("magazines", {"name":"Tech Times", "category":"Technology"})
    insert_values("magazines", {"name":"Health Weekly", "category":"Health"})

    insert_values("articles", {"title":"AI Revolution", "author_id":1, "magazine_id":1})
    insert_values("articles", {"title":"Future of Health", "author_id":1, "magazine_id":2})
    insert_values("articles", {"title":"Cybersecurity Tips", "author_id":2, "magazine_id":1})

def clean_up(tbl):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ?", (tbl,))
    conn.commit()
    conn.close()

def find_by_name(cls, tbl, name):
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute(f"SELECT * FROM {tbl} WHERE name = ?", (name,))
    record = row.fetchone()
    return cls(**{ desc[0]: record[desc[0]] if type(record) != tuple else record[i] \
                  for i, desc in enumerate(row.description) })

def count(tbl, where):
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    for k, v in where.items():
        params.append(k)
        params.append(v)
    q = "SELECT COUNT(*) AS count FROM %s WHERE %s = ?" % (tbl, *where.keys(),)
    row = cursor.execute(q, (*where.values(),)).fetchone()
    conn.close()
    return row["count"]

def get_row(tbl):
    conn = get_connection()
    cursor = conn.cursor()
    return cursor.execute(f"SELECT * FROM {tbl}")

def get_value(row, obj, attr):
    if hasattr(obj, attr):
        return getattr(obj, attr)
    
    if type(obj) == dict and attr in obj:
        item = { desc[0]: obj.get(desc[0]) for desc in row.description }
        return item.get(attr)

    if not hasattr(obj, attr):
        item = { desc[0]: obj[desc[0]] for desc in row.description }
        return item.get(attr)
    
def get_one(records):
    if type(records) == list:
        return records[0]
    else: 
        return records

def test_author_save_and_find():
    author = Author(name="Charlie")
    author.save()
    found = None
    if callable(globals().get("Author.find_by_name")):
        found = Author.find_by_name("Charlie")
    else:
        found = find_by_name(Author, 'authors', "Charlie")
    assert not None and found.name == "Charlie"

def test_author_articles():
    author = get_one(Author.find_by_name("Alice"))
    articles = author.articles() if callable(author.articles) else author.articles
    assert len(articles) == count("articles", {"author_id": author.id})
    row = get_row("articles")
    assert any(get_value(row, a, "title") == "AI Revolution" for a in articles)

def test_author_magazines():
    if callable(globals().get("Author.find_by_name")):
        author = get_one(Author.find_by_name("Alice"))
    else:
        author = find_by_name(Author, 'authors', "Alice")
    
    mags = author.magazines() if callable(author.magazines) else author.magazines
    row = get_row("magazines")
    names = [get_value(row, m, 'name') for m in mags]
    assert set(names) == {"Tech Times", "Health Weekly"}

def test_author_add_article():
    author = Author(name="Daisy")
    author.save()
    mag = Magazine(name="Science Daily", category="Science")
    mag.save()
    author.add_article(mag, "SpaceX Launch")
    articles = author.articles() if callable(author.articles) else author.articles
    row = get_row("articles")
    assert get_value(row, articles[0],'title') == "SpaceX Launch"

### Magazine Tests ###

def test_magazine_find_by_category():
    mag = get_one(Magazine.find_by_category("Technology"))
    row = get_row("magazines")
    assert get_value(row, mag, "name") == "Tech Times"

def test_magazine_contributors():
    if callable(globals().get("Magazine.find_by_name")):
        mag = get_one(Magazine.find_by_name("Tech Times"))
    else:
        mag = find_by_name(Magazine, 'magazines', "Tech Times")
    authors = mag.contributors() if callable(mag.contributors) else mag.contributors
    row = get_row("authors")
    names = [get_value(row, a, 'name') for a in authors]
    assert set(names) == {"Alice", "Bob"}

def test_magazine_article_titles():
    if callable(globals().get("Magazine.find_by_name")):
        mag = get_one(Magazine.find_by_name("Tech Times"))
    else:
        mag = find_by_name(Magazine, 'magazines', "Tech Times")
    titles = mag.article_titles() if callable(mag.article_titles) else mag.article_titles
    assert set(titles) == {"AI Revolution", "Cybersecurity Tips"}

def test_magazine_contributing_authors():
    if callable(globals().get("Magazine.find_by_name")):
        mag = get_one(Magazine.find_by_name("Tech Times"))
    else:
        mag = find_by_name(Magazine, 'magazines', "Tech Times")
    authors = mag.contributing_authors() if callable(mag.contributing_authors) else mag.contributing_authors
    assert isinstance(authors, list)

### Article Tests ###

def test_article_find_by_title():
    article = get_one(Article.find_by_title("AI Revolution"))
    row = get_row("articles")
    assert get_value(row, article, "title") == "AI Revolution"

### SQL Query Tests ###

def test_magazines_with_multiple_authors():
    mags = Magazine.with_multiple_authors()
    row = get_row("magazines")
    assert any(get_value(row, m, 'name') == "Tech Times" for m in mags)

def test_article_count_per_magazine():
    counts = Magazine.article_counts()
    row = get_row("magazines")
    assert any(get_value(row, c, 'name') == "Tech Times" for i, c in enumerate(counts))

def test_top_author_by_articles():
    top = Author.top_author()
    row = get_row("articles")
    assert get_value(row, top, 'name') == "Alice"

