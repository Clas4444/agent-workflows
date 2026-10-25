from decimal import Decimal


def _cents(amount):
    parts = Decimal(amount).as_tuple()
    value = 0
    for digit in parts.digits:
        value = value * 10 + digit
    scale = parts.exponent + 2
    if scale >= 0:
        value *= 10 ** scale
    else:
        value //= 10 ** (-scale)
    return -value if parts.sign else value


def _format_cents(value):
    sign = '-' if value < 0 else ''
    whole, fraction = divmod(abs(value), 100)
    # Small chunks avoid Python's limit on converting huge integers to strings.
    chunks = []
    while whole >= 1000000000:
        whole, chunk = divmod(whole, 1000000000)
        chunks.append(f'{chunk:09d}')
    digits = str(whole) + ''.join(reversed(chunks))
    return f'{sign}{digits}.{fraction:02d}'


def summarize(rows):
    groups = {}
    row_count = 0
    complete = True
    for row in rows:
        row_count += 1
        key = (row['category'], row['currency'])
        if key not in groups:
            groups[key] = {'total': 0, 'known': False, 'missing_ids': []}
        group = groups[key]
        amount = row['amount']
        if amount is None or (isinstance(amount, str) and not amount.strip()):
            group['missing_ids'].append(row['id'])
            complete = False
        else:
            group['total'] += _cents(amount)
            group['known'] = True

    return {
        'row_count': row_count,
        'complete': complete,
        'groups': [
            {
                'category': category,
                'currency': currency,
                'known_total': _format_cents(group['total']) if group['known'] else None,
                'missing_ids': group['missing_ids'],
            }
            for (category, currency), group in sorted(groups.items())
        ],
    }
