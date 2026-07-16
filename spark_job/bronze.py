from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, TimestampType, FloatType
import pyspark.sql.functions as f

spark.sql(f"
  DROP CATALOG IF EXISTS ecommerce CASCADE;
  CREATE CATALOG IF NOT EXISTS ecommerce;

  DROP SCHEMA IF EXISTS ecommerce.bronze_schema CASCADE;
  CREATE SCHEMA IF NOT EXISTS ecommerce.bronze_schema;
")

catalog = "ecommerce"
table_schema = "bronze_schema"
bucket_name = "ecommercelakehouse"





data_path = "customer"

table_name = f"{catalog}.{table_schema}.brnz_{data_path}"

full_path = f"s3://{bucket_name}/raw/full_load/{data_path}.csv"

incremental_path = (
    f"s3://{bucket_name}/raw/incremental/"
    f"batch_date=2026-07-12/{data_path}.csv"
)


# Read Full Load
df_full = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(full_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Read Incremental
df_incremental = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(incremental_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Create Bronze Table (first Run)
if not spark.catalog.tableExists(table_name):

    (df_full.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(table_name))

    print("Bronze table created.")


# Append Incremental Batch
if df_incremental.count() > 0:

    (df_incremental.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(table_name))

    print(f"Appended {df_incremental.count()} rows.")

else:
    print("No incremental records found.")


# Verify
bronze_df = spark.read.table(table_name)

print("Total Bronze Rows:", bronze_df.count())

display(
    bronze_df.orderBy(f.col("ingestion_timestamp").desc())
)








data_path = "order_items"

table_name = f"{catalog}.{table_schema}.brnz_{data_path}"

full_path = f"s3://{bucket_name}/raw/full_load/{data_path}.csv"

incremental_path = (
    f"s3://{bucket_name}/raw/incremental/"
    f"batch_date=2026-07-12/{data_path}.csv"
)


# Read Full Load
df_full = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(full_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Read Incremental
df_incremental = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(incremental_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Create Bronze Table (first Run)
if not spark.catalog.tableExists(table_name):

    (df_full.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(table_name))

    print("Bronze table created.")


# Append Incremental Batch
if df_incremental.count() > 0:

    (df_incremental.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(table_name))

    print(f"Appended {df_incremental.count()} rows.")

else:
    print("No incremental records found.")


# Verify
bronze_df = spark.read.table(table_name)

print("Total Bronze Rows:", bronze_df.count())

display(
    bronze_df.orderBy(f.col("ingestion_timestamp").desc())
)






data_path = "orders"

table_name = f"{catalog}.{table_schema}.brnz_{data_path}"

full_path = f"s3://{bucket_name}/raw/full_load/{data_path}.csv"

incremental_path = (
    f"s3://{bucket_name}/raw/incremental/"
    f"batch_date=2026-07-12/{data_path}.csv"
)


# Read Full Load
df_full = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(full_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Read Incremental
df_incremental = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(incremental_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Create Bronze Table (first Run)
if not spark.catalog.tableExists(table_name):

    (df_full.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(table_name))

    print("Bronze table created.")


# Append Incremental Batch
if df_incremental.count() > 0:

    (df_incremental.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(table_name))

    print(f"Appended {df_incremental.count()} rows.")

else:
    print("No incremental records found.")


# Verify
bronze_df = spark.read.table(table_name)

print("Total Bronze Rows:", bronze_df.count())

display(
    bronze_df.orderBy(f.col("ingestion_timestamp").desc())
)






data_path = "payments"

table_name = f"{catalog}.{table_schema}.brnz_{data_path}"

full_path = f"s3://{bucket_name}/raw/full_load/{data_path}.csv"

incremental_path = (
    f"s3://{bucket_name}/raw/incremental/"
    f"batch_date=2026-07-12/{data_path}.csv"
)


# Read Full Load
df_full = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(full_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Read Incremental
df_incremental = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(incremental_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Create Bronze Table (first Run)
if not spark.catalog.tableExists(table_name):

    (df_full.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(table_name))

    print("Bronze table created.")


# Append Incremental Batch
if df_incremental.count() > 0:

    (df_incremental.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(table_name))

    print(f"Appended {df_incremental.count()} rows.")

else:
    print("No incremental records found.")


# Verify
bronze_df = spark.read.table(table_name)

print("Total Bronze Rows:", bronze_df.count())

display(
    bronze_df.orderBy(f.col("ingestion_timestamp").desc())
)







data_path = "product_category"

table_name = f"{catalog}.{table_schema}.brnz_{data_path}"

full_path = f"s3://{bucket_name}/raw/full_load/{data_path}.csv"


# Read Full Load
df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(full_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)

df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(table_name)

print("Bronze table created.")

bronze_df = spark.read.table(table_name)

display(
    bronze_df.orderBy(f.col("ingestion_timestamp").desc())
)







data_path = "products"

table_name = f"{catalog}.{table_schema}.brnz_{data_path}"

full_path = f"s3://{bucket_name}/raw/full_load/{data_path}.csv"

incremental_path = (
    f"s3://{bucket_name}/raw/incremental/"
    f"batch_date=2026-07-12/{data_path}.csv"
)


# Read Full Load
df_full = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(full_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Read Incremental
df_incremental = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(incremental_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Create Bronze Table (first Run)
if not spark.catalog.tableExists(table_name):

    (df_full.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(table_name))

    print("Bronze table created.")


# Append Incremental Batch
if df_incremental.count() > 0:

    (df_incremental.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(table_name))

    print(f"Appended {df_incremental.count()} rows.")

else:
    print("No incremental records found.")


# Verify
bronze_df = spark.read.table(table_name)

print("Total Bronze Rows:", bronze_df.count())

display(
    bronze_df.orderBy(f.col("ingestion_timestamp").desc())
)








data_path = "returns_refunds"

table_name = f"{catalog}.{table_schema}.brnz_{data_path}"

full_path = f"s3://{bucket_name}/raw/full_load/{data_path}.csv"

incremental_path = (
    f"s3://{bucket_name}/raw/incremental/"
    f"batch_date=2026-07-12/{data_path}.csv"
)


# Read Full Load
df_full = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(full_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Read Incremental
df_incremental = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(incremental_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Create Bronze Table (first Run)
if not spark.catalog.tableExists(table_name):

    (df_full.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(table_name))

    print("Bronze table created.")


# Append Incremental Batch
if df_incremental.count() > 0:

    (df_incremental.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(table_name))

    print(f"Appended {df_incremental.count()} rows.")

else:
    print("No incremental records found.")


# Verify
bronze_df = spark.read.table(table_name)

print("Total Bronze Rows:", bronze_df.count())

display(
    bronze_df.orderBy(f.col("ingestion_timestamp").desc())
)








data_path = "sellers"

table_name = f"{catalog}.{table_schema}.brnz_{data_path}"

full_path = f"s3://{bucket_name}/raw/full_load/{data_path}.csv"


# Read Full Load
df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(full_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)

df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(table_name)

print("Bronze table created.")

bronze_df = spark.read.table(table_name)

display(
    bronze_df.orderBy(f.col("ingestion_timestamp").desc())
)











data_path = "shipping_events"

table_name = f"{catalog}.{table_schema}.brnz_{data_path}"

full_path = f"s3://{bucket_name}/raw/full_load/{data_path}.csv"

incremental_path = (
    f"s3://{bucket_name}/raw/incremental/"
    f"batch_date=2026-07-12/{data_path}.csv"
)


# Read Full Load
df_full = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(full_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Read Incremental
df_incremental = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(incremental_path)
    .withColumn("_source_file", f.col("_metadata.file_path"))
    .withColumn("ingestion_timestamp", f.current_timestamp())
)


# Create Bronze Table (first Run)
if not spark.catalog.tableExists(table_name):

    (df_full.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(table_name))

    print("Bronze table created.")


# Append Incremental Batch
if df_incremental.count() > 0:

    (df_incremental.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(table_name))

    print(f"Appended {df_incremental.count()} rows.")

else:
    print("No incremental records found.")


# Verify
bronze_df = spark.read.table(table_name)

print("Total Bronze Rows:", bronze_df.count())

display(
    bronze_df.orderBy(f.col("ingestion_timestamp").desc())
)
