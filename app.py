import pandas as pd
import streamlit as st

from sources.utils import compile_dataframe
from targets.utils import make_form_url_from_series, make_form_url_from_plate

plate_search, desc_search = st.columns(2)

with plate_search:
    plate_search_string = st.text_input("Plate", help="Enter _complete_ plate for 'New Plate' submission button").upper()

with desc_search:
    vehicle_search_string = st.text_input("Vehicle", help="Search Vehicle Description").upper()

st.caption("Use the above fields to search.")

melt_plates_df = compile_dataframe(st.secrets.sources)


melt_plates_df = melt_plates_df[
    (
        melt_plates_df["Plate"].str.upper().str.contains(plate_search_string.strip(), na=False)
        & melt_plates_df["Vehicle"]
        .str.upper()
        .str.contains(vehicle_search_string, na=False)
    )
]

name = st.query_params.get("name","")

if melt_plates_df.shape[0] > 0:
    
    event = st.dataframe(
        melt_plates_df,
        column_order=("Timestamp", "State_Plate", "Vehicle"),
        column_config={
            "Timestamp": "Last Seen",
            "State_Plate": "Plate",
            "Vehicle": "Vehicle Description",
        },
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True,
    )

    info_str = """
      Please use your obeservations on the gound
      to verify identities as rentals have been used
    """
    st.info(info_str)

    if len(event.selection.rows) > 0:

        selected = event.selection.rows
        selected_df = melt_plates_df.iloc[selected]
        selected_info = selected_df["Info"].iloc[0]
        form_url = make_form_url_from_series(st.secrets.target_form, selected_df, name)
        st.link_button(label="Submit Incident", url=form_url)
        st.write(selected_info)
        with st.expander("details"):
            st.dataframe(selected_df.transpose())

    else:
        st.caption("select record for more info and form submittions button...")

else:
    st.text("No matching records")
    series = pd.Series(data={"Plate": plate_search_string})
    form_url = make_form_url_from_plate(st.secrets.target_form, plate_search_string, name)
    st.link_button(label="Submit New Plate", url=form_url)
