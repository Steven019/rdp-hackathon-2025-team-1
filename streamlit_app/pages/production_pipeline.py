import sqlite3
from datetime import datetime
import pandas as pd

import streamlit as st


def connect_to_db():
    connection = sqlite3.connect('./db/warehouse_data.db')
    c = connection.cursor()
    c.execute('SELECT * FROM production_pipeline')
    #connection.commit()
    return connection, c


def production_pipeline_page():
    connection, cursor = connect_to_db()

    production_pipeline = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    rename_columns = {
        "pipeline_id": "Pipeline ID",
        "sku_id": "SKU ID",
        "stage": "Stage",
        "status": "Status",
        "start_time": "Start Time",
        "end_time": "End Time"
    }
    column_names = [rename_columns.get(col, col.replace('_', ' ').title()) for col in column_names]

    main_table = pd.DataFrame(production_pipeline, columns = column_names)
    
    st.table(main_table)

    connection.close()

production_pipeline_page()