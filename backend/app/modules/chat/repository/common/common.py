BREED_THRESHOLD = 0.3
MIX_BREED_THRESHOLD = 0.45
COLOR_THRESHOLD = 0.3
MIX_COLOR_THRESHOLD = 0.45
LIMIT_COUNT = 30


COLOR_COLUMN_MAP = {
    "검정색": "black",
    "노란색": "yellow",
    "회색": "gray",
    "흰색": "white",
    "갈색": "brown",
    "주황색": "orange",
}


def normalize_breeds(breed):
    if not breed:
        return []

    if isinstance(breed, list):
        return [b for b in breed if b]

    return [breed]


def get_region(sido):
    region_mapping = {
        "서울": ["서울특별시"],
        "부산": ["부산광역시"],
        "대구": ["대구광역시"],
        "인천": ["인천광역시"],
        "광주": ["광주광역시"],
        "대전": ["대전광역시"],
        "울산": ["울산광역시"],
        "세종": ["세종특별자치시", "세종시"],
        "경기": ["경기도"],
        "강원": ["강원도", "강원특별자치도"],
        "충북": ["충청북도"],
        "충남": ["충청남도"],
        "전북": ["전라북도", "전북특별자치도"],
        "전남": ["전라남도"],
        "경북": ["경상북도"],
        "경남": ["경상남도"],
        "제주": ["제주특별자치도", "제주도"],
    }
    return region_mapping.get(sido, [])


def add_region_condition(where_clauses, values, sido, table_alias="sa"):
    if not sido:
        return

    regions = get_region(sido)

    if not regions:
        return

    placeholders = ", ".join(["%s"] * len(regions))
    where_clauses.append(
        f"SUBSTRING_INDEX({table_alias}.care_addr, ' ', 1) IN ({placeholders})"
    )
    values.extend(regions)


def build_color_condition(colors):
    color_cols = []

    for color in colors:
        col = COLOR_COLUMN_MAP.get(color)
        if col:
            color_cols.append(col)

    if not color_cols:
        return None, None, []

    if len(color_cols) == 1:
        col = color_cols[0]
        return f"c.{col}", f"c.{col} >= %s", [COLOR_THRESHOLD]

    expr = " + ".join([f"c.{col}" for col in color_cols])
    return f"({expr})", f"({expr}) >= %s", [MIX_COLOR_THRESHOLD]