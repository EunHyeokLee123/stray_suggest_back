from llm.chat import extract_filters
from llm.google import extract_filters_google

is_google = True

user_text = "대전에 사는 하얀색 페르시안"

def getFilters(user_text = str) :
    # 🔥 여기 분기 추가
    if is_google:
        filters = extract_filters_google(user_text, use_llm=True, verbose=True)
    else:
        filters = extract_filters(user_text, use_llm=True, verbose=True)

    print(filters)

    return filters


# 🔥 여기 분기 추가
if is_google:
    filters = extract_filters_google(user_text, use_llm=True, verbose=True)
else:
    filters = extract_filters(user_text, use_llm=True, verbose=True)

print(filters)

