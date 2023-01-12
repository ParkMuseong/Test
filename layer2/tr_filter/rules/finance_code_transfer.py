"""
9-1 금융사코드 이체
"""
from layer2.tr_filter.rules import finance_code, human_name
import re


def get_finance_vendor(tr_name):
    # 금융사 코드 형식인지 확인
    if '.' in tr_name:
        tokens = tr_name.split('.')
        if len(tokens) == 2:
            code = tokens[0]
            name = tokens[1]
            if code in finance_code.code_name_map:
                if human_name.contains(name):
                    return finance_code.code_name_map[code]

    if tr_name.startswith('#'):
        for code in finance_code.code_name_map:
            if tr_name.startswith(f'#{code}'):
                _tr_name = tr_name.replace(f'#{code}', '')
                if human_name.contains(_tr_name):
                    return finance_code.code_name_map[code]

    if '-' in tr_name:
        tokens = tr_name.split('-')
        if len(tokens) == 2:
            code = tokens[0]
            name = tokens[1]
            if code in finance_code.code_name_map:
                if human_name.contains(name):
                    return finance_code.code_name_map[code]

    return None
