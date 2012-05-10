import datetime
from django.conf import settings
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.encoding import force_unicode
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.views.generic.base import View
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin
from django.views.generic.list import MultipleObjectMixin, MultipleObjectTemplateResponseMixin

class YearMixin(object):
    year_format = '%Y'
    year = None

    def get_year_format(self):
        """
        Get a year format string in strptime syntax to be used to parse the
        year from url variables.
        """
        return self.year_format

    def get_year(self):
        "Return the year for which this view should display data"
        year = self.year
        if year is None:
            try:
                year = self.kwargs['year']
            except KeyError:
                try:
                    year = self.request.GET['year']
                except KeyError:
                    raise Http404(_(u"No year specified"))
        return year


class MonthMixin(object):
    month_format = '%b'
    month = None

    def get_month_format(self):
        """
        Get a month format string in strptime syntax to be used to parse the
        month from url variables.
        """
        return self.month_format

    def get_month(self):
        "Return the month for which this view should display data"
        month = self.month
        if month is None:
            try:
                month = self.kwargs['month']
            except KeyError:
                try:
                    month = self.request.GET['month']
                except KeyError:
                    raise Http404(_(u"No month specified"))
        return month

    def get_next_month(self, date):
        """
        Get the next valid month.
        """
        # next must be the first day of the next month.
        if date.month == 12:
            next = date.replace(year=date.year + 1, month=1, day=1)
        else:
            next = date.replace(month=date.month + 1, day=1)
        return _get_next_prev_month(self, next, is_previous=False, use_first_day=True)

    def get_previous_month(self, date):
        """
        Get the previous valid month.
        """
        # prev must be the last day of the previous month.
        prev = date.replace(day=1) - datetime.timedelta(days=1)
        return _get_next_prev_month(self, prev, is_previous=True, use_first_day=True)


class DayMixin(object):
    day_format = '%d'
    day = None

    def get_day_format(self):
        """
        Get a day format string in strptime syntax to be used to parse the day
        from url variables.
        """
        return self.day_format

    def get_day(self):
        "Return the day for which this view should display data"
        day = self.day
        if day is None:
            try:
                day = self.kwargs['day']
            except KeyError:
                try:
                    day = self.request.GET['day']
                except KeyError:
                    raise Http404(_(u"No day specified"))
        return day

    def get_next_day(self, date):
        """
        Get the next valid day.
        """
        next = date + datetime.timedelta(days=1)
        return _get_next_prev_month(self, next, is_previous=False, use_first_day=False)

    def get_previous_day(self, date):
        """
        Get the previous valid day.
        """
        prev = date - datetime.timedelta(days=1)
        return _get_next_prev_month(self, prev, is_previous=True, use_first_day=False)


class WeekMixin(object):
    week_format = '%U'
    week = None

    def get_week_format(self):
        """
        Get a week format string in strptime syntax to be used to parse the
        week from url variables.
        """
        return self.week_format

    def get_week(self):
        "Return the week for which this view should display data"
        week = self.week
        if week is None:
            try:
                week = self.kwargs['week']
            except KeyError:
                try:
                    week = self.request.GET['week']
                except KeyError:
                    raise Http404(_(u"No week specified"))
        return week


class DateMixin(object):
    """
    Mixin class for views manipulating date-based data.
    """
    date_field = None
    allow_future = False

    def get_date_field(self):
        """
        Get the name of the date field to be used to filter by.
        """
        if self.date_field is None:
            raise ImproperlyConfigured(u"%s.date_field is required." % self.__class__.__name__)
        return self.date_field

    def get_allow_future(self):
        """
        Returns `True` if the view should be allowed to display objects from
        the future.
        """
        return self.allow_future

    # Note: the following three methods only work in subclasses that also
    # inherit SingleObjectMixin or MultipleObjectMixin.

    @cached_property
    def uses_datetime_field(self):
        """
        Return `True` if the date field is a `DateTimeField` and `False`
        if it's a `DateField`.
        """
        model = self.get_queryset().model if self.model is None else self.model
        field = model._meta.get_field(self.get_date_field())
        return isinstance(field, models.DateTimeField)

    def _make_date_lookup_arg(self, value):
        """
        Convert a date into a datetime when the date field is a DateTimeField.

        When time zone support is enabled, `date` is assumed to be in the
        current time zone, so that displayed items are consistent with the URL.
        """
        if self.uses_datetime_field:
            value = datetime.datetime.combine(value, datetime.time.min)
            if settings.USE_TZ:
                value = timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def _make_single_date_lookup(self, date):
        """
        Get the lookup kwargs for filtering on a single date.

        If the date field is a DateTimeField, we can't just filter on
        date_field=date because that doesn't take the time into account.
        """
        date_field = self.get_date_field()
        if self.uses_datetime_field:
            since = self._make_date_lookup_arg(date)
            until = self._make_date_lookup_arg(date + datetime.timedelta(days=1))
            return {
                '%s__gte' % date_field: since,
                '%s__lt' % date_field: until,
            }
        else:
            # Skip self._make_date_lookup_arg, it's a no-op in this branch.
            return {date_field: date}


class BaseDateListView(MultipleObjectMixin, DateMixin, View):
    """
    Abstract base class for date-based views display a list of objects.
    """
    allow_empty = False

    def get(self, request, *args, **kwargs):
        self.date_list, self.object_list, extra_context = self.get_dated_items()
        context = self.get_context_data(object_list=self.object_list,
                                        date_list=self.date_list)
        context.update(extra_context)
        return self.render_to_response(context)

    def get_dated_items(self):
        """
        Obtain the list of dates and items.
        """
        raise NotImplementedError('A DateView must provide an implementation of get_dated_items()')

    def get_dated_queryset(self, **lookup):
        """
        Get a queryset properly filtered according to `allow_future` and any
        extra lookup kwargs.
        """
        qs = self.get_queryset().filter(**lookup)
        date_field = self.get_date_field()
        allow_future = self.get_allow_future()
        allow_empty = self.get_allow_empty()
        paginate_by = self.get_paginate_by(qs)

        if not allow_future:
            now = timezone.now() if self.uses_datetime_field else datetime.date.today()
            qs = qs.filter(**{'%s__lte' % date_field: now})

        if not allow_empty:
            # When pagination is enabled, it's better to do a cheap query
            # than to load the unpaginated queryset in memory.
            is_empty = not bool(qs) if paginate_by is None else not qs.exists()
            if is_empty:
                raise Http404(_(u"No %(verbose_name_plural)s available") % {
                        'verbose_name_plural': force_unicode(qs.model._meta.verbose_name_plural)
                })

        return qs

    def get_date_list(self, queryset, date_type):
        """
        Get a date list by calling `queryset.dates()`, checking along the way
        for empty lists that aren't allowed.
        """
        date_field = self.get_date_field()
        allow_empty = self.get_allow_empty()

        date_list = queryset.dates(date_field, date_type)[::-1]
        if date_list is not None and not date_list and not allow_empty:
            name = force_unicode(queryset.model._meta.verbose_name_plural)
            raise Http404(_(u"No %(verbose_name_plural)s available") %
                          {'verbose_name_plural': name})

        return date_list


class BaseArchiveIndexView(BaseDateListView):
    """
    Base class for archives of date-based items.

    Requires a response mixin.
    """
    context_object_name = 'latest'

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        qs = self.get_dated_queryset()
        date_list = self.get_date_list(qs, 'year')

        if date_list:
            object_list = qs.order_by('-' + self.get_date_field())
        else:
            object_list = qs.none()

        return (date_list, object_list, {})


class ArchiveIndexView(MultipleObjectTemplateResponseMixin, BaseArchiveIndexView):
    """
    Top-level archive of date-based items.
    """
    template_name_suffix = '_archive'


class BaseYearArchiveView(YearMixin, BaseDateListView):
    """
    List of objects published in a given year.
    """
    make_object_list = False

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        year = self.get_year()

        date_field = self.get_date_field()
        date = _date_from_string(year, self.get_year_format())

        since = self._make_date_lookup_arg(date)
        until = self._make_date_lookup_arg(datetime.date(date.year + 1, 1, 1))
        lookup_kwargs = {
            '%s__gte' % date_field: since,
            '%s__lt' % date_field: until,
        }

        qs = self.get_dated_queryset(**lookup_kwargs)
        date_list = self.get_date_list(qs, 'month')

        if self.get_make_object_list():
            object_list = qs.order_by('-' + date_field)
        else:
            # We need this to be a queryset since parent classes introspect it
            # to find information about the model.
            object_list = qs.none()

        return (date_list, object_list, {'year': year})

    def get_make_object_list(self):
        """
        Return `True` if this view should contain the full list of objects in
        the given year.
        """
        return self.make_object_list


class YearArchiveView(MultipleObjectTemplateResponseMixin, BaseYearArchiveView):
    """
    List of objects published in a given year.
    """
    template_name_suffix = '_archive_year'


class BaseMonthArchiveView(YearMixin, MonthMixin, BaseDateListView):
    """
    List of objects published in a given year.
    """
    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        year = self.get_year()
        month = self.get_month()

        date_field = self.get_date_field()
        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format())

        # Construct a date-range lookup.
        since = self._make_date_lookup_arg(date)
        if date.month == 12:
            until = self._make_date_lookup_arg(datetime.date(date.year + 1, 1, 1))
        else:
            until = self._make_date_lookup_arg(datetime.date(date.year, date.month + 1, 1))
        lookup_kwargs = {
            '%s__gte' % date_field: since,
            '%s__lt' % date_field: until,
        }

        qs = self.get_dated_queryset(**lookup_kwargs)
        date_list = self.get_date_list(qs, 'day')

        return (date_list, qs, {
            'month': date,
            'next_month': self.get_next_month(date),
            'previous_month': self.get_previous_month(date),
        })


class MonthArchiveView(MultipleObjectTemplateResponseMixin, BaseMonthArchiveView):
    """
    List of objects published in a given year.
    """
    template_name_suffix = '_archive_month'


class BaseWeekArchiveView(YearMixin, WeekMixin, BaseDateListView):
    """
    List of objects published in a given week.
    """

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        year = self.get_year()
        week = self.get_week()

        date_field = self.get_date_field()
        week_format = self.get_week_format()
        week_start = {
            '%W': '1',
            '%U': '0',
        }[week_format]
        date = _date_from_string(year, self.get_year_format(),
                                 week_start, '%w',
                                 week, week_format)

        # Construct a date-range lookup.
        since = self._make_date_lookup_arg(date)
        until = self._make_date_lookup_arg(date + datetime.timedelta(days=7))
        lookup_kwargs = {
            '%s__gte' % date_field: since,
            '%s__lt' % date_field: until,
        }

        qs = self.get_dated_queryset(**lookup_kwargs)

        return (None, qs, {'week': date})


class WeekArchiveView(MultipleObjectTemplateResponseMixin, BaseWeekArchiveView):
    """
    List of objects published in a given week.
    """
    template_name_suffix = '_archive_week'


class BaseDayArchiveView(YearMixin, MonthMixin, DayMixin, BaseDateListView):
    """
    List of objects published on a given day.
    """
    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()

        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format(),
                                 day, self.get_day_format())

        return self._get_dated_items(date)

    def _get_dated_items(self, date):
        """
        Do the actual heavy lifting of getting the dated items; this accepts a
        date object so that TodayArchiveView can be trivial.
        """
        lookup_kwargs = self._make_single_date_lookup(date)
        qs = self.get_dated_queryset(**lookup_kwargs)

        return (None, qs, {
            'day': date,
            'previous_day': self.get_previous_day(date),
            'next_day': self.get_next_day(date),
            'previous_month': self.get_previous_month(date),
            'next_month': self.get_next_month(date)
        })


class DayArchiveView(MultipleObjectTemplateResponseMixin, BaseDayArchiveView):
    """
    List of objects published on a given day.
    """
    template_name_suffix = "_archive_day"


class BaseTodayArchiveView(BaseDayArchiveView):
    """
    List of objects published today.
    """

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        return self._get_dated_items(datetime.date.today())


class TodayArchiveView(MultipleObjectTemplateResponseMixin, BaseTodayArchiveView):
    """
    List of objects published today.
    """
    template_name_suffix = "_archive_day"


class BaseDateDetailView(YearMixin, MonthMixin, DayMixin, DateMixin, BaseDetailView):
    """
    Detail view of a single object on a single date; this differs from the
    standard DetailView by accepting a year/month/day in the URL.
    """
    def get_object(self, queryset=None):
        """
        Get the object this request displays.
        """
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format(),
                                 day, self.get_day_format())

        # Use a custom queryset if provided
        qs = queryset or self.get_queryset()

        if not self.get_allow_future() and date > datetime.date.today():
            raise Http404(_(u"Future %(verbose_name_plural)s not available because %(class_name)s.allow_future is False.") % {
                'verbose_name_plural': qs.model._meta.verbose_name_plural,
                'class_name': self.__class__.__name__,
            })

        # Filter down a queryset from self.queryset using the date from the
        # URL. This'll get passed as the queryset to DetailView.get_object,
        # which'll handle the 404
        lookup_kwargs = self._make_single_date_lookup(date)
        qs = qs.filter(**lookup_kwargs)

        return super(BaseDetailView, self).get_object(queryset=qs)


class DateDetailView(SingleObjectTemplateResponseMixin, BaseDateDetailView):
    """
    Detail view of a single object on a single date; this differs from the
    standard DetailView by accepting a year/month/day in the URL.
    """
    template_name_suffix = '_detail'


def _date_from_string(year, year_format, month='', month_format='', day='', day_format='', delim='__'):
    """
    Helper: get a datetime.date object given a format string and a year,
    month, and day (only year is mandatory). Raise a 404 for an invalid date.
    """
    format = delim.join((year_format, month_format, day_format))
    datestr = delim.join((year, month, day))
    try:
        return datetime.datetime.strptime(datestr, format).date()
    except ValueError:
        raise Http404(_(u"Invalid date string '%(datestr)s' given format '%(format)s'") % {
            'datestr': datestr,
            'format': format,
        })


def _get_next_prev_month(generic_view, naive_result, is_previous, use_first_day):
    """
    Helper: Get the next or the previous valid date. The idea is to allow
    links on month/day views to never be 404s by never providing a date
    that'll be invalid for the given view.

    This is a bit complicated since it handles both next and previous months
    and days (for MonthArchiveView and DayArchiveView); hence the coupling to generic_view.

    However in essence the logic comes down to:

        * If allow_empty and allow_future are both true, this is easy: just
          return the naive result (just the next/previous day or month,
          reguardless of object existence.)

        * If allow_empty is true, allow_future is false, and the naive month
          isn't in the future, then return it; otherwise return None.

        * If allow_empty is false and allow_future is true, return the next
          date *that contains a valid object*, even if it's in the future. If
          there are no next objects, return None.

        * If allow_empty is false and allow_future is false, return the next
          date that contains a valid object. If that date is in the future, or
          if there are no next objects, return None.

    """
    date_field = generic_view.get_date_field()
    allow_empty = generic_view.get_allow_empty()
    allow_future = generic_view.get_allow_future()

    # If allow_empty is True the naive value will be valid
    if allow_empty:
        result = naive_result

    # Otherwise, we'll need to go to the database to look for an object
    # whose date_field is at least (greater than/less than) the given
    # naive result
    else:
        # Construct a lookup and an ordering depending on whether we're doing
        # a previous date or a next date lookup.
        if is_previous:
            lookup = {'%s__lte' % date_field: generic_view._make_date_lookup_arg(naive_result)}
            ordering = '-%s' % date_field
        else:
            lookup = {'%s__gte' % date_field: generic_view._make_date_lookup_arg(naive_result)}
            ordering = date_field

        qs = generic_view.get_queryset().filter(**lookup).order_by(ordering)

        # Snag the first object from the queryset; if it doesn't exist that
        # means there's no next/previous link available.
        try:
            result = getattr(qs[0], date_field)
        except IndexError:
            result = None

    # Convert datetimes to a dates
    if result and generic_view.uses_datetime_field:
        if settings.USE_TZ:
            result = timezone.localtime(result)
        result = result.date()

    # For month views, we always want to have a date that's the first of the
    # month for consistency's sake.
    if result and use_first_day:
        result = result.replace(day=1)

    # Check against future dates.
    if result and (allow_future or result < datetime.date.today()):
        return result
    else:
        return None