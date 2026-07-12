
import logging
from pathlib import Path

from extract import ingestion_full, ingestion_incremental
from transform import transform_data
from load import load_data_to_s3
from utils.config_loader import get_project_root, load_yaml_config


PATHS_CONFIG = load_yaml_config("paths.yaml")
LOGS_DIR = PATHS_CONFIG["paths"]["logs_dir"]

def setup_logging():
    project_root = get_project_root()
    logs_path = project_root / LOGS_DIR
    logs_path.mkdir(parents=True, exist_ok=True)

    log_file = logs_path / "ecommerce_pipeline.log"

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def run_pipeline(load_type: str = "incremental", batch_date: str = None):
    """
    Run the ETL pipeline.

    Parameters
    ----------
    load_type : str
        'full' or 'incremental'
    batch_date : str, optional
        Used only for incremental loads.
        If None, the latest batch_date folder will be used.
    """

    logging.info(f"Pipeline started | load_type={load_type} | batch_date={batch_date}")

    try:
        # ======================================================
        # FULL LOAD
        # ======================================================
        if load_type == "full":
            ingestion_tables = ingestion_full()

            transformation = transform_data(
                ingestion_tables,
                batch_date=batch_date,
                load_type="full"
            )

            # Upload transformed full-load files to S3
            load_data_to_s3(
                transformation,
                load_type="full"
            )

        # ======================================================
        # INCREMENTAL LOAD
        # ======================================================
        elif load_type == "incremental":
            ingestion_tables, resolved_batch_date = ingestion_incremental(batch_date=batch_date)

            transformation = transform_data(
                ingestion_tables,
                batch_date=resolved_batch_date,
                load_type="incremental"
            )

            # Upload transformed incremental batch to S3
            load_data_to_s3(
                transformation,
                load_type="incremental",
                batch_date=resolved_batch_date
            )

        else:
            raise ValueError("load_type must be 'full' or 'incremental'")

        logging.info("Pipeline completed successfully.")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    # FULL LOAD
    # run_pipeline(load_type="full")

    # LATEST INCREMENTAL BATCH
    run_pipeline(load_type="incremental")

    # SPECIFIC INCREMENTAL BATCH
    # run_pipeline(load_type="incremental", batch_date="2026-07-07")

