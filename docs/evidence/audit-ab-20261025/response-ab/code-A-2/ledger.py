"""Exact, currency-specific ledger summaries."""

from decimal import Decimal


def _cents(amount):
    value = Decimal(amount)
    sign, digits, exponent = value.as_tuple()
    coefficient = 0
    for digit in digits:
        coefficient = coefficient * 10 + digit
    shift = exponent + 2
    if shift >= 0:
        coefficient *= 10 ** shift
    else:
        coefficient //= 10 ** (-shift)
    return -coefficient if sign else coefficient


def _integer_string(value):
    # Small chunks avoid Python's limit on converting enormous integers to text.
    if value == 0:
        return '0'
    chunks = []
    while value:
        value, remainder = divmod(value, 1000000000)
        chunks.append(remainder)
    return str(chunks[-1]) + ''.join(
        f'{chunk:09d}' for chunk in reversed(chunks[:-1])
    )


def _format_cents(value):
    sign = '-' if value < 0 else ''
    whole, fraction = divmod(abs(value), 100)
    return f'{sign}{_integer_string(whole)}.{fraction:02d}'


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
        if amount is None or amount == '':
            complete = False
            group['missing_ids'].append(row['id'])
        else:
            group['total'] += _cents(amount)
            group['has_known'] = True

    return {
        'row_count': row_count,
        'complete': complete,
        'groups': [
            {
                'category': category,
                'currency': currency,
                'known_total': (
                    _format_cents(groups[(category, currency)]['total'])
                    if groups[(category, currency)]['has_known'] else None
                ),
                'missing_ids': groups[(category, currency)]['missing_ids'],
            }
            for category, currency in sorted(groups)
        ],
    }
