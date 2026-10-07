import datetime

TAX = 0.07
member_points = {}
LOG = []


def calc(items, member=None, coupon=None, today=None):
    total = 0

    for item in items:
        quantity = item[1]
        if quantity <= 0:
            continue

        line_total = quantity * item[2]
        if quantity >= 100:
            line_total = line_total * 0.9
        elif quantity >= 50:
            line_total = line_total * 0.95

        total = total + line_total

    if member is not None:
        if member not in member_points:
            member_points[member] = 0

        total = total * 0.95
        member_points[member] = member_points[member] + int(total / 100)

    if coupon is not None:
        if coupon == "SAVE50":
            total = total - 50
        elif coupon == "HALF":
            total = total * 0.5
        elif coupon == "NEWYEAR":
            if today is None:
                today = datetime.date.today()
            if today.month == 1:
                total = total * 0.8

    if total < 0:
        total = 0

    total = total + total * TAX
    total = round(total, 2)
    LOG.append((member, total))
    return total
