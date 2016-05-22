import datetime

from django import template

register = template.Library()


@register.filter
def elapsed(duration):
    if isinstance(duration, datetime.timedelta):
        duration = int(duration.total_seconds())
    rem, secs = divmod(duration, 60)
    return "{}:{:02d}".format(rem, secs)


@register.simple_tag
def enum_value(member, attr):
    # Don't ask, don't tell. Yet another Django Mystery™.
    return getattr(member.value, attr)
