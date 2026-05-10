from app.modules.chat.repository.connector.mysql import get_mysql_connection
from app.modules.chat.repository.common.common import (
    BREED_THRESHOLD,
    MIX_BREED_THRESHOLD,
    LIMIT_COUNT,
    normalize_breeds,
    add_region_condition,
    build_color_condition,
)
from app.modules.chat.service.breed_info import _find_requested_breed


CAT_COLUMNS = [
    "abyssinian", "american_shorthair", "bengal", "birman", "bombay",
    "british_shorthair", "cornish_rex", "devon_rex", "domestic",
    "maine_coon", "munchkin", "norwegian_forest_cat", "others",
    "persian", "ragdoll", "russian_blue", "scottish_fold", "siamese",
    "sphynx", "turkish_angora", "turkish_van",
]


CAT_KIND_NM_MAP = {
    "abyssinian": ["아비시니안"],
    "american_shorthair": ["아메리칸숏헤어", "아메리칸 숏헤어", "아메숏"],
    "bengal": ["벵갈"],
    "birman": ["버먼"],
    "bombay": ["봄베이"],
    "british_shorthair": ["브리티시숏헤어", "브리티시 숏헤어", "브숏"],
    "cornish_rex": ["코니시렉스", "코니시 렉스"],
    "devon_rex": ["데본렉스", "데본 렉스"],
    "domestic": ["코숏", "코리안숏헤어", "코리안 숏헤어", "도메스틱", "집고양이"],
    "maine_coon": ["메인쿤", "메인 쿤"],
    "munchkin": ["먼치킨"],
    "norwegian_forest_cat": ["노르웨이숲", "노르웨이 숲", "노르웨이숲고양이", "노르웨이 숲 고양이"],
    "persian": ["페르시안"],
    "ragdoll": ["랙돌", "렉돌"],
    "russian_blue": ["러시안블루", "러시안 블루"],
    "scottish_fold": ["스코티시폴드", "스코티시 폴드"],
    "siamese": ["샴", "샴고양이", "샴 고양이"],
    "sphynx": ["스핑크스"],
    "turkish_angora": ["터키쉬앙고라", "터키쉬 앙고라", "터키시앙고라", "터키시 앙고라"],
    "turkish_van": ["터키쉬반", "터키쉬 반", "터키시반", "터키시 반"],
}


def validate_cat_breeds(breeds):
    return [breed for breed in breeds if breed in CAT_COLUMNS]


def search_cats(filters: dict):
    kind = "고양이"
    sido = filters.get("sido")
    breeds = normalize_breeds(filters.get("breed"))
    colors = filters.get("colors") or []

    temp = _find_requested_breed(filters.get("origin"), filters)
    original = temp.get("requested_breed_name") if temp else None

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        direct_results = []

        if len(breeds) == 1:
            direct_breed = breeds[0]

            if direct_breed != "others":
                candidates = CAT_KIND_NM_MAP.get(direct_breed, [])

                if original:
                    candidates.append(original)

                candidates = list(set(candidates))

                direct_where = ["sa.up_kind_nm = %s"]
                direct_values = [kind]

                if candidates:
                    placeholders = ", ".join(["%s"] * len(candidates))
                    direct_where.append(f"sa.kind_nm IN ({placeholders})")
                    direct_values.extend(candidates)
                else:
                    direct_where.append("sa.kind_nm = %s")
                    direct_values.append(direct_breed)

                add_region_condition(direct_where, direct_values, sido)

                direct_sql = f"""
                    SELECT sa.*
                    FROM stray_animal sa
                    WHERE {" AND ".join(direct_where)}
                    ORDER BY sa.desertion_no DESC
                    LIMIT %s
                """

                direct_values.append(LIMIT_COUNT)
                cursor.execute(direct_sql, direct_values)
                direct_results = cursor.fetchall()

        breeds = validate_cat_breeds(breeds)

        where_clauses = ["sa.up_kind_nm = %s"]
        values = [kind]

        if not breeds:
            breed_score_expr = "0"
        elif len(breeds) == 1:
            breed_col = breeds[0]
            breed_score_expr = f"bk.{breed_col}"
            where_clauses.append(f"bk.{breed_col} >= %s")
            values.append(BREED_THRESHOLD)
        else:
            breed_score_expr = " + ".join([f"bk.{breed}" for breed in breeds])
            breed_score_expr = f"({breed_score_expr})"
            where_clauses.append(f"{breed_score_expr} >= %s")
            values.append(MIX_BREED_THRESHOLD)

        color_score_expr, color_condition, color_values = build_color_condition(colors)

        if color_score_expr is None:
            color_score_expr = "0"
        else:
            where_clauses.append(color_condition)
            values.extend(color_values)

        add_region_condition(where_clauses, values, sido)

        model_sql = f"""
            SELECT
                sa.*,
                {breed_score_expr} AS breed_score,
                {color_score_expr} AS color_score,
                ({breed_score_expr} + {color_score_expr}) AS total_score
            FROM stray_animal sa
            INNER JOIN cat_kind bk
                ON sa.desertion_no = bk.desertion_no
            INNER JOIN color c
                ON sa.desertion_no = c.desertion_no
            WHERE {" AND ".join(where_clauses)}
            ORDER BY
                total_score DESC,
                breed_score DESC,
                color_score DESC,
                sa.desertion_no DESC
            LIMIT %s
        """

        values.append(LIMIT_COUNT)
        cursor.execute(model_sql, values)
        model_results = cursor.fetchall()

        return {
            "direct_results": direct_results,
            "model_results": model_results,
        }

    finally:
        cursor.close()
        conn.close()