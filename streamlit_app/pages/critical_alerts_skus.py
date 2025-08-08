import streamlit as st

st.subheader("The following SKUs have critical alerts:")

table_for_sidebar = st.session_state.get('filtered_table')
if table_for_sidebar is not None and 'Days of Service' in table_for_sidebar.columns:
    critical_skus = table_for_sidebar[table_for_sidebar['Days of Service'] < 2]
    st.dataframe(critical_skus)
else:
    st.warning("No data available for critical SKUs.")
