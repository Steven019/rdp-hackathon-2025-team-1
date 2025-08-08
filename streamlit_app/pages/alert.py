import sqlite3
from datetime import datetime
import pandas as pd

import streamlit as st


def connect_to_db():
    connection = sqlite3.connect('./db/warehouse_data.db')
    c = connection.cursor()
    c.execute('SELECT * FROM alerts')
    #connection.commit()
    return connection, c


def alert_page():
    connection, cursor = connect_to_db()

    alerts = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    rename_columns = {
        "alert_id": "Alert ID",
        "pipeline_id": "Pipeline ID",
        "sku_id": "SKU ID",
        "stage": "Stage",
        "status": "Status",
        "start_time": "Start Time",
        "end_time": "End Time",
        "message": "Message",
        "created_at": "Created At"
    }
    column_names = [rename_columns.get(col, col.replace('_', ' ').title()) for col in column_names]

    main_table = pd.DataFrame(alerts, columns = column_names)
    
    st.table(main_table)

    connection.close()


alert_page()