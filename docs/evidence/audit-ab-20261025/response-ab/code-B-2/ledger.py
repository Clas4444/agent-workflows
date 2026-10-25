"""Exact ledger summaries using only the standard library."""

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


def _format_cents(total):
    # Decimal construction and formatting avoid integer string digit limits.
    digits = format(Decimal(abs(total)), 'f').zfill(3)
    return ('-' if total < 0 else '') + digits[:-2] + '.' + digits[-2:]


def summarize(rows):
    """Group by category and currency, preserving unknown amounts and IDs."""
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
        if amount is None or (isinstance(amount, str) and not amount.strip()):
            group['missing_ids'].append(row['id'])
            complete = False
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
