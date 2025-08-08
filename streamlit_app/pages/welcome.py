import sqlite3
from datetime import datetime
import pandas as pd

import streamlit as st


def connect_to_db():
    connection = sqlite3.connect('./db/warehouse_data.db')
    c = connection.cursor()
    return connection, c


def main():
    st.set_page_config(layout="wide")

    st.title("Temp Title")

    st.header("A Description of the Program")


    connection, cursor = connect_to_db()

    cursor.execute('SELECT s.sku_id, s.product_name, s.product_number, s.destination, s.pallets, s.weight_lbs,'\
                   'ds.staging_lane, ds.days_of_service, ds.dock_location, ds.last_refresh from skus s JOIN dock_status ds where s.sku_id = ds.sku_id')
    joined_table = cursor.fetchall()

    column_names = [i[0] for i in cursor.description]
    rename_columns = {
        "sku_id": "SKU ID",
        "name": "Name",
        "description": "Description",
        "quantity": "Quantity",
        "location": "Location",
        "staging_lane": "Lane",
        "days_of_service": "Days of Service",
        "dock_location": "Dock Location",
        "last_refresh": "Last Refresh"
    }
    column_names = [rename_columns.get(col, col.replace('_', ' ').title()) for col in column_names]

    main_table = pd.DataFrame(joined_table, columns = column_names)

    #st.text_input("Search by",width=500)
    column_select = st.multiselect("Search in column", options=column_names, width=400)
    item_searching = st.text_input("Search for", width=400)

    filtered_table = main_table.copy()
    if st.button("Search"):
        if column_select and item_searching:

            match_row = filtered_table[column_select].apply(lambda row: row.astype(str).str.contains(item_searching, case=False, na=False), axis=1)

            if isinstance(match_row, pd.DataFrame):
                match_row = match_row.any(axis=1)
            filtered_table = filtered_table[match_row]
            st.success(f"Found {filtered_table.shape[0]} matching rows.")
        else:
            st.warning("Please select at least one column and enter a search term.")
        st.dataframe(filtered_table, hide_index=True)
    else:
        st.dataframe(main_table, hide_index=True)

    st.dataframe(main_table, hide_index=True)

    connection.close()


main()
