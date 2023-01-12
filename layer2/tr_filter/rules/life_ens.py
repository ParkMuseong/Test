"""
생명보험 보험료
"""
import re


life_ens_name_map = [
    ("한화생명", "한화생명[0-2]\d-\d{2}", "한화생명보험"),
    ("한화생명", "한화생명\d{5}", "한화생명보험"),
    ("삼성생명", "삼성생명[0-2]\d-\d{2}", "삼성생명보험"),
    ("삼성생명", "삼성생명보헙주식회", "삼성생명보험"),
    ("신한라이프", "신한생명[0-2]\d-\d{2}", "신한라이프생명보험"),
    ("AIA생명", "AIA\d{2}", "에이아이에이생명보험"),
    ("농협생명", "농협생명.+회", "농협생명보험"),
    ("푸본현대생명", "푸본[0-2]\d-\d{3}", "푸본현대생명보험"),
    ("푸본현대생명", "푸본현[0-2]\d-\d{3}", "푸본현대생명보험"),
    ("푸본현대생명", "푸본현대[0-2]\d-\d{3}", "푸본현대생명보험"),
    ("푸르덴셜생명", "푸르\d{5}", "푸르덴셜생명보험"),
    ("동양생명", "동양생명[0-2]\d-\d{3}", "동양생명보험"),
    ("교보생명", "교보[0-2]\d-\d{3}", "교보생명보험"),
    ("교보생명", "교보\d{4}-\d{3}", "교보생명보험")
]
life_ens_name_map = [
    (name, re.compile(reg), biz_name) for (name, reg, biz_name) in life_ens_name_map
]


def find_life_ens(name):
    for life_ens_name, reg, biz_name in life_ens_name_map:
        if reg.match(name):
            return life_ens_name, biz_name
    return None, None


if __name__ == '__main__':
    print(find_life_ens('한화생명11-33'))