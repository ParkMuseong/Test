"""
결제 내역이 이체인지 BUY 인지 판단하고
이체일시에는 어떤 이체 분류인지 확인합니다.
"""
import json

from layer2.tr_filter.rules import account_auth, amt_in_out, card_income, card_vendor_name, ef_name, finance_name, \
    finance_code, human_name, openbanking_name, finance_code_transfer, toss_transfer, life_ens, fire_ins

from layer2.tr_filter import rule_types
import re


korean_4 = re.compile('[가-힣]{4}')
number_5gt = re.compile('^\d{4}\d+$')
yello_umb = re.compile('^노란\d{3}$')
sponsor = re.compile('후원금+')


def _make_return(tr_type, target_name=None, target_type=None, target_biz_name=None, target_biz_type=None,
                 target_account_vendor=None, tr_channel=None, tr_target_channel=None):
    """
    :param tr_type: 이체유형
    :param target_name: 이체 상대명
    :param target_type: 이체 상대 분류
    :param target_biz_name: 이체 상대 사업자명
    :param target_biz_type: 이체 상대 사업자 분류
    :param target_account_vendor: 이체 상대 계좌 벤더
    :param tr_channel: 이체 매체
    :param tr_target_channel: 이체 상대 매체
    :return:
    """
    return {
        'tr_type': tr_type,
        'target_name': target_name,
        'target_type': target_type,
        'target_biz_name': target_biz_name,
        'target_biz_type': target_biz_type,
        'target_account_vendor': target_account_vendor,
        'tr_channel': tr_channel,
        'tr_target_channel': tr_target_channel,
    }


def get_trx_type(transaction, user_name):
    """
    결제 내역이 어떤 이체 타입인지 확인합니다.
    :param transaction: {
        name, outbound, inbound
    }
    :param user_name: 사용자의 이름
    :return:
    """
    candidates = []  # 후보 목록
    # transaction 이 어떤 trx 타입인지 확인합니다.
    name = transaction['name']
    outbound = transaction['outbound']
    inbound = transaction['inbound']
    vendor_type = transaction['vendor_type']

    if not name:
        return []

    # "inbound > 0
    # AND [3]카드매출 시트 조건"
    if inbound > 0:
        target_name = card_income.find(name)
        if target_name:
            candidates.append(_make_return(rule_types.card_income, target_name))

    # "inbound > 0
    # AND [2]ATM입출금 시트 조건"
    if inbound > 0 and amt_in_out.find(name):
        candidates.append(_make_return(rule_types.atm_in, tr_target_channel='ATM'))
    # "outbound > 0
    # AND [2]ATM입출금 시트 조건"
    if outbound > 0 and amt_in_out.find(name):
        candidates.append(_make_return(rule_types.atm_out, tr_channel='ATM'))
    # "inbound == 1
    # AND [1]계좌인증 조건"
    if inbound == 1:
        finance_vendor = account_auth.find(name)
        if finance_vendor:
            candidates.append(_make_return(rule_types.account_auth, target_name=finance_vendor))
    # 계좌인증 4글자
    if inbound == 1 and len(name) == 4:
        candidates.append(_make_return(rule_types.account_auth))
    # 계좌인증 4글자. 계좌
    if inbound == 1:
        fv = finance_name.find_finance_vendor(name)
        if fv and re.match(korean_4, name):
            candidates.append(_make_return(rule_types.account_auth, target_name=fv))
    # 송금
    # 개인이체 (이름 3,4 자리)
    h_name = human_name.contains(name)
    if h_name and h_name == name and h_name != user_name and '오픈' not in name:
        candidates.append(_make_return(rule_types.send_money, target_name=h_name, target_type='개인'))

    # 개인이체 본인
    if name == user_name and '오픈' not in name:
        candidates.append(_make_return(rule_types.send_money, target_name=user_name, target_type='개인>본인'))

    # 개인이체 (금융사 명칭)
    fv = finance_name.find_finance_vendor(name)
    if h_name and h_name == name and fv and name != user_name and '오픈' not in name:
        candidates.append(_make_return(rule_types.send_money, h_name, '개인', target_account_vendor=fv))

    # 개인이체 (금융사 명칭, 본인)
    if user_name in name and fv:
        candidates.append(_make_return(rule_types.send_money, h_name, '개인>본인', target_account_vendor=fv))

    # 개인이체 (금융사코드)
    fvc = finance_code_transfer.get_finance_vendor(name)
    if fvc and user_name != h_name and '오픈' not in name:
        candidates.append(_make_return(rule_types.send_money, h_name, '개인', target_account_vendor=fvc))

    # 개인이체 (금융사코드, 본인)
    if fvc and user_name == h_name and '오픈' not in name:
        candidates.append(_make_return(rule_types.send_money, user_name, '개인>본인', target_account_vendor=fvc))

    is_toss = toss_transfer.is_toss(name)
    # 간편이체(개인, 토스, 출금)
    if outbound > 0 and is_toss and h_name != user_name:
        candidates.append(_make_return(rule_types.send_money, h_name, '개인', tr_channel='토스'))
    # 간편이체(개인, 토스, 입금)
    if inbound > 0 and is_toss and h_name != user_name:
        candidates.append(_make_return(rule_types.send_money, h_name, '개인', tr_channel='토스'))

    # 간편이체 (본인, 토스, 출금)
    if outbound > 0 and is_toss and h_name == user_name:
        candidates.append(_make_return(rule_types.send_money, user_name, '개인>본인', tr_channel='토스'))
    # 간편이체 (본인, 토스, 입금)
    if inbound > 0 and is_toss  and h_name == user_name:
        candidates.append(_make_return(rule_types.send_money, user_name, '개인>본인', tr_target_channel='토스'))

    # 대출이자
    if outbound > 0 and '까지의 이자를 납입하셨습니다' in name:
        candidates.append(_make_return(rule_types.interest_payment, target_type='금융', target_biz_type='금융 및 보험업'))

    # 카드대금
    card_vendor, card_vendor_biz = card_vendor_name.find_card_vendor_biz_name(name)
    if outbound > 0 and card_vendor:
        candidates.append(_make_return(rule_types.credit_card_payment,
                                       target_name=card_vendor, target_type='금융>신용카드',
                                       target_biz_name=card_vendor_biz,
                                       target_biz_type='금융 및 보험업>여신 금융업>신용카드 및 할부 금융업'))

    fire_ins_name, fire_ins_biz_name = fire_ins.find_fire_ins(name)
    # 손해보험 보험료 납부
    if outbound > 0 and fire_ins_name and vendor_type == 'bank':
        candidates.append(
            _make_return(rule_types.ensurance, fire_ins_name, '금융>보험>화재보험', fire_ins_biz_name,
                         '금융 및 보험업>손해 및 보증보험업>손해보험업')
        )

    # 노란우산공제
    if outbound > 0 and yello_umb.match(name):
        candidates.append(
            _make_return(rule_types.yellow_umb, target_name='중소기업중앙회', target_type='공공기관',)
        )

    # 생명보험 보험료 납부
    life_ens_name, life_ens_biz_name = life_ens.find_life_ens(name)
    if outbound > 0 and vendor_type == 'bank' and life_ens_name:
        candidates.append(_make_return(rule_types.ensurance, life_ens_name, '금융>보험>생명보험', life_ens_biz_name, "금융 및 보험업>생명보험업>생명보험업"))

    # 아이템매니아 충전
    if outbound > 0 and user_name in name and 'IMI' in name:
        candidates.append(_make_return(rule_types.recharge_prepaid, target_type='개인>본인', target_account_vendor='아이템매니아'))

    # 카카오뱅크 26주 적금
    if name.startswith('26주적금('):
        candidates.append(_make_return(rule_types.kakao_26_week_saving, target_type='개인', target_account_vendor='카카오뱅크'))

    # 카카오뱅크 자유적금
    if name.startswith('자유적금('):
        candidates.append(_make_return(rule_types.kakao_free_saving, target_type='개인', target_account_vendor='카카오뱅크'))

    # 케이뱅크 적금
    if name.startswith('K뱅') and '적금' in name:
        candidates.append(_make_return(rule_types.saving, target_type='개인', target_account_vendor='케이뱅크'))

    # 예금
    if '예금 [만기일:' in name:
        candidates.append(_make_return(rule_types.deposit, target_type='개인'))

    # 주택 청약
    if outbound > 0 and '주택청약' in name and '회차' in name:
        candidates.append(_make_return(rule_types.housing_subscription, user_name, '개인>본인'))

    # 주택청약(금융사코드)
    fn = finance_code.find_fn(name)
    if fn and '.주택청약' in name:
        candidates.append(_make_return(rule_types.housing_subscription, user_name, '개인>본인', target_account_vendor=fn))

    # 카카오페이 내역 처리
    if '카카오페이' == name:
        candidates.append(_make_return(rule_types.recharge_prepaid, user_name, '개인>본인', target_account_vendor='카카오페이'))

    # 네이버페이 내역 처리
    if '네이버페이' == name:
        candidates.append(_make_return(rule_types.recharge_prepaid, user_name, '개인>본인', target_account_vendor='네이버페이'))

    # 급여 처리
    if inbound > 0 and '급여' in name:
        candidates.append(_make_return(rule_types.salary))

    # 입금 내역 이체 처리
    if inbound > 0:
        candidates.append(_make_return(rule_types.income))

    # 긴 숫자 이체 처리
    if not name.startswith('010') and number_5gt.match(name):
        candidates.append(_make_return(rule_types.unk))
        
    # 후원금 이체 처리    
    if outbound > 0 and sponsor.search(str(name)) :
        candidates.append(_make_return(rule_types.sponsorship))

    return candidates

if __name__ == '__main__':
    from layer2.db_api import crud
    trs = crud.query_items('transaction', [])
    results = []
    for idx, tr in enumerate(trs):
        conditions = get_trx_type(tr, '')
        results.append({
            'name': tr['name'],
            'outbound': tr['outbound'],
            'inbound': tr['inbound'],
            'conditions': conditions,
        })
        if idx == 10000:
            break

    with open('results.json', 'w+') as fp:
        json.dump(results, fp)
