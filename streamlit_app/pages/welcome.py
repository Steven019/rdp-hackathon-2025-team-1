import sqlite3
from datetime import datetime
import pandas as pd

import streamlit as st


def connect_to_db():
    connection = sqlite3.connect('./db/warehouse_data.db')
    c = connection.cursor()
    c.execute('SELECT * FROM skus')
    #connection.commit()
    return connection, c


def main():
    connection, cursor = connect_to_db()

    skus = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    rename_columns = {
        "sku_id": "SKU ID",
        "name": "Name",
        "description": "Description",
        "quantity": "Quantity",
        "location": "Location"
    }
    column_names = [rename_columns.get(col, col.replace('_', ' ').title()) for col in column_names]

    main_table = pd.DataFrame(skus, columns = column_names)
    
    st.table(main_table)

    connection.close()


main()
