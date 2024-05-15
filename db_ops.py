import pandas as pd
import db_connect
import conf
import re


def upload_csv_to_database():
    try:
        # Read CSV file into a pandas DataFrame
        df = pd.read_excel(conf.csv_file_path, sheet_name='Sheet1')

        df.fillna(1, inplace=True)
        df.columns = [re.sub(r'\W+', '_', col)[:30] for col in df.columns]

        main = db_connect.DatabaseUploader()
        conn = main.connect_to_database()

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Create a table in the database
        create_table_query = f"CREATE TABLE IF NOT EXISTS {conf.table_name} ("
        for column in df.columns:
            create_table_query += f"{column} VARCHAR,"
        create_table_query = create_table_query[:-1]  # Remove the trailing comma
        create_table_query += ");"
        cur.execute(create_table_query)

        # Insert data into the table
        for index, row in df.iterrows():
            insert_query = f"INSERT INTO {conf.table_name} ({', '.join(df.columns)}) VALUES {tuple(row.values)};"
            cur.execute(insert_query)

        # Commit the transaction
        conn.commit()

        # Close cursor
        cur.close()

        # Close connection
        main.close_connection()

        print("CSV file uploaded to database successfully.")

    except Exception as e:
        print("Error:", e)

if __name__=="__main__":
    upload_csv_to_database()