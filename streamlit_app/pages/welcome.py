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

    main_table = pd.DataFrame(skus)

    st.table(main_table)

    connection.close()


main()
