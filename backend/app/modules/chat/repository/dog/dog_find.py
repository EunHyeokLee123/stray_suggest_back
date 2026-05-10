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

DOG_COLUMNS = [
    "beagle", "bichon_frise", "border_collie", "boston_bull", "chihuahua",
    "chow", "cocker_spaniel", "dachshund", "french_bulldog",
    "german_shepherd", "golden_retriever", "italian_greyhound", "jindo_dog",
    "labrador_retriever", "maltese_dog", "papillon", "pekinese",
    "pomeranian", "poodle", "pug", "samoyed", "schnauzer", "shiba_inu",
    "shih_tzu", "siberian_husky", "welsh_corgi", "yorkshire_terrier",
    "other",
]


DOG_KIND_NM_MAP = {
    "beagle": ["비글"],
    "bichon_frise": ["비숑", "비숑프리제", "비숑 프리제"],
    "border_collie": ["보더콜리", "보더 콜리"],
    "boston_bull": ["보스턴불", "보스턴 불", "보스턴테리어", "보스턴 테리어"],
    "chihuahua": ["치와와"],
    "chow": ["차우", "차우차우", "차우 차우"],
    "cocker_spaniel": ["코커스패니얼", "코커 스패니얼", "코카스파니엘", "코카 스파니엘"],
    "dachshund": ["닥스훈트", "닥스 훈트"],
    "french_bulldog": ["프렌치불독", "프렌치 불독"],
    "german_shepherd": ["저먼셰퍼드", "저먼 셰퍼드", "셰퍼드", "쉐퍼드"],
    "golden_retriever": ["골든리트리버", "골든 리트리버"],
    "italian_greyhound": ["이탈리안그레이하운드", "이탈리안 그레이하운드"],
    "jindo_dog": ["진돗개", "진도개", "진도견"],
    "labrador_retriever": ["라브라도리트리버", "라브라도 리트리버", "래브라도리트리버", "래브라도 리트리버"],
    "maltese_dog": ["말티즈", "몰티즈"],
    "papillon": ["파피용", "빠삐용"],
    "pekinese": ["페키니즈", "페키니스"],
    "pomeranian": ["포메라니안", "포메"],
    "poodle": ["푸들", "토이푸들", "토이 푸들", "미니푸들", "미니 푸들"],
    "pug": ["퍼그"],
    "samoyed": ["사모예드"],
    "schnauzer": ["슈나우저", "미니어처슈나우저", "미니어처 슈나우저"],
    "shiba_inu": ["시바견", "시바이누", "시바 이누", "시바"],
    "shih_tzu": ["시츄", "시추", "시추견"],
    "siberian_husky": ["시베리안허스키", "시베리안 허스키", "허스키"],
    "welsh_corgi": ["웰시코기", "웰시 코기"],
    "yorkshire_terrier": ["요크셔테리어", "요크셔 테리어", "요키"],
}


def validate_dog_breeds(breeds):
    return [breed for breed in breeds if breed in DOG_COLUMNS]


def search_dogs(filters: dict):
    kind = "개"
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

            if direct_breed != "other":
                candidates = DOG_KIND_NM_MAP.get(direct_breed, []).copy()

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

        breeds = validate_dog_breeds(breeds)

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
            INNER JOIN dog_kind bk
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