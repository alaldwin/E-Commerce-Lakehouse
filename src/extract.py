from pathlib import Path
import pandas as pd
import logging
from pandas.errors import EmptyDataError

from utils.config_loader import get_project_root, load_yaml_config

# Load config once
PATHS_CONFIG = load_yaml_config("paths.yaml")
TABLES_CONFIG = load_yaml_config("tables.yaml")

FULL_REQUIRED_FILES = TABLES_CONFIG["full_required_files"]
INCREMENTAL_REQUIRED_FILES = TABLES_CONFIG["incremental_required_files"]
INCREMENTAL_OPTIONAL_FILES = TABLES_CONFIG["incremental_optional_files"]


def resolve_data_path(relative_path: str) -> Path:
    return get_project_root() / relative_path


def validation_file(base_path: Path, required_files: dict):
    # Validate that all required CSV file exist in the given folder.

    for table_name, file_name in required_files.items():
        file_path = base_path / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"Missing file for {table_name}: {file_path}")



def read_csv_file(base_path: Path,
    required_files: dict,
    optional_files: dict | None = None
) -> dict:

    """
    Read required + optional CSV files.

    Rules:
    - Required files:
        - if missing -> fail in validate step
        - if empty -> create empty DataFrame and continue
    - Optional files:
        - if missing -> skip
        - if empty -> skip
    """

    tables = {}

    # Read required files
    for table_name, file_name in required_files.items():
        file_path = base_path / file_name

        try:
            df = pd.read_csv(file_path)
            tables[table_name] = df
            logging.info(f"Loaded required table {table_name}: {file_path.name} | rows={len(df)}")

        except EmptyDataError:
            logging.warning(
                f"Required file is empty (no columns/header): {file_path}. "
                f"Creating empty DataFrame for table '{table_name}'."
            )
            tables[table_name] = pd.DataFrame()

     # Read optional files only if they exist
    if optional_files:
        for table_name, file_name in optional_files.items():
            file_path = base_path / file_name

            if not file_path.exists():
                logging.warning(f"Optional file not found for {table_name}: {file_path} | skipping")
                continue
            try: 
                df = pd.read_csv(file_path)
                tables[table_name] = df
                logging.info(f"Loaded optional table {table_name}: {file_path.name} | rows={len(df)}")

            except EmptyDataError:
                logging.warning(
                    f"Optional file is empty (no columns/header): {file_path} | skipping table '{table_name}'"
                )
                continue

    return tables




def get_latest_batch_date(incremental_root: Path) -> str:

    """
    Find the latest batch_date folder inside:
        data/incremental/batch_date=YYYY-MM-DD
    Returns:
        YYYY-MM-DD
    """

    if not incremental_root.exists():
        raise FileNotFoundError(f"Incremental root folder not found: {incremental_root}")

    batch_folders = [
        folder for folder in incremental_root.iterdir()
        if folder.is_dir() and folder.name.startswith("batch_date=")
    ]

    if not batch_folders:
        raise FileNotFoundError(f"No batch folders found in {incremental_root}")

    batch_dates = sorted(folder.name.replace("batch_date=", "") for folder in batch_folders)
    return batch_dates[-1]




def ingestion_full() -> dict:

    """
    Read all full-load CSV files from:
        data/full/
    """

    logging.info("Starting Full Data Ingestion...")

    try:
        full_data_path = PATHS_CONFIG["paths"]["full_data"]
        base_path = resolve_data_path(full_data_path)

        if not base_path.exists():
            raise FileNotFoundError(
                f"Full data folder not found: {base_path}\n"
                f"Expected folder from config/paths.yaml -> paths.full_data"
            )

        validation_file(base_path, FULL_REQUIRED_FILES)
        all_tables = read_csv_file(base_path, FULL_REQUIRED_FILES)

        logging.info("Full Data Ingestion completed successfully.")
        return all_tables

    except Exception as e:
        logging.error(f"Error during full data ingestion: {e}")
        raise





def ingestion_incremental(batch_date: str = None) -> tuple[dict, str]:

    """
    Read incremental CSV files from:
        data/incremental/batch_date=YYYY-MM-DD/

    If batch_date is None, automatically use the latest available batch.
    Returns:
        (all_tables, resolved_batch_date)
    """

    logging.info("Starting Incremental Data Ingestion...")

    try:
        incremental_data_path = PATHS_CONFIG["paths"]["incremental"]
        incremental_root = resolve_data_path(incremental_data_path)

        if batch_date is None:
            batch_date = get_latest_batch_date(incremental_root)
            logging.info(f"No batch_date provided. Using latest batch_date={batch_date}")

        base_path = incremental_root / f"batch_date={batch_date}"

        if not base_path.exists():
            raise FileNotFoundError(
                f"Incremental batch folder not found: {base_path}\n"
                f"Expected folder: data/incremental/batch_date={batch_date}/"
            )

        validation_file(base_path, INCREMENTAL_REQUIRED_FILES)

        all_tables = read_csv_file(
            base_path=base_path,
            required_files=INCREMENTAL_REQUIRED_FILES,
            optional_files=INCREMENTAL_OPTIONAL_FILES
        )

        logging.info(
            f"Incremental Data Ingestion completed successfully for batch_date={batch_date}"
        )
        return all_tables, batch_date

    except Exception as e:
        logging.error(f"Error during incremental data ingestion: {e}")
        raise

    