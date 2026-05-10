from math import ceil
from app.modules.others.repository.connector.mysql import get_mysql_connection


PAGE_SIZE = 9


def find_breeds_by_page(kind: str, page: int):
    offset = (page - 1) * PAGE_SIZE

    if kind == "dog":
        count_sql = """
            SELECT COUNT(*) AS total
            FROM dog_breeds db
            INNER JOIN dog_image di
                ON db.breed_key = di.breed_key
        """

        data_sql = """
            SELECT
                db.breed_key,
                di.img
            FROM dog_breeds db
            INNER JOIN dog_image di
                ON db.breed_key = di.breed_key
            ORDER BY db.breed_key ASC
            LIMIT %s OFFSET %s
        """

    elif kind == "cat":
        count_sql = """
            SELECT COUNT(*) AS total
            FROM cat_breeds cb
            INNER JOIN cat_image ci
                ON cb.name = ci.breed_key
        """

        data_sql = """
            SELECT
                cb.name,
                ci.img
            FROM cat_breeds cb
            INNER JOIN cat_image ci
                ON cb.name = ci.breed_key
            ORDER BY cb.name ASC
            LIMIT %s OFFSET %s
        """

    else:
        return {
            "total_items": 0,
            "items": []
        }

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(count_sql)
        total_items = cursor.fetchone()["total"]

        cursor.execute(data_sql, [PAGE_SIZE, offset])
        items = cursor.fetchall()

        return {
            "total_items": total_items,
            "items": items
        }

    finally:
        cursor.close()
        conn.close()


def find_breed_detail(kind: str, mapped_breed: str):
    if kind == "dog":
        sql = """
            SELECT
                db.*,
                di.img
            FROM dog_breeds db
            INNER JOIN dog_image di
                ON db.breed_key = di.breed_key
	        WHERE db.breed_key = %s
            LIMIT 1
        """

    elif kind == "cat":
        sql = """
            SELECT
                cb.*,
                ci.img
            FROM cat_breeds cb
            INNER JOIN cat_image ci
                ON cb.name = ci.breed_key
                WHERE cb.name = %s    
            LIMIT 1
        """

    else:
        return None

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(sql, [mapped_breed])
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()