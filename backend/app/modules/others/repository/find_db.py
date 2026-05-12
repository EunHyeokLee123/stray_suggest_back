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
                db.breed_key,
                db.name,
                db.image_link,
                db.energy,
                db.trainability,
                db.protectiveness,
                db.shedding,
                db.barking,
                db.playfulness,
                db.grooming,
                db.drooling,
                db.coat_length,

                db.good_with_other_dogs,
                db.good_with_strangers,

                db.min_life_expectancy,
                db.max_life_expectancy,

                db.min_height_male,
                db.max_height_male,
                db.min_height_female,
                db.max_height_female,

                db.min_weight_male,
                db.max_weight_male,
                db.min_weight_female,
                db.max_weight_female,

                db.life_expectancy,

                db.origin,

                dk.description AS description,
                dk.temperament AS temperament,
                dk.colors AS colors,
                dk.breed_function AS breed_function,
                dk.coat_type AS coat_type,

                db.size_category,
                db.popularity_score,
                db.breed_group,

                db.children_friendly,
                db.apartment_friendly,
                db.novice_owner_friendly,
                db.prey_drive,
                db.exercise_needs,
                db.heat_tolerance,
                db.cold_tolerance,

                db.review_status,
                db.source_registry,
                db.source_url,
                db.reviewed_at,

                di.img

            FROM dog_breeds db

            INNER JOIN dog_image di
                ON db.breed_key = di.breed_key

            LEFT JOIN dog_kr dk
                ON db.breed_key = dk.breed_key

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