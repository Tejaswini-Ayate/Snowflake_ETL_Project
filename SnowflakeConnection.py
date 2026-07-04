import snowflake.connector
from dotenv import load_dotenv
import os
load_dotenv()

account = os.getenv("snowflake_account")
user = os.getenv("snowflake_user")
password = os.getenv("snowflake_password")
warehouse = os.getenv("snowflake_warehouse")
database = os.getenv("snowflake_database")
schema = os.getenv("snowflake_schema")

def get_connection():

    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        database=database,
        schema=schema
    )

    return conn