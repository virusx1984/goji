"""create all sequences and triggers

Revision ID: 6b47ebb28177
Revises: 454c238b2ab5
Create Date: 2025-09-26 20:29:12.693148

"""

# revision identifiers, used by Alembic.
revision = '6b47ebb28177'
down_revision = '454c238b2ab5'
branch_labels = None
depends_on = None


import sys

project_path = r'F:\Lining\MyProjects\OnGitHub'
sys.path.append(project_path)

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects import oracle
from sqlalchemy import text

# Import all models to ensure Alembic can discover the tables.
from goji.app.models import ModelBase
from goji.app.user_management.models import user_roles, role_permissions
# Import the custom utility functions for generating SQL.
from goji.utils.oracle_utils import generate_sequence_and_trigger_sql, generate_drop_sql


def get_all_managed_tables():
    """
    Dynamically gets all table names that inherit from ModelBase
    and also explicitly lists association tables.
    """
    # Tables from ModelBase subclasses
    managed_tables = [model.__tablename__ for model in ModelBase.__subclasses__() if 'alembic_version' not in model.__tablename__]
    
    # Add association tables manually, as they don't inherit from ModelBase
    managed_tables.append('gj_user_roles')
    managed_tables.append('gj_role_permissions')
    
    return managed_tables

def upgrade():
    # This function creates sequences and triggers by completely bypassing
    # SQLAlchemy's execution layer and using the raw DBAPI driver directly.
    
    # Check if the current database dialect is Oracle.
    if op.get_context().dialect.name != 'oracle':
        print("Skipping Oracle-specific migration as the dialect is not 'oracle'.")
        return
        
    # Get the current SQLAlchemy Connection object from Alembic's context.
    bind = op.get_bind()
    
    # Get the underlying raw DBAPI connection using the correct '.connection' attribute.
    dbapi_connection = bind.connection

    # We will manage the cursor and transaction manually.
    cursor = dbapi_connection.cursor()
    try:
        # Loop through all tables that need a sequence and trigger.
        for table_name in get_all_managed_tables():
            print(f"Processing table: {table_name}")
            
            # Generate the plain, native SQL strings.
            sequence_sql, trigger_sql = generate_sequence_and_trigger_sql(table_name)
            
            # Execute the SQL directly using the DBAPI cursor.
            cursor.execute(sequence_sql)
            cursor.execute(trigger_sql)
            
            print(f"Successfully executed DDL for {table_name}.")

        # If the loop completes without errors, commit the transaction.
        print("All sequences and triggers processed. Committing transaction.")
        dbapi_connection.commit()

    except Exception as e:
        # If any error occurs, roll back the entire transaction.
        print(f"An error occurred: {e}. Rolling back transaction.")
        dbapi_connection.rollback()
        # Re-raise the exception to halt the Alembic migration.
        raise e
        
    finally:
        # No matter what happens, always close the cursor.
        print("Closing cursor.")
        cursor.close()

            
def downgrade():
    """
    Removes sequences and triggers for all tables.
    
    This function performs the reverse operation of `upgrade`. It iterates
    through the same list of tables and, for each one, generates and
    executes the SQL to drop the corresponding trigger and sequence.
    """
    if op.get_context().dialect.name != 'oracle':
        print("Skipping Oracle-specific migration.")
        return

    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    for table_name in get_all_managed_tables():
        try:
            # Check if the table has an 'id' column before attempting to drop
            columns = inspector.get_columns(table_name)
            if any(col['name'].lower() == 'id' for col in columns):
                print(f"Dropping sequence and trigger for table: {table_name}")
                
                # Generate the drop SQL using the utility function
                drop_trigger_sql, drop_sequence_sql = generate_drop_sql(table_name)

                # Execute the generated SQL statements
                op.execute(text(drop_trigger_sql))
                op.execute(text(drop_sequence_sql))
        except Exception as e:
            # Catch exceptions, which is useful for situations where a table
            # might have been dropped but its sequence/trigger wasn't.
            print(f"Skipping table {table_name} due to an error: {e}")