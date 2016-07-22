"""Make reports from data."""

from collections import namedtuple
from datetime import date

from dateutil.relativedelta import relativedelta

Report = namedtuple("Report", ["table", "summary"])


class ThroughputReporter(object):
    """Generate throughput reports.

    Attributes:
        title (unicode): The name of the report
        period (unicode): The interval you'd like, one of daily, weekly, monthly,
        start_date (datetime): The starting range of the report.
        end_date (datetime): The ending range of the report.
    """

    def __init__(self, title, period=None, start_date=None, end_date=None):
        self.title = title
        self.period = period
        self.start_date = start_date
        self.end_date = end_date
        object.__init__(self)

    @property
    def start_date(self):
        return self.valid_start_date(self._start_date, self.period)

    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def end_date(self):
        return self.valid_end_date(self._end_date, self.period)

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    def valid_start_date(self, target_date, period):
        if period == "weekly" and target_date.weekday() != 6:
            # Walk back to a Sunday
            while target_date.weekday() != 6:
                target_date = target_date - relativedelta(days=1)

        return target_date

    def valid_end_date(self, target_date, period):
        if period == "weekly" and target_date.weekday() != 5:
            # Walk forward to a Saturday
            while target_date.weekday() != 5:
                target_date = target_date + relativedelta(days=1)

        return target_date

    def starts_of_weeks(self):
        start = self.start_date
        end = self.end_date
        week_starting = date(start.year, start.month, start.day)
        while week_starting <= date(end.year, end.month, end.day):
            yield week_starting
            week_starting += relativedelta(days=7)

    def _count_by_week(self, issues):
        counted_by_week = {}
        for week_starting in self.starts_of_weeks():
            counted_by_week[week_starting] = 0

        return counted_by_week

    def filter_issues(self, issues):
        filtered_issues = [i for i in issues if i.ended and (i.ended['entered_at'] >= self.start_date and i.ended['entered_at'] <= self.end_date)]
        return filtered_issues

    def report_on(self, issues):
        r = Report(
            table=[],
            summary=dict(
                title=self.title,
                period=self.period,
                start_date=self.start_date,
                end_date=self.end_date
            )
        )
        r.table.append(["Week", "Completed"])
        filtered_issues = self.filter_issues(issues)
        counted_by_week = self._count_by_week(filtered_issues)

        weeks = counted_by_week.keys()
        weeks.sort()
        for week in weeks:
            r.table.append([week, counted_by_week[week]])

        return r