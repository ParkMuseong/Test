

card_payment_name_vendor_bizs = [
    ('KB국민카드', 'KB국민카드', 'KB국민카드'),
    ('KB카드출금', 'KB국민카드', 'KB국민카드'),
    ('KB카드', 'KB국민카드', 'KB국민카드'),
    ('국민카드', 'KB국민카드', 'KB국민카드'),
    ('현대카드', '현대카드', '현대카드'),
    ('우리카드', '우리카드', '우리카드'),
    ('하나카드', '하나카드', '하나카드'),
    ('신한카드', '신한카드', '신한카드'),
    ('신한카드출금', '신한카드', '신한카드'),
    ('롯데카드', '롯데카드', '롯데카드')
]

def find_card_vendor_biz_name(name):
    # name 이 카드사 명칭과 동일할시..
    for card_pm, card_vendor, biz_name in card_payment_name_vendor_bizs:
        if card_pm == name:
            return card_vendor, biz_name
    return None, None