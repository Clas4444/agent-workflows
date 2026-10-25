"""Summarize ledger rows without modifying them."""
from decimal import Decimal


def _cents(amount):
    value = Decimal(amount)
    sign, digits, exponent = value.as_tuple()
    coefficient = 0
    for digit in digits:
        coefficient = coefficient * 10 + digit
    scale = exponent + 2
    if scale >= 0:
        coefficient *= 10 ** scale
    else:
        coefficient //= 10 ** (-scale)
    return -coefficient if sign else coefficient


def _format_cents(value):
    sign = '-' if value < 0 else ''
    whole, fraction = divmod(abs(value), 100)
    # Small chunks avoid Python's integer-to-string digit limit.
    chunks = []
    while whole:
        whole, chunk = divmod(whole, 1000000000)
        chunks.append(chunk)
    if chunks:
        integer = str(chunks.pop())
        integer += ''.join(f'{chunk:09d}' for chunk in reversed(chunks))
    else:
        integer = '0'
    return f'{sign}{integer}.{fraction:02d}'


def summarize(rows):
    groups = {}
    row_count = 0
    complete = True
    for row in rows:
        row_count += 1
        key = (row['category'], row['currency'])
        if key not in groups:
            groups[key] = {'total': 0, 'has_known': False, 'missing_ids': []}
        group = groups[key]
        amount = row['amount']
        if amount == '' or amount is None:
            group['missing_ids'].append(row['id'])
            complete = False
        else:
            group['total'] += _cents(amount)
            group['has_known'] = True
    result = []
    for category, currency in sorted(groups):
        group = groups[(category, currency)]
        result.append({
            'category': category,
            'currency': currency,
            'known_total': _format_cents(group['total']) if group['has_known'] else None,
            'missing_ids': group['missing_ids'],
        })
    return {'row_count': row_count, 'complete': complete, 'groups': result}
