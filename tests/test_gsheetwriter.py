"""Test the GSheetWriter."""

import pytest


@pytest.fixture
def gspread():
    import gspread
    return gspread


@pytest.fixture
def orig_class():
    """Return the CUT with network access enabled"""
    from agile_analytics import GSheetWriter
    return GSheetWriter


def test_orig_class(orig_class):
    """Ensure the fixture works."""
    assert orig_class.__name__ == "GSheetWriter"


@pytest.fixture
def klass(orig_class, mocker):
    """Return the CUT with some networky bits mocked out."""
    credential_mock_attrs = {
        'from_json_keyfile_name.return_value': "FakeTestCredentials"
    }
    driver_mock_attrs = {
    }
    orig_class.CREDENTIAL_CLASS = mocker.Mock(**credential_mock_attrs)
    orig_class.DRIVER_MODULE = mocker.Mock(**driver_mock_attrs)
    return orig_class


def test_klass_init(klass):
    """Ensure the CUT can be initialized."""
    k = klass('test_secret.json')
    assert k.keyfile_name == 'test_secret.json'


def test_driver(klass):
    """Ensure the driver is initialized properly."""
    k = klass('test_secret.json')

    assert k.driver

    k.CREDENTIAL_CLASS.from_json_keyfile_name.assert_called_once_with(
        'test_secret.json',
        k.scope
    )

    k.DRIVER_MODULE.authorize.assert_called_once_with('FakeTestCredentials')


def test_get_datasheet_happy(klass, mocker):
    """Ensure the get_datasheet method finds existing sheets."""
    k = klass('foo')

    mock_doc = mocker.Mock()
    k.get_datasheet(mock_doc, "Foo")
    mock_doc.worksheet.called_once_with("Foo")
    mock_doc.add_worksheet.assert_not_called()


def test_get_datasheet_exception(klass, mocker, gspread):
    """Ensure get datasheet method creates one if the requested name doesn't exist."""
    k = klass('foo')

    mock_doc_attrs = {
        'worksheet.side_effect': gspread.exceptions.WorksheetNotFound
    }
    mock_doc = mocker.Mock(**mock_doc_attrs)
    k.get_datasheet(mock_doc, "Foo")
    mock_doc.worksheet.called_once_with("Foo")
    mock_doc.add_worksheet.called_once_with("Foo", 1, 1)