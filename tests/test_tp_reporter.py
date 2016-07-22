"""Test ThroughputReporter"""

import pytest


@pytest.fixture
def klass():
    """Return CUT."""
    from agile_analytics import ThroughputReporter
    return ThroughputReporter


@pytest.fixture
def AnalyzedAgileTicket():
    """Return a class used by the CUT."""
    from agile_analytics.models import AnalyzedAgileTicket
    return AnalyzedAgileTicket


def test_title(klass):
    """Ensure the title gets set."""
    r = klass(
        title="Weekly Throughput"
    )
    assert r.title == "Weekly Throughput"


def test_period(klass):
    """Ensure the period can be set."""
    r = klass(title="Weekly Throughput")
    r.period = "weekly"
    assert r.period == "weekly"


def test_date_assignment(klass, days_ago):
    """Ensure the range can be set."""
    r = klass(title="Weekly Throughput")
    r.start_date = days_ago(30)
    r.end_date = days_ago(0)

    assert r.start_date == days_ago(30)
    assert r.end_date == days_ago(0)


def test_date_range_reconcile(klass, datetime):
    """Ensure the right dates are set when passed two dates and a weekly period arg."""
    r = klass(title="Weekly Throughput")
    r.period = "weekly"
    r.start_date = datetime(2016, 5, 21, 0, 0, 0)
    r.end_date = datetime(2016, 6, 21, 11, 59, 59)

    assert r.start_date == datetime(2016, 5, 15, 0, 0, 0)  # Sunday
    assert r.end_date == datetime(2016, 6, 25, 11, 59, 59)  # Saturday


def test_date_reconcile_post_hoc(klass, datetime):
    """When you set the period after the dates, the dates should be adjusted."""
    r = klass(title="Weekly Throughput")
    r.start_date = datetime(2016, 5, 21, 0, 0, 0)
    r.end_date = datetime(2016, 6, 21, 11, 59, 59)
    r.period = "weekly"

    assert r.start_date == datetime(2016, 5, 15, 0, 0, 0)  # Sunday
    assert r.end_date == datetime(2016, 6, 25, 11, 59, 59)  # Saturday


def test_report_summary(klass, datetime):
    """report_on returns an object with metadata about the report."""
    r = klass(
        title="Weekly Throughput",
        start_date=datetime(2016, 5, 15, 0, 0, 0),
        end_date=datetime(2016, 6, 25, 11, 59, 59),
        period="weekly",
    )

    expected = dict(
        title="Weekly Throughput",
        start_date=datetime(2016, 5, 15, 0, 0, 0),
        end_date=datetime(2016, 6, 25, 11, 59, 59),
        period="weekly",
    )

    report = r.report_on([])
    assert report.summary == expected


def test_report_summary_table(klass, datetime, date, AnalyzedAgileTicket):
    """report_on returns an object with metadata about the report."""
    r = klass(
        title="Weekly Throughput",
        start_date=datetime(2016, 5, 15, 0, 0, 0),
        end_date=datetime(2016, 6, 25, 11, 59, 59),
        period="weekly",
    )

    analyzed_issues = [
        AnalyzedAgileTicket("KEY-1", {}, {}, dict(state="FOO", entered_at=datetime(2016, 5, 16, 0, 0, 0))),
        AnalyzedAgileTicket("KEY-2", {}, {}, dict(state="FOO", entered_at=datetime(2016, 5, 17, 0, 0, 0))),
        AnalyzedAgileTicket("KEY-3", {}, {}, dict(state="FOO", entered_at=datetime(2016, 5, 17, 0, 0, 0))),
        AnalyzedAgileTicket("KEY-4", {}, {}, dict(state="FOO", entered_at=datetime(2016, 5, 20, 0, 0, 0))),
        AnalyzedAgileTicket("KEY-5", {}, {}, dict(state="FOO", entered_at=datetime(2016, 6, 8, 0, 0, 0))),
        AnalyzedAgileTicket("KEY-6", {}, {}, dict(state="FOO", entered_at=datetime(2016, 6, 8, 0, 0, 0))),
        AnalyzedAgileTicket("KEY-7", {}, {}, dict(state="FOO", entered_at=datetime(2016, 6, 8, 0, 0, 0))),
        AnalyzedAgileTicket("KEY-8", {}, {}, dict(state="FOO", entered_at=datetime(2016, 6, 8, 0, 0, 0))),
        AnalyzedAgileTicket("KEY-7", {}, dict(state="FOO", entered_at=datetime(2016, 6, 8, 0, 0, 0)), {}),  # Started, but not finished this week
    ]

    expected = [
        ["Week", "Completed"],
        [date(2016, 5, 15), ],
        [date(2016, 5, 22), ],
        [date(2016, 5, 29), ],
        [date(2016, 6, 5), ],
        [date(2016, 6, 12), ],
        [date(2016, 6, 19), ],
    ]

    report = r.report_on(analyzed_issues)
    assert report.table[0] == expected[0]
    assert len(report.table) == len(expected)

    for i in xrange(0, len(expected)):
        expected_row = expected[i]
        actual_row = report.table[i]
        assert expected_row[0] == actual_row[0]