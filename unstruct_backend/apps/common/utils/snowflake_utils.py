from django.conf import settings
import snowflake.connector
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas

class SnowflakeManager:
    def __init__(self, config):
        """
        Initialize with Snowflake configuration
        
        Args:
            config: dict containing Snowflake credentials and configuration:
                - account
                - user
                - password
                - warehouse
                - database
                - schema
                - role
        """
        self.config = config

    def get_connection(self):
        return snowflake.connector.connect(
            account=self.config['account'],
            user=self.config['user'],
            password=self.config['password'],
            warehouse=self.config['warehouse'],
            database=self.config['database'],
            schema=self.config['schema'],
            role=self.config['role']
        )

    def upload_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
        """
        Upload a pandas DataFrame to Snowflake table
        
        Args:
            df: Pandas DataFrame to upload
            table_name: Name of the target table
            if_exists: What to do if table exists ('append', 'replace', 'fail')
        """
        conn = self.get_connection()
        try:
            # Create table if it doesn't exist
            columns = []
            for col in df.columns:
                dtype = 'VARCHAR' if df[col].dtype == 'object' else 'FLOAT' if df[col].dtype in ['float64', 'float32'] else 'INTEGER'
                columns.append(f'"{col}" {dtype}')
            
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns)}
            )
            """
            
            conn.cursor().execute(create_table_sql)
            
            # Write the DataFrame to Snowflake
            success, num_chunks, num_rows, output = write_pandas(
                conn=conn,
                df=df,
                table_name=table_name,
                database=self.config['database'],
                schema=self.config['schema'],
                quote_identifiers=True
            )
            
            return {
                'success': success,
                'rows_uploaded': num_rows
            }
            
        finally:
            conn.close()
