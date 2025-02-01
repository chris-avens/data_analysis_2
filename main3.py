import streamlit as st
import pandas as pd

# Sample data for the table
data = {
    "ID": [1, 2, 3],
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "Department": ["HR", "Engineering", "Marketing"],
}
df = pd.DataFrame(data)

# Initialize session state to track the selected row
if "selected_row" not in st.session_state:
    st.session_state["selected_row"] = None

# Function to handle row selection
def select_row(row_index):
    st.session_state["selected_row"] = row_index

# UI Layout
if st.session_state["selected_row"] is None:
    # Single column view
    st.write("Click on a row to see details")
    for index, row in df.iterrows():
        if st.button(f"Select Row {index + 1}", key=f"row-{index}"):
            select_row(index)
else:
    # Two-column view
    col1, col2 = st.columns(2)

    with col1:
        st.write("Table:")
        for index, row in df.iterrows():
            if st.button(f"Select Row {index + 1}", key=f"row-{index}"):
                select_row(index)

    with col2:
        selected_row_data = df.iloc[st.session_state["selected_row"]]
        st.write("Row Details:")
        st.json(selected_row_data.to_dict())


df = pd.DataFrame(
    [
       {"command": "st.selectbox", "rating": 4, "is_widget": True},
       {"command": "st.balloons", "rating": 5, "is_widget": False},
       {"command": "st.time_input", "rating": 3, "is_widget": True},
   ]
)
edited_df = st.data_editor(df)

# favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
# st.markdown(f"Your favorite command is **{favorite_command}** 🎈")