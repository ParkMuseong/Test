"""
[11] 토스이체
"""
from layer2.tr_filter.rules import human_name


def is_toss(tr_name):
    words = ['토스_', '토스 ', '토스', '토스　']
    for word in words:
        if word in tr_name:
            _tr_name = tr_name.replace(word, '')
            if human_name.contains(_tr_name):
                return True
    return False
