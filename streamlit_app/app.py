import traceback

import streamlit as st

from streamlit_app._logger import log, logging_config


@st.cache_resource
def _configure_logging() -> None:
    logging_config()
    log.info("Starting application...")



def main() -> None:
    welcome = st.Page("pages/welcome.py", title="Welcome", icon=":material/home:", default=True)
    dock_status = st.Page("pages/dock_status.py", title="Dock Status", icon=":material/dock:", default=False)
    production_pipeline = st.Page("pages/production_pipeline.py", title="Production Pipeline", icon=":material/pipeline:", default=False)
    alerts = st.Page("pages/alert.py", title="Alerts", icon=":material/alert:", default=False)

    pg = st.navigation(
        {
            "App": [welcome], 
            "Tables": [dock_status, production_pipeline, alerts],
        }
    )

    pg.run()


if __name__ == "__main__":
    try:
        _configure_logging()
        main()
    except Exception as e:
        log.critical(traceback.format_exc())
        raise e

st.title("Warehouse Dashboard")
st.write("Welcome! Use the sidebar to select a page and view data.")
