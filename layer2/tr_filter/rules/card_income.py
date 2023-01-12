"""
카드 매출 판별 규칙입니다.
"""
import re


# 패턴 정의
pattern_map = {
    'kb': ['^KB[0-9]{7,9}$'],
    'hana': ['^하나[0-9]{7,9}$'],
    'lotte': ['^롯데[0-9]{7, 10}$'],
    'sinhan': ['^SHC[0-9]{7,9}$', '^신한[0-9]{7,10}$'],
    'samsung': ['^삼성[0-9]{7,9}$'],
}
pattern_compiled = {
    key: [re.compile(v) for v in value] for key, value in pattern_map.items()
}


def find(name):
    """
    어떤 타입인지, 리턴 없으면 None
    :param transaction:
    :return:
    """
    for key, patterns in pattern_compiled.items():
        for pattern in patterns:
            if pattern.match(name):
                return key
    return None
