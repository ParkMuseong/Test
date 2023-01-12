"""
화재보험 보험료
"""
import re




life_ens_name_map = [
    ('현대해상', '현대해상[0-2]{2}-\d{3}', '현대해상화재보험'),
    ('현대해상', '현대해\d{5}', '현대해상화재보험'),
    ('KB손해보험', 'KB손\d{3}', 'KB손해보험'),
    ('메리츠화재', '메리츠\d{3}건', '메리츠화재해상보험'),
    ('DB손해보험', 'DB손\d{5}', 'DB손해보험'),
    ('롯데손해보험', '롯손\d{5}', '롯데손해보험'),
    ('NH농협손해보험', '농협손보\d{3}', '농협손해보험'),
    ('한화손해보험', '한화손\d{4}', '한화손해보험'),
    ('삼성화재', '삼성화\d{5}', '삼성화재해상보험'),
    ('흥국화재', '흥화\d{5}', '흥국화재해상보험')
]
life_ens_name_map = [
(name, re.compile(reg), biz_name) for (name, reg, biz_name) in life_ens_name_map
]


def find_fire_ins(name):
    for life_ens_name, reg, biz_name in life_ens_name_map:
        if reg.search(name):
            return life_ens_name, biz_name
    return None, None


if __name__ == '__main__':
    print(find_fire_ins('현대해상11-233'))