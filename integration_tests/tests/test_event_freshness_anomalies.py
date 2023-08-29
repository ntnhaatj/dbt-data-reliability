from datetime import datetime, timedelta

from data_generator import DATE_FORMAT, generate_dates
from dbt_project import DbtProject

TEST_NAME = "elementary.event_freshness_anomalies"
EVENT_TIMESTAMP_COLUMN = "event_timestamp"
UPDATE_TIMESTAMP_COLUMN = "update_timestamp"
STEP = timedelta(hours=1)


def test_anomalyless_event_freshness(test_id: str, dbt_project: DbtProject):
    dbt_project.dbt_runner.vars["disable_run_results"] = False
    dbt_project.dbt_runner.vars["disable_tests_results"] = False
    dbt_project.dbt_runner.vars["disable_dbt_invocation_autoupload"] = False
    dbt_project.dbt_runner.vars["disable_dbt_artifacts_autoupload"] = False
    data = [
        {
            EVENT_TIMESTAMP_COLUMN: date.strftime(DATE_FORMAT),
            UPDATE_TIMESTAMP_COLUMN: date.strftime(DATE_FORMAT),
        }
        for date in generate_dates(datetime.now(), step=STEP)
    ]
    result = dbt_project.test(
        test_id,
        TEST_NAME,
        dict(
            event_timestamp_column=EVENT_TIMESTAMP_COLUMN,
            update_timestamp_column=UPDATE_TIMESTAMP_COLUMN,
        ),
        data=data,
    )
    assert result["status"] == "pass"


def test_stop_event_freshness(test_id: str, dbt_project: DbtProject):
    anomaly_date = datetime.now() - timedelta(days=2)
    data = [
        {
            EVENT_TIMESTAMP_COLUMN: date.strftime(DATE_FORMAT),
            UPDATE_TIMESTAMP_COLUMN: date.strftime(DATE_FORMAT),
        }
        for date in generate_dates(anomaly_date, step=STEP)
    ]
    result = dbt_project.test(
        test_id,
        TEST_NAME,
        dict(
            event_timestamp_column=EVENT_TIMESTAMP_COLUMN,
            update_timestamp_column=UPDATE_TIMESTAMP_COLUMN,
        ),
        data=data,
    )
    assert result["status"] == "fail"


def test_slower_rate_event_freshness(test_id: str, dbt_project: DbtProject):
    anomaly_date = datetime.now() - timedelta(days=1)
    data = [
        {
            EVENT_TIMESTAMP_COLUMN: date.strftime(DATE_FORMAT),
            UPDATE_TIMESTAMP_COLUMN: date.strftime(DATE_FORMAT),
        }
        for date in generate_dates(anomaly_date, step=STEP)
    ]
    slow_data = [
        {
            EVENT_TIMESTAMP_COLUMN: date.strftime(DATE_FORMAT),
            UPDATE_TIMESTAMP_COLUMN: (date + STEP).strftime(DATE_FORMAT),
        }
        for date in generate_dates(datetime.now(), step=STEP, days_back=1)
    ]
    data.extend(slow_data)
    result = dbt_project.test(
        test_id,
        TEST_NAME,
        dict(
            event_timestamp_column=EVENT_TIMESTAMP_COLUMN,
            update_timestamp_column=UPDATE_TIMESTAMP_COLUMN,
        ),
        data=data,
    )
    assert result["status"] == "fail"
