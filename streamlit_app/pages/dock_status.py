import sqlite3
from datetime import datetime
import pandas as pd

import streamlit as st


def connect_to_db():
    connection = sqlite3.connect('./db/warehouse_data.db')
    c = connection.cursor()
    c.execute('SELECT * FROM dock_status')
    #connection.commit()
    return connection, c


def dock_status_page():
    connection, cursor = connect_to_db()

    dock_status = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    rename_columns = {
        "dock_id": "Dock ID",
        "status": "Status",
        "last_updated": "Last Updated",
        "assigned_truck": "Assigned Truck"
    }
    column_names = [rename_columns.get(col, col.replace('_', ' ').title()) for col in column_names]

    main_table = pd.DataFrame(dock_status, columns = column_names)
    
    st.table(main_table)

    connection.close()


dock_status_page()
