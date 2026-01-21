from celery import shared_task
from twilio.rest import Client
from datetime import datetime, timedelta
import pandas as pd
import boto3
import io
from django.conf import settings


@shared_task
def pull_twilio_messages_to_s3():
    """
    Pull yesterday's Twilio messages and save as Parquet to S3
    """
    # Calculate yesterday's date range
    yesterday = datetime.now() - timedelta(days=1)
    start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=0)

    try:
        # Fetch messages from Twilio
        messages = fetch_twilio_messages(start_date, end_date)

        if not messages:
            return f"No messages found for {yesterday.strftime('%Y-%m-%d')}"

        # Convert to DataFrame and save as Parquet to S3
        df = pd.DataFrame(messages)
        s3_key = upload_to_s3(df, yesterday)

        return f"Successfully uploaded {len(messages)} messages to S3: {s3_key}"

    except Exception as e:
        return f"Error processing Twilio messages: {str(e)}"


def fetch_twilio_messages(start_date, end_date):
    """
    Fetch Twilio messages for date range
    """
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    if not account_sid or not auth_token:
        raise ValueError("Missing Twilio credentials")

    client = Client(account_sid, auth_token)

    messages = client.messages.list(
        date_sent_after=start_date, date_sent_before=end_date, limit=None
    )

    message_records = []
    for msg in messages:
        record = {
            "from": msg.from_,
            "to": msg.to,
            "body": msg.body,
            "status": msg.status,
            "direction": msg.direction,
            "date_sent": msg.date_sent,
            "date_created": msg.date_created,
            "price": float(msg.price) if msg.price else None,
            "price_unit": msg.price_unit,
            "sid": msg.sid,
        }
        message_records.append(record)

    return message_records


def upload_to_s3(df, date):
    """
    Upload DataFrame as Parquet to S3
    """
    # Convert datetime columns properly
    df["date_sent"] = pd.to_datetime(df["date_sent"])
    df["date_created"] = pd.to_datetime(df["date_created"])

    # Create S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    # Generate S3 key with date partitioning
    s3_key = f"twilio/{date.year}/{date.month:02d}/{date.day:02d}/messages_{date.strftime('%Y%m%d')}.parquet"

    # Convert DataFrame to Parquet in memory
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, engine="pyarrow", index=False)
    parquet_buffer.seek(0)

    # Upload to S3
    s3_client.upload_fileobj(
        parquet_buffer,
        "sknv-datalake-inbound",
        s3_key,
        ExtraArgs={"ContentType": "application/octet-stream"},
    )

    return s3_key
