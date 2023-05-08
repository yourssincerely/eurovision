import pandas as pd
import numpy as np
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

with open("login/mysql_credentials.json", "r") as f:
    info = json.load(f)
    user = info['user']
    password = info['password']

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@localhost/eurovision")
session = Session()

def pd_df_to_sql_tables(df, name, engine = engine, session = session):
    """
    Create a SQL table with the specified name in the given database engine, using the data from the provided pandas DataFrame.

    Parameters:
    - df: pd.DataFrame - The pandas DataFrame to be used as the source data for the SQL table.
    - name: str - A string representing the name of the SQL table to be created.
    - engine: sqlalchemy.engine.Engine - An SQL Alchemy `Engine` object representing the connection to the database. 
      Defaults to `engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@localhost/eurovision")`.
    - session: sqlalchemy.orm.Session - An SQL Alchemy `Session` object representing the connection to the database.
      Defaults to `Session()`.

    Returns:
    - None - The function does not return any value.

    Raises:
    - sqlalchemy.exc.ProgrammingError - If there is an error in the syntax of the SQL query or in the connection to the database.

    Example usage:
    ```
    engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@localhost/eurovision")
    session = Session()
    df = pd.read_csv("data.csv")
    pd_df_to_sql_tables(df, "my_table", engine, session)
    ```
    """
    df.to_sql(
        name = name,
        con = engine,
        if_exists = "replace",
        index = False
        )
    session.commit()
    print(f"Table {name} created with {len(df)} rows.")

def sql(query:str, engine = engine):
    """
    Execute the specified SQL query on the given database engine and return the result as a pandas DataFrame.

    Parameters:
    - query: str - A string containing the SQL query to execute.
    - engine: sqlalchemy.engine.Engine - An SQL Alchemy `Engine` object representing the connection to the database. 
      Defaults to `engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@localhost/eurovision")`.

    Returns:
    - pd.core.frame.DataFrame - A pandas DataFrame containing the result of the SQL query.

    Raises:
    - sqlalchemy.exc.ProgrammingError - If there is an error in the syntax of the SQL query or in the connection to the database.

    Example usage:
    ```
    engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@localhost/eurovision")
    df = sql("SELECT * FROM countries WHERE year = 2019", engine)
    ```
    """
    results = engine.execute(query).mappings().all()
    df = pd.DataFrame.from_dict(results)
    return df

def create_view(query, engine=engine):
    """
    Creates a view in the database using the specified SQL query.

    Parameters:
    - query: str - A string containing the SQL query to create the view.
    - engine: sqlalchemy.engine.Engine - A SQL Alchemy `Engine` object representing the connection to the database.

    Returns:
    - None - The function does not return any value.

    Example usage:
    ```
    create_view("CREATE OR REPLACE VIEW my_view AS SELECT column1, column2 FROM my_table WHERE column3 > 10", engine)
    ```
    """
    with Session(engine) as session:
        session.execute(text(query))
        session.commit()
    print("View has been created!")