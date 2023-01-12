"""
ATM 입출금 판별 규칙입니다.
"""
import re

# 패턴 정의
pattern_map = {
    'nice': '^NICE-[A-Za-z0-9]{4}$',
    'hyj': '^HYJ[A-Za-z0-9]{4}$',
    'kbj': '^KBJ[A-Za-z0-9]{4}$',
    'kci': '^KCI[0-9]{4}$',
    'nci': '^NCI[A-Za-z0-9]{4}$',
    'kcj': '^KCJ[0-9]{4}$',
    'kibank': '^KIBank-[A-Za-z0-9]{3}$',
    'hyosung': '^효성-[A-Za-z0-9]{3}$',
    'hannet': '^한네트-[A-Za-z0-9]{3}$',
    'cd_cash': '^[0-9]{3}-[0-9]{4}$',
}
pattern_compiled = {
    key: re.compile(value) for key, value in pattern_map.items()
}


def find(name):
    """
    어떤 타입인지, 리턴 없으면 None
    :param transaction:
    :return:
    """
    for key, pattern in pattern_compiled.items():
        if pattern.match(name):
            return key
    return None
