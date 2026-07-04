from snowflake.connector.pandas_tools import write_pandas
from SnowflakeConnection import get_connection
from config import CSV_FILE, TARGET_TABLE, LOG_FILE
from validation import validate_nulls, validate_duplicates,validate_negative_salary,validate_department
import pandas as pd
import logging
from datetime import datetime


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

conn=None

# Connect to Snowflake
try:
    logger.info("ETL Started")
    logger.info(f"Source File: {CSV_FILE}")
    logger.info(f"Target Table: {TARGET_TABLE}")
    conn = get_connection()

    # Read CSV
    df = pd.read_csv(CSV_FILE)
    original_row_count = len(df)
    if df.empty:
        logger.warning(
            f"Input file '{CSV_FILE}' contains no data. ETL stopped."
        )
        raise SystemExit("Empty input file")
    
    logger.info("CSV loaded successfully.")
    # Validate incoming data
    #null value logic
    good_rows, bad_rows = validate_nulls(df)
    logger.info(
        f"Null validation completed. "
        f"Null rows found: {len(bad_rows)}"
    )
    
    #duplicate logic
    good_rows, duplicate_rows = validate_duplicates(good_rows)
    all_rejected = pd.concat(
    [bad_rows, duplicate_rows],
    ignore_index=True
    )
    logger.info(
        f"Duplicate validation completed. "
        f"Duplicate rows found: {len(duplicate_rows)}"
    )

    #negative salary logic
    good_rows, negative_salary_rows = validate_negative_salary(good_rows)
    all_rejected = pd.concat(
    [bad_rows,duplicate_rows, negative_salary_rows],
    ignore_index=True
    )
    logger.info(
        f"Negative salary validation completed. "
        f"Negative salary rows found: {len(negative_salary_rows)}"
    )

    good_rows, department_rows = validate_department(good_rows)
    all_rejected = pd.concat(
    [bad_rows,duplicate_rows, negative_salary_rows,department_rows],
    ignore_index=True
    )
    logger.info(
        f"Department validation completed. "
        f"Invalid department rows found: {len(department_rows)}"
    )
    
    # Save rejected rows
    if len(all_rejected) > 0:
        logger.warning(
            f"Rejected Rows: {len(all_rejected)} "
            f"(Null: {len(bad_rows)}, Duplicate: {len(duplicate_rows)},"
            f"Negative salary: {len(negative_salary_rows)}, Invalid department: {len(department_rows)})"
        )
        current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rejected_file_name = f"Rejected_Records_{current_timestamp}.csv"
        all_rejected.to_csv(
            rejected_file_name,
            index=False
    )

        logger.warning(f"Rejected records saved to {rejected_file_name}")
    # Handle good rows
    
    loaded_row_count_expected = len(good_rows)
    rejected_row_count = len(all_rejected)

    if len(good_rows) > 0:
        success, nchunks, nrows, _ = write_pandas(
            conn,
            good_rows,
            TARGET_TABLE
        )

        conn.commit()
        logger.info(f"Success: {success}")
        logger.info(f"Rows Loaded: {nrows}")

        if original_row_count == loaded_row_count_expected + rejected_row_count:
            logger.info(
            f"Row Count Reconciliation PASSED | "
            f"Original: {original_row_count}, "
            f"Loaded: {loaded_row_count_expected}, "
            f"Rejected: {rejected_row_count}"
            )
        else:
            logger.error(
            f"Row Count Reconciliation FAILED | "
            f"Original: {original_row_count}, "
            f"Loaded: {loaded_row_count_expected}, "
            f"Rejected: {rejected_row_count}"
            )
        
        logger.info("ETL completed successfully!")

#handles if source file is not available
except FileNotFoundError:
    logger.error(
        f"Input file '{CSV_FILE}' not found. ETL aborted."
        )
    
except Exception as e:
    logger.error(f"ETL failed: {e}")
    
finally:
    if conn is not None:
        conn.close()
    logger.info("Resources cleaned up successfully.")