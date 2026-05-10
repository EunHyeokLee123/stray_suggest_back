from math import ceil
from app.modules.others.repository.connector.mysql import get_mysql_connection

ANIMAL_SIZE = 6
DETAIL_SIZE = 5

def find_random_stray(kind: str) :
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT
        popfile1,
        desertion_no
        FROM stray_animal
        WHERE up_kind_nm = %s
        AND popfile1 IS NOT NULL
        AND popfile1 != ''
        ORDER BY RAND()
        LIMIT %s;
    """

    if kind == 'dog':
        kind = '개'
    elif kind == 'cat':
        kind = '고양이'
    else :
        return {
            "items": []
        }

    try:

        cursor.execute(sql, [kind, ANIMAL_SIZE,])
        items = cursor.fetchall()

        return {
            "items": items
        }

    finally:
        cursor.close()
        conn.close()

def find_random_detail(kind: str) :
    if kind == "dog":

        data_sql = """
            SELECT
                db.breed_key,
                di.img
            FROM dog_breeds db
            INNER JOIN dog_image di
                ON db.breed_key = di.breed_key
            ORDER BY RAND()
            LIMIT %s
        """

    elif kind == "cat":

        data_sql = """
            SELECT
                cb.name,
                ci.img
            FROM cat_breeds cb
            INNER JOIN cat_image ci
                ON cb.name = ci.breed_key
            ORDER BY RAND()
            LIMIT %s
        """

    else:
        return {
            "items": []
        }

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(data_sql, [DETAIL_SIZE,])
        items = cursor.fetchall()

        return {
            "items": items
        }

    finally:
        cursor.close()
        conn.close()