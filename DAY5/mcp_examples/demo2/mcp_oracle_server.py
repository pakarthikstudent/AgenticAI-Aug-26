import os
import oracledb

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


# Load environment variables
load_dotenv()


# -------------------------------------
# Create MCP Server
# -------------------------------------

mcp = FastMCP("Oracle23aiTools")


# -------------------------------------
# Oracle Connection
# -------------------------------------

def get_connection():

    connection = oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN")
    )

    return connection


# -------------------------------------
# MCP TOOL 1
# Execute SQL Query
# -------------------------------------

@mcp.tool()
def execute_sql(query: str):
    """
    Execute a SELECT query in Oracle Database.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(query)

    columns = [
        column[0]
        for column in cursor.description
    ]

    rows = cursor.fetchall()

    result = []

    for row in rows:

        row_dict = dict(
            zip(columns, row)
        )

        result.append(row_dict)

    cursor.close()

    connection.close()

    return result


# -------------------------------------
# MCP TOOL 2
# Get Database Tables
# -------------------------------------

@mcp.tool()
def get_tables():
    """
    Get all tables owned by the current Oracle user.
    """

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        SELECT table_name
        FROM user_tables
        ORDER BY table_name
    """

    cursor.execute(query)

    tables = [
        row[0]
        for row in cursor.fetchall()
    ]

    cursor.close()

    connection.close()

    return tables


# -------------------------------------
# Start MCP Server
# -------------------------------------

if __name__ == "__main__":

    mcp.run()