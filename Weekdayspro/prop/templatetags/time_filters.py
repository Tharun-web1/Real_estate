from django import template
from django.utils.timezone import now
from datetime import timedelta

register = template.Library()

@register.filter
def custom_time(value):
    if not value:
        return ''
    diff = now() - value
    
    if diff < timedelta(days=7):
        days = diff.days
        if days == 0: return 'Today'
        return f'{days} days ago'
    
    if diff < timedelta(days=30):
        weeks = diff.days // 7
        return f'{weeks} week' + ('s' if weeks > 1 else '') + ' ago'
    
    if diff < timedelta(days=365):
        months = diff.days // 30
        return f'{months} month' + ('s' if months > 1 else '') + ' ago'
    
    years = diff.days // 365
    return f'{years} year' + ('s' if years > 1 else '') + ' ago'

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def indian_price(value):
    """
    Converts a number to Indian price format.
    e.g. 100000 → ₹1 Lakh, 2500000 → ₹25 Lakh, 10000000 → ₹1 Cr
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    if value >= 10_000_000:          # 1 Crore+
        cr = value / 10_000_000
        formatted = f"{cr:.2f}".rstrip('0').rstrip('.')
        return f"₹{formatted} Cr"
    elif value >= 100_000:           # 1 Lakh+
        lakh = value / 100_000
        formatted = f"{lakh:.2f}".rstrip('0').rstrip('.')
        return f"₹{formatted} Lakh"
    elif value >= 1_000:             # 1 Thousand+
        k = value / 1_000
        formatted = f"{k:.2f}".rstrip('0').rstrip('.')
        return f"₹{formatted}K"
    else:
        return f"₹{int(value)}"
