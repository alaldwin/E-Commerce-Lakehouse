import pandas as pd
import logging

def transform_data(
        table_files: dict, 
        batch_date: str = None, 
        load_type: str = "full"
    ) -> dict:

    """
    Transform ingested tables.
    
    If batch_date is provided (incremental load), add metadata columns:
        - batch_date
        - ingestion_timestamp
    """

    if load_type is None:
        raise ValueError("load_type must be provided to transform_data()")

    logging.info(f"Starting Data Transformation... | load_type={load_type} | batch_date={batch_date}")

    try:

        transform_data = {}

        for table_name, df in table_files.items():
            print(f"\n{'-' * 70}")
            print(f"TABLE: {table_name.upper()}")
            print(f"{'-' * 70}")


            df = df.copy()

            # Skip completely empty DataFrames with no columns
            if df.empty and len(df.columns) == 0:
                logging.warning(f"Skipping table '{table_name}' because it is completely empty.")
                continue

            # Standardize column names
            df.columns = [str(col).strip().lower() for col in df.columns]


            # metadata columns
            if batch_date is not None:
                df["batch_date"] = batch_date
                df["ingestion_timestamp"] = pd.Timestamp.now()
                df["load_type"] = load_type


            # check for missing values
            print("\n    Missing Values:    ")
            missing_data = df.isnull().sum()
            missing_percentage = (missing_data / len(df)) * 100 if len(df) > 0 else 0 

            missing_df = pd.DataFrame({
                "Missing Values": missing_data,
                "Percentage": missing_percentage
            })

            missing_df = missing_df[missing_df["Missing Values"] > 0]

            if len(missing_df) > 0:
                print(missing_df)
            else:
                print("No missing values found.")


            # check for duplicate
            print("\n    Duplicate Records Check:   ")
            duplicate_records = df.duplicated().sum()
            print(f" Duplicate Records: {duplicate_records}")

            

            # Type conversions by table
            if table_name in "orders":
                if "order_date" in df.columns:
                    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

                if "delivered_date" in df.columns:
                        df["delivered_date"] = pd.to_datetime(df["delivered_date"], errors="coerce")

                if "shipped_date" in df.columns:
                    df["shipped_date"] = pd.to_datetime(df["shipped_date"], errors="coerce")

                if "total_amount" in df.columns:
                    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")

            elif table_name == "order_items":
                numeric_cols = ["quantity", "unit_price", "discount_amount", "line_total"]
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")

            elif table_name == "payments":
                numeric_cols = ["amount"]
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")

            # returns_refunds table
            elif table_name == "returns_refunds":
                if "refund_amount" in df.columns:
                    df["refund_amount"] = pd.to_numeric(df["refund_amount"], errors="coerce")

                if "return_date" in df.columns:
                    df["return_date"] = pd.to_datetime(df["return_date"], errors="coerce")

            # shipping_events table
            elif table_name == "shipping_events":
                if "event_time" in df.columns:
                    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")

            transform_data[table_name] = df

        logging.info("Data Transformation Completed Successfully.")
        return transform_data

    except Exception as e:
        logging.error(f"Error during data transformation: {e}")
        raise