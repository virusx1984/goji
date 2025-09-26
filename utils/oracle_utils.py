# goji/utils/oracle_utils.py
import sqlalchemy as sa
from sqlalchemy.engine import Connection

# Oracle's identifier limit is 30 characters.
ORACLE_MAX_NAME_LENGTH = 30

def get_short_name(table_name):
    """
    Generates a unique, short name for Oracle identifiers.
    This simple implementation truncates the name if it's too long.
    """
    # Adjust length calculation based on the new naming convention (no _id suffix)
    # The prefix 'seq_' or 'trg_' is 4 characters long.
    if len(table_name) > ORACLE_MAX_NAME_LENGTH - 4:
        return table_name[:(ORACLE_MAX_NAME_LENGTH - 4)] + "_sn"
    return table_name

def generate_sequence_and_trigger_sql(table_name):
    """
    Generates SQL statements for creating a sequence and a trigger
    for a table's 'id' column in Oracle.
    """
    # Use a short name for long tables
    short_table_name = get_short_name(table_name)
    # The sequence and trigger names do not include _id suffix
    seq_name = f"seq_{short_table_name}"
    trg_name = f"trg_{short_table_name}"

    # The SQL for the sequence is wrapped in sa.text()
    sequence_sql = f"""CREATE SEQUENCE "{seq_name}" START WITH 1 INCREMENT BY 1 NOCACHE"""
    
    # The SQL for the trigger MUST be wrapped in sa.text() to prevent bind parameter errors
    trigger_sql = f"""  
    CREATE OR REPLACE TRIGGER "{trg_name}"
    BEFORE INSERT ON {table_name}
    FOR EACH ROW
    when (new."ID" IS NULL) -- Condition is checked here
    BEGIN
       SELECT "{seq_name}".nextval
       INTO :new."ID" FROM dual;
    END;
    """

    return (sequence_sql, trigger_sql)

def generate_drop_sql(table_name):
    """
    Generates SQL statements for dropping a sequence and a trigger
    for a table's 'id' column in Oracle, gracefully handling non-existent objects.
    """
    # Use a short name for long tables
    short_table_name = get_short_name(table_name)
    # The sequence and trigger names do not include _id suffix
    seq_name = f"seq_{short_table_name}"
    trg_name = f"trg_{short_table_name}"

    # Use sa.text() for both drop statements to prevent errors
    drop_trigger_sql = f"""
    BEGIN
       EXECUTE IMMEDIATE 'DROP TRIGGER "{trg_name}"';
    EXCEPTION
       WHEN OTHERS THEN
          IF SQLCODE != -4080 THEN
             RAISE;
          END IF;
    END;
    """
    
    drop_sequence_sql = f"""
    BEGIN
       EXECUTE IMMEDIATE 'DROP SEQUENCE "{seq_name}"';
    EXCEPTION
       WHEN OTHERS THEN
          IF SQLCODE != -2289 THEN
             RAISE;
          END IF;
    END;
    """
    
    return (drop_trigger_sql, drop_sequence_sql)