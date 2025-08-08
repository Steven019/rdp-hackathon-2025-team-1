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

    # Layout: two columns for filters, table below as wide as possible
    left_col, right_col = st.columns([2,1])

    with left_col:
        column_select = st.multiselect("Search in column", options=column_names, key="col_select")
        item_searching = st.text_input("Search for", key="item_search")
        search_clicked = st.button("Search", key="search_btn")

    with right_col:
        sort_col = st.selectbox("Sort by column", options=column_names, key="sort_col")
        sort_asc = st.radio("Sort order", ["Ascending", "Descending"], index=0, key="sort_order")

    def days_under_two(val):
        color = 'red' if val < 2 else ''
        return f'background-color: {color}'

    # Use session state to persist filtered results
    if 'filtered_table' not in st.session_state:
        st.session_state['filtered_table'] = main_table.copy()
        st.session_state['search_active'] = False

    if search_clicked:
        if column_select and item_searching:
            matched_row = main_table[column_select].apply(lambda row: row.astype(str).str.contains(item_searching, case=False, na=False), axis=1)
            if isinstance(matched_row, pd.DataFrame):
                matched_row = matched_row.any(axis=1)
            filtered_table = main_table[matched_row]
            st.session_state['filtered_table'] = filtered_table
            st.session_state['search_active'] = True
            num_matches = filtered_table.shape[0]
            if num_matches < 1:
                st.warning(f"Found no matching rows.")
            else:
                st.success(f"Found {num_matches} matching rows.")
        else:
            st.warning("Please select at least one column and enter a search term.")
            st.session_state['filtered_table'] = main_table.copy()
            st.session_state['search_active'] = False

    # Always sort the currently filtered results
    if st.session_state.get('search_active', False):
        table_to_show = st.session_state['filtered_table']
    else:
        table_to_show = main_table

    ascending = True if sort_asc == "Ascending" else False
    table_to_show = table_to_show.sort_values(by=sort_col, ascending=ascending)

    st.dataframe(table_to_show.style.applymap(days_under_two, subset=['Days of Service']))

    #st.dataframe(main_table, hide_index=True)

    connection.close()


main()
