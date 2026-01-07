import logging
import time
from typing import Dict, Optional
from urllib.parse import urlparse

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.exceptions import BotoCoreError, NoCredentialsError
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
import requests

try:
    import snappy  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    snappy = None

logger = logging.getLogger(__name__)


def _build_descriptor_pool() -> descriptor_pool.DescriptorPool:
    file_descriptor = descriptor_pb2.FileDescriptorProto()
    file_descriptor.name = "prometheus_remote_write.proto"
    file_descriptor.package = "prometheus"
    file_descriptor.syntax = "proto3"

    write_request = file_descriptor.message_type.add()
    write_request.name = "WriteRequest"
    field = write_request.field.add()
    field.name = "timeseries"
    field.number = 1
    field.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
    field.type = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
    field.type_name = ".prometheus.TimeSeries"

    time_series = file_descriptor.message_type.add()
    time_series.name = "TimeSeries"
    field = time_series.field.add()
    field.name = "labels"
    field.number = 1
    field.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
    field.type = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
    field.type_name = ".prometheus.Label"
    field = time_series.field.add()
    field.name = "samples"
    field.number = 2
    field.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
    field.type = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
    field.type_name = ".prometheus.Sample"

    label = file_descriptor.message_type.add()
    label.name = "Label"
    field = label.field.add()
    field.name = "name"
    field.number = 1
    field.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    field.type = descriptor_pb2.FieldDescriptorProto.TYPE_STRING
    field = label.field.add()
    field.name = "value"
    field.number = 2
    field.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    field.type = descriptor_pb2.FieldDescriptorProto.TYPE_STRING

    sample = file_descriptor.message_type.add()
    sample.name = "Sample"
    field = sample.field.add()
    field.name = "value"
    field.number = 1
    field.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    field.type = descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE
    field = sample.field.add()
    field.name = "timestamp"
    field.number = 2
    field.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    field.type = descriptor_pb2.FieldDescriptorProto.TYPE_INT64

    pool = descriptor_pool.DescriptorPool()
    pool.Add(file_descriptor)
    return pool


_DESCRIPTOR_POOL = _build_descriptor_pool()
_MESSAGE_FACTORY = message_factory.MessageFactory(_DESCRIPTOR_POOL)
_WRITE_REQUEST_CLASS = _MESSAGE_FACTORY.GetPrototype(
    _DESCRIPTOR_POOL.FindMessageTypeByName("prometheus.WriteRequest")
)


def _infer_region(remote_write_url: str) -> Optional[str]:
    hostname = urlparse(remote_write_url).hostname
    if not hostname:
        return None

    parts = hostname.split(".")
    for idx, part in enumerate(parts):
        if idx > 0 and parts[idx - 1] == "aps-workspaces":
            return part

    for part in parts:
        if part and part not in {"amazonaws", "com", "aps-workspaces"} and "-" in part:
            return part

    return None


def _build_timeseries_payload(metric_name: str, value: float, labels: Dict[str, str], timestamp_ms: int) -> bytes:
    request = _WRITE_REQUEST_CLASS()
    series = request.timeseries.add()

    name_label = series.labels.add()
    name_label.name = "__name__"
    name_label.value = metric_name

    for key in sorted(labels.keys()):
        label = series.labels.add()
        label.name = key
        label.value = str(labels[key])

    sample = series.samples.add()
    sample.value = float(value)
    sample.timestamp = int(timestamp_ms)

    return request.SerializeToString()


def push_sample_to_amp(
    metric_name: str,
    value: float,
    labels: Dict[str, str],
    remote_write_url: str,
    region: Optional[str],
    timeout_seconds: int = 5,
) -> bool:
    if not remote_write_url:
        logger.warning("Prometheus remote write URL is not configured; skipping heartbeat push.")
        return False

    session = boto3.Session()
    credentials = session.get_credentials()
    if credentials is None:
        logger.error("AWS credentials are not available for signing remote write request.")
        return False

    frozen_credentials = credentials.get_frozen_credentials()

    resolved_region = region or session.region_name or _infer_region(remote_write_url)
    if not resolved_region:
        logger.error("Unable to determine AWS region for Prometheus remote write.")
        return False

    timestamp_ms = int(time.time() * 1000)
    payload = _build_timeseries_payload(metric_name, value, labels, timestamp_ms)

    headers = {
        "Content-Type": "application/x-protobuf",
        "User-Agent": "celery-prometheus-heartbeat/1.0",
        "X-Prometheus-Remote-Write-Version": "0.1.0",
    }

    if snappy:
        try:
            payload = snappy.compress(payload)
            headers["Content-Encoding"] = "snappy"
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to compress Prometheus payload with snappy: %s", exc)
    else:
        logger.warning("python-snappy not installed; sending uncompressed payload.")

    aws_request = AWSRequest(method="POST", url=remote_write_url, data=payload, headers=headers)
    try:
        SigV4Auth(frozen_credentials, "aps", resolved_region).add_auth(aws_request)
    except (BotoCoreError, NoCredentialsError) as exc:
        logger.error("Failed to sign Prometheus remote write request: %s", exc)
        return False

    if frozen_credentials.token:
        aws_request.headers["X-Amz-Security-Token"] = frozen_credentials.token

    request_headers = dict(aws_request.headers.items())
    request_headers.setdefault("Host", urlparse(remote_write_url).netloc)

    try:
        response = requests.post(remote_write_url, data=payload, headers=request_headers, timeout=timeout_seconds)
        if response.status_code >= 300:
            logger.error(
                "Prometheus remote write request failed with status %s: %s",
                response.status_code,
                response.text,
            )
            return False
    except requests.RequestException as exc:
        logger.error("Prometheus remote write request raised exception: %s", exc)
        return False

    return True
