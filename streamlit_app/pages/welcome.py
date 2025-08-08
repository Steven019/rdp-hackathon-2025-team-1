import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st


def connect_to_db():
    connection = sqlite3.connect('./db/warehouse_data.db')
    c = connection.cursor()
    return connection, c

def create_data_table():
    connection, cursor = connect_to_db()

    cursor.execute('SELECT s.sku_id, s.product_name, s.product_number, s.destination, s.pallets, s.weight_lbs,'\
                   'ds.staging_lane, ds.days_of_service, ds.dock_aging_hours, ds.last_refresh from skus s JOIN dock_status ds where s.sku_id = ds.sku_id')
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
        "dock_aging_hours": "Dock Aging Hours",
        "last_refresh": "Last Refresh"
    }
    column_names = [rename_columns.get(col, col.replace('_', ' ').title()) for col in column_names]

    main_table = pd.DataFrame(joined_table, columns = column_names)

    connection.close()

    return main_table, column_names


def main():
    st.set_page_config(layout="wide")

    st.title("GSC Dock Status Display")

    st.subheader("This program allows you to check on the status of items on docks for different facilities.")

    main_table, column_names = create_data_table()
    # Layout: two columns for filters, table below as wide as possible
    left_col, right_col = st.columns([2,1])

    with left_col:
        column_select = st.multiselect("Search in column", options=column_names, key="col_select")
        item_searching = st.text_input("Search for", key="item_search")
        col_search, col_clear = st.columns([2,1])
        with col_search:
            search_clicked = st.button("Search", key="search_btn")
        with col_clear:
            clear_clicked = st.button("Clear Filter", key="clear_filter_btn")

    with right_col:
        sort_col = st.selectbox("Sort by column", options=column_names, key="sort_col")
        sort_asc = st.radio("Sort order", ["Ascending", "Descending"], index=0, key="sort_order")

    def days_under_two(val):
        color = 'red' if val < 2 else ''
        return f'background-color: {color}'
    
    def high_dock_aging_alert(val):
        color = 'yellow' if val >= 6 else ''
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
    if clear_clicked:
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


# Store critical_clicked in session state for page logic
if 'critical_clicked' not in st.session_state:
    st.session_state['critical_clicked'] = False

st.sidebar.header('Select Facility')
selected_facility = st.sidebar.selectbox('Facility', ['Lebanon, Pa','Orlando, Fl', 'Morrow, Ga', ])


st.sidebar.header('Critical Alerts')

# Button to view all critical alerts from main table
view_all_critical_main = st.sidebar.button("View All Critical Alerts (Main Table)", key="view_all_critical_main")

if st.session_state['critical_clicked']:
    table_for_sidebar = st.session_state.get('filtered_table')
    if table_for_sidebar is not None and 'Days of Service' in table_for_sidebar.columns:
        critical_skus = table_for_sidebar[table_for_sidebar['Days of Service'] < 2]
        st.session_state['filtered_table'] = critical_skus
        st.session_state['search_active'] = True
        st.sidebar.success(f"Showing {critical_skus.shape[0]} critical SKUs with Days of Service < 2.")
        st.dataframe(critical_skus)
    else:
        st.sidebar.warning("No data available for critical SKUs.")


        
elif view_all_critical_main:
    try:
        main_table_btn, column_names = create_data_table()
    except Exception:
        main_table_btn = None

    if main_table_btn is not None and 'Days of Service' in main_table_btn.columns:
        critical_skus_main = main_table_btn[main_table_btn['Days of Service'] < 2]
        st.subheader("All Critical SKUs")
        st.dataframe(critical_skus_main)
        # CSV download button for critical SKUs
        csv = critical_skus_main.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Critical SKUs as CSV",
            data=csv,
            file_name="critical_skus.csv",
            mime="text/csv"
        )
        st.markdown("---")

        column_names = list(main_table_btn.columns)
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
            st.session_state['filtered_table'] = main_table_btn.copy()
            st.session_state['search_active'] = False
        if search_clicked:
            if column_select and item_searching:
                matched_row = main_table_btn[column_select].apply(lambda row: row.astype(str).str.contains(item_searching, case=False, na=False), axis=1)
                if isinstance(matched_row, pd.DataFrame):
                    matched_row = matched_row.any(axis=1)
                filtered_table = main_table_btn[matched_row]
                st.session_state['filtered_table'] = filtered_table
                st.session_state['search_active'] = True
                num_matches = filtered_table.shape[0]
                if num_matches < 1:
                    st.warning(f"Found no matching rows.")
                else:
                    st.success(f"Found {num_matches} matching rows.")
            else:
                st.warning("Please select at least one column and enter a search term.")
                st.session_state['filtered_table'] = main_table_btn.copy()
                st.session_state['search_active'] = False
        # Always sort the currently filtered results
        if st.session_state.get('search_active', False):
            table_to_show = st.session_state['filtered_table']
        else:
            table_to_show = main_table_btn
        ascending = True if sort_asc == "Ascending" else False
        table_to_show = table_to_show.sort_values(by=sort_col, ascending=ascending)
        st.subheader("Main Table")
        st.dataframe(table_to_show.style.applymap(days_under_two, subset=['Days of Service']))
    else:
        st.warning("No data available for critical SKUs.")
else:
    main()

main_table = None
if 'main_table' in st.session_state:
    main_table = st.session_state['main_table']
else:

    try:
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
        connection.close()
    except Exception:
        main_table = None

if main_table is not None and 'Days of Service' in main_table.columns:
    critical_skus = main_table[main_table['Days of Service'] < 2]
    st.sidebar.subheader("SKUs with less than 2 Days of Service")
    if not critical_skus.empty:
        for _, row in critical_skus.iterrows():
            st.sidebar.write(
                f":red[:material/Warning:] {row.get('Product Name', '')}, SKU ID: {row.get('SKU ID', '')}, Days of Service: {row['Days of Service']}"
            )
    else:
        st.sidebar.write("No critical SKUs found.")
else:
    st.sidebar.write("No data available for critical SKUs.")
