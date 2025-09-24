import pytest
from inline_snapshot import snapshot
from mcp.client.session import ClientSession
from mcp.types import TextContent

pytestmark = [pytest.mark.vcr, pytest.mark.anyio]


async def test_schema_reference(session: ClientSession) -> None:
    result = await session.call_tool('schema_reference')

    assert result.content == snapshot(
        [
            TextContent(
                type='text',
                text="""\
CREATE TABLE records (
    attributes TEXT,
    attributes_json_schema TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    day DATE NOT NULL,
    deployment_environment TEXT,
    duration DOUBLE PRECISION,
    end_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    exception_message TEXT,
    exception_stacktrace TEXT,
    exception_type TEXT,
    http_method TEXT,
    http_response_status_code INTEGER,
    http_route TEXT,
    is_exception BOOLEAN,
    kind TEXT NOT NULL,
    level INTEGER NOT NULL,
    log_body TEXT,
    message TEXT NOT NULL,
    otel_events TEXT,
    otel_links TEXT,
    otel_resource_attributes TEXT,
    otel_scope_attributes TEXT,
    otel_scope_name TEXT,
    otel_scope_version TEXT,
    otel_status_code TEXT,
    otel_status_message TEXT,
    parent_span_id TEXT,
    process_pid INTEGER,
    project_id TEXT NOT NULL,
    service_instance_id TEXT,
    service_name TEXT NOT NULL,
    service_namespace TEXT,
    service_version TEXT,
    span_id TEXT NOT NULL,
    span_name TEXT NOT NULL,
    start_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    tags TEXT[],
    telemetry_sdk_language TEXT,
    telemetry_sdk_name TEXT,
    telemetry_sdk_version TEXT,
    trace_id TEXT NOT NULL,
    url_full TEXT,
    url_path TEXT,
    url_query TEXT
);

CREATE TABLE metrics (
    aggregation_temporality TEXT,
    attributes TEXT,
    attributes_json_schema TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    day DATE NOT NULL,
    deployment_environment TEXT,
    exemplars TEXT,
    exp_histogram_negative_bucket_counts INTEGER[],
    exp_histogram_negative_bucket_counts_offset INTEGER,
    exp_histogram_positive_bucket_counts INTEGER[],
    exp_histogram_positive_bucket_counts_offset INTEGER,
    exp_histogram_scale INTEGER,
    exp_histogram_zero_count INTEGER,
    exp_histogram_zero_threshold DOUBLE PRECISION,
    histogram_bucket_counts INTEGER[],
    histogram_count INTEGER,
    histogram_explicit_bounds DOUBLE PRECISION[],
    histogram_max DOUBLE PRECISION,
    histogram_min DOUBLE PRECISION,
    histogram_sum DOUBLE PRECISION,
    is_monotonic BOOLEAN,
    metric_description TEXT,
    metric_name TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    otel_resource_attributes TEXT,
    otel_scope_attributes TEXT,
    otel_scope_name TEXT,
    otel_scope_version TEXT,
    process_pid INTEGER,
    project_id TEXT NOT NULL,
    recorded_timestamp TIMESTAMP WITH TIME ZONE,
    scalar_value DOUBLE PRECISION,
    service_instance_id TEXT,
    service_name TEXT NOT NULL,
    service_namespace TEXT,
    service_version TEXT,
    start_timestamp TIMESTAMP WITH TIME ZONE,
    telemetry_sdk_language TEXT,
    telemetry_sdk_name TEXT,
    telemetry_sdk_version TEXT,
    unit TEXT NOT NULL
);\
""",
            )
        ]
    )
