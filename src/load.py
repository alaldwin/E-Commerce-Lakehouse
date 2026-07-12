
import os
import io
import logging
import boto3
from dotenv import load_dotenv

load_dotenv()


def delete_s3_prefix(s3_client, bucket_name: str, prefix: str):

    """
    Delete all objects under an S3 prefix.
    """

    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if "Contents" not in response:
        logging.info(f"No existing objects found under s3://{bucket_name}/{prefix}")
        return

    objects_to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]

    s3_client.delete_objects(
        Bucket=bucket_name,
        Delete={"Objects": objects_to_delete}
    )

    logging.info(f"Deleted existing objects under s3://{bucket_name}/{prefix}")


def load_data_to_s3(
    transform_tables: dict,
    load_type: str = "full",
    batch_date: str | None = None,
    overwrite: bool = True
):
    
    """
    Upload transformed pandas DataFrames to AWS S3 as CSV files.

    Full load:
        s3://bucket/base_prefix/full_load/

    Incremental load:
        s3://bucket/base_prefix/incremental/batch_date=YYYY-MM-DD/

    Parameters
    ----------
    transform_tables : dict
        Dictionary of {table_name: pandas_dataframe}
    load_type : str
        "full" or "incremental"
    batch_date : str | None
        Required when load_type="incremental"
    overwrite : bool
        If True, delete existing objects in the target prefix first
    """


    logging.info(
        f"Starting S3 Data Upload... | load_type={load_type} | batch_date={batch_date}"
    )

    try:
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_DEFAULT_REGION")

        bucket_name = os.getenv("S3_BUCKET_NAME")
        base_prefix = os.getenv("S3_BASE_PREFIX")

        if not bucket_name:
            raise ValueError("S3_BUCKET_NAME is missing in .env")

        if load_type not in ["full", "incremental"]:
            raise ValueError("load_type must be either 'full' or 'incremental'")

        if load_type == "incremental" and not batch_date:
            raise ValueError("batch_date is required for incremental loads")

        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

        if load_type == "full":
            target_prefix = f"{base_prefix}/full_load"
        else:
            target_prefix = f"{base_prefix}/incremental/batch_date={batch_date}"

        logging.info(f"S3 target prefix: s3://{bucket_name}/{target_prefix}/")

        # Optional cleanup before upload
        if overwrite:
            delete_s3_prefix(s3, bucket_name, target_prefix)

        for table_name, df in transform_tables.items():
            logging.info(f"Uploading table: {table_name}")

            if df.empty and len(df.columns) == 0:
                logging.warning(f"Skipping table '{table_name}' because it is completely empty.")
                continue

            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)

            s3_key = f"{target_prefix}/{table_name}.csv"

            s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=csv_buffer.getvalue(),
                ContentType="text/csv"
            )

            logging.info(f"Uploaded '{table_name}' to s3://{bucket_name}/{s3_key}")

        logging.info("All tables uploaded to S3 successfully.")

    except Exception as e:
        logging.error(f"Error during S3 upload: {e}")
        raise

