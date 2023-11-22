# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 06:14:48 2023

@author: Abdullah Syafiq
"""
import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from math import ceil, floor

# %%
def roundup(x):
    return int(ceil(x * 2 / 1000.0)) * 1000 / 2


def rounddown(x):
    return int(floor(x / 100.0)) * 100


def roundup10(x):
    return int(ceil(x * 2 / 10.0)) * 10 / 2


def rounddown10(x):
    return int(floor(x / 10.0)) * 10


req_table = {
    "File": ["amplification primary curve data", "melting data", "reaction id data"],
    "Extension": ["csv", "txt", "csv"],
    "Source": [
        "Results tab",
        "Output tab",
        "Self made, check github for an example file",
    ],
}

st.set_page_config(layout="wide", page_title="qPCR explorer")
# Hide deploy button
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

# Functions for each of the pages
def home(uploaded_file):
    if uploaded_file:
        st.header("Begin exploring the data using the menu on the left")
    else:
        st.header("To begin please upload following files:")
        st.table(req_table)


def amp_df():
    st.write("Amplification data")
    st.dataframe(amp)


def melt_df():
    st.write("Melting temperature data")
    st.dataframe(melt)


def melt_plot():
    # data processing
    temp_diff = melt.columns[2:].to_numpy(dtype=np.float32)  # extract temp

    delta = melt.iloc[:, 2:]  # remove first two column
    delta = delta.diff(periods=-1, axis=1)  # calculate diff
    delta = delta.iloc[:, 1:-1]  # remove first and last column
    melt_deriv = delta / (temp_diff[1] - temp_diff[0])  # calculate first derivative

    # merge with id data
    melt_deriv = pd.concat([melt_deriv, reaction_id], axis=1)

    # wide to long
    melt_deriv = melt_deriv.melt(
        id_vars=reaction_id.columns, var_name="temp", value_name="first_derivative"
    )
    melt_deriv["group_target"] = melt_deriv["group"] + "_" + melt_deriv["target"]

    # min max for axis
    y_max = melt_deriv["first_derivative"].max()
    y_min = melt_deriv["first_derivative"].min()

    # options list
    filter_with_options = reaction_id.columns.tolist()
    filter_with_options.remove("target")
    plotly_palette = [
        x
        for x in dir(px.colors.qualitative)
        if not (x.startswith("__") or x.startswith("_"))
    ]
    plotly_palette.remove("swatches")
    avail_themes = [
        "ggplot2",
        "seaborn",
        "simple_white",
        "plotly",
        "plotly_white",
        "plotly_dark",
        "presentation",
        "xgridoff",
        "ygridoff",
        "gridon",
        "none",
    ]

    # header
    st.markdown(
        "<h1 style='text-align: center; color: black;'>Melting curve</h1>",
        unsafe_allow_html=True,
    )
    st.subheader("Data options")
    # filter options
    col1, col2, col3 = st.columns(3)

    target_filter = col1.selectbox("Target:", options=melt_deriv["target"].unique())
    # target_filter = col1.multiselect('Target:', options=melt_deriv['target'].unique(),default=melt_deriv['target'].unique()[0])

    col1_container = col1.container()
    col3_container = col3.container()

    # declare initial state
    if "select_all_btn" not in st.session_state:
        st.session_state["select_all_btn"] = False
    all = col3.checkbox("Select all")

    col1_2, col2_2, col3_2 = st.columns(3)
    default_all = col1_2.checkbox("Default filter")

    st.subheader("Theme options")
    col1_3, col2_3, _ = st.columns(3)
    col1_container_theme = col1_3.container()
    col2_container_palette = col2_3.container()
    palette = col1_container_theme.selectbox(
        "Color palette:", options=plotly_palette, index=plotly_palette.index("Plotly")
    )
    theme = col2_container_palette.selectbox(
        "Theme:", options=avail_themes, index=avail_themes.index("none")
    )

    if default_all:
        filter_with = col2.selectbox(
            "Filter by:",
            options=filter_with_options,
            index=filter_with_options.index("group"),
        )
        filter_options = col3_container.multiselect(
            "Filter options:",
            melt_deriv[filter_with].unique(),
            melt_deriv[filter_with].unique(),
        )

        st.session_state["select_all_btn"] = not st.session_state["select_all_btn"]
        color_group = col1_container.selectbox(
            "Color by:",
            options=filter_with_options,
            index=filter_with_options.index("id"),
        )
        line_dash_group = col2.selectbox(
            "Line dash by:",
            options=filter_with_options,
            index=filter_with_options.index("replicate"),
        )

    else:
        filter_with = col2.selectbox("Select filter:", options=filter_with_options)

        if all:
            st.session_state["select_all_btn"] = not st.session_state["select_all_btn"]
            filter_options = col3_container.multiselect(
                "Filter options:",
                melt_deriv[filter_with].unique(),
                melt_deriv[filter_with].unique(),
            )
        else:
            filter_options = col3_container.multiselect(
                "Filter options:", melt_deriv[filter_with].unique()
            )
            color_group = col1_container.selectbox(
                "Color by:", options=filter_with_options
            )
            line_dash_group = col2.selectbox(
                "Line dash by:", options=filter_with_options
            )

    # %%
    # filter_options = col3.multiselect('Filter options', options=melt_deriv[filter_with].unique())

    filtered_df = melt_deriv[
        (melt_deriv[filter_with].isin(filter_options))
        & (melt_deriv["target"] == target_filter)
    ]
    # multi select target
    # filtered_df = melt_deriv[(melt_deriv[filter_with].isin(filter_options)) & (melt_deriv['target'].isin(target_filter))]

    plot = px.line(
        filtered_df,
        x="temp",
        y="first_derivative",
        color=color_group,  #'id_combined',
        line_dash=line_dash_group,
        # line_dash  = 'group',
        # line_group  = 'target',
        # symbol='dilution',
        labels={
            "temp": "Temperature",
            "first_derivative": "Fluoroscence (1st Derivative)",
        },
        title=f"Melting curve of {target_filter}",
        template=theme,
        color_discrete_sequence=getattr(px.colors.qualitative, palette),
    )
    # %%
    plot.update_yaxes(
        showline=True,
        zeroline=False,
        range=[rounddown(y_min), roundup(y_max)],
        color="black",
    )
    plot.update_xaxes(showline=True, color="black")

    plot.update_layout(
        title={"xanchor": "center", "yanchor": "top"},
        # plot_bgcolor='white'
    )

    st.plotly_chart(plot, use_container_width=True)

    # Create an in-memory buffer
    with io.BytesIO() as buffer:
        # Write plot to buffer png
        plot.write_image(file=buffer, format="png", engine="kaleido", scale=2)
        # button to download image
        st.download_button(
            label="Download plot",
            data=buffer,
            file_name=f"Melting curve of {target_filter}.png",
            # mime="application/pdf",
            mime="image/png",
        )

    # # Create an in-memory buffer
    # buffer = io.BytesIO()
    # # Write plot to buffer png
    # plot.write_image(file=buffer, format="png"
    # , engine="orca", scale=2
    # )
    # # button to download image
    # st.download_button(
    # label="Download plot",
    # data=buffer,
    # file_name=f'Melting curve of {target_filter}.png',
    # mime="image/png",
    # )
    # #buffer.close()


def amp_primary_plot():
    amp2 = amp.iloc[:, 5:]  # remove first five columns
    amp2 = pd.concat([amp2, reaction_id], axis=1)  # merge with reaction id data
    amp2 = amp2.melt(
        id_vars=reaction_id.columns, var_name="cycle", value_name="amplification"
    )
    amp2["group_target"] = amp2["group"] + "_" + amp2["target"]

    # min max for axis
    y_max = amp2["amplification"].max()
    y_min = amp2["amplification"].min()

    # options list
    filter_with_options = reaction_id.columns.tolist()
    filter_with_options.remove("target")
    plotly_palette = [
        x
        for x in dir(px.colors.qualitative)
        if not (x.startswith("__") or x.startswith("_"))
    ]
    plotly_palette.remove("swatches")
    avail_themes = [
        "ggplot2",
        "seaborn",
        "simple_white",
        "plotly",
        "plotly_white",
        "plotly_dark",
        "presentation",
        "xgridoff",
        "ygridoff",
        "gridon",
        "none",
    ]

    # header
    st.markdown(
        "<h1 style='text-align: center; color: black;'>Melting curve</h1>",
        unsafe_allow_html=True,
    )
    st.subheader("Data options")
    # filter options
    col1, col2, col3 = st.columns(3)

    target_filter = col1.selectbox("Target:", options=amp2["target"].unique())
    # target_filter = col1.multiselect('Target:', options=melt_deriv['target'].unique(),default=melt_deriv['target'].unique()[0])

    col1_container = col1.container()
    col3_container = col3.container()

    # declare initial state
    if "select_all_btn" not in st.session_state:
        st.session_state["select_all_btn"] = False
    all = col3.checkbox("Select all")

    col1_2, col2_2, col3_2 = st.columns(3)
    default_all = col1_2.checkbox("Default filter")

    st.subheader("Theme options")
    col1_3, col2_3, _ = st.columns(3)
    col1_container_theme = col1_3.container()
    col2_container_palette = col2_3.container()
    palette = col1_container_theme.selectbox(
        "Color palette:", options=plotly_palette, index=plotly_palette.index("Plotly")
    )
    theme = col2_container_palette.selectbox(
        "Theme:", options=avail_themes, index=avail_themes.index("none")
    )

    if default_all:
        filter_with = col2.selectbox(
            "Filter by:",
            options=filter_with_options,
            index=filter_with_options.index("group"),
        )
        filter_options = col3_container.multiselect(
            "Filter options:", amp2[filter_with].unique(), amp2[filter_with].unique()
        )

        st.session_state["select_all_btn"] = not st.session_state["select_all_btn"]
        color_group = col1_container.selectbox(
            "Color by:",
            options=filter_with_options,
            index=filter_with_options.index("id"),
        )
        line_dash_group = col2.selectbox(
            "Line dash by:",
            options=filter_with_options,
            index=filter_with_options.index("replicate"),
        )

    else:
        filter_with = col2.selectbox("Select filter:", options=filter_with_options)

        if all:
            st.session_state["select_all_btn"] = not st.session_state["select_all_btn"]
            filter_options = col3_container.multiselect(
                "Filter options:",
                amp2[filter_with].unique(),
                amp2[filter_with].unique(),
            )
        else:
            filter_options = col3_container.multiselect(
                "Filter options:", amp2[filter_with].unique()
            )
            color_group = col1_container.selectbox(
                "Color by:", options=filter_with_options
            )
            line_dash_group = col2.selectbox(
                "Line dash by:", options=filter_with_options
            )

    # %%
    # filter_options = col3.multiselect('Filter options', options=melt_deriv[filter_with].unique())

    filtered_df = amp2[
        (amp2[filter_with].isin(filter_options)) & (amp2["target"] == target_filter)
    ]
    # multi select target
    # filtered_df = melt_deriv[(melt_deriv[filter_with].isin(filter_options)) & (melt_deriv['target'].isin(target_filter))]
    # amp3 = amp.iloc[:,5:]
    # st.dataframe(amp)
    # st.dataframe(amp3)
    # st.dataframe(amp2)
    # st.write(y_max, y_min)
    plot = px.line(
        filtered_df,
        x="cycle",
        y="amplification",
        color=color_group,  #'id_combined',
        line_dash=line_dash_group,
        # line_dash  = 'group',
        # line_group  = 'target',
        # symbol='dilution',
        labels={"temp": "Temperature", "amplification": "Fluoroscence (primary curve)"},
        title=f"Amplification curve of {target_filter}",
        template=theme,
        color_discrete_sequence=getattr(px.colors.qualitative, palette),
    )
    # %%
    plot.update_yaxes(
        showline=True,
        zeroline=False,
        range=[rounddown10(y_min), roundup10(y_max)],
        color="black",
    )
    plot.update_xaxes(showline=True, color="black")

    plot.update_layout(
        title={"xanchor": "center", "yanchor": "top"},
        # plot_bgcolor='white'
    )

    st.plotly_chart(plot, use_container_width=True)

    # Create an in-memory buffer
    with io.BytesIO() as buffer:
        # Write plot to buffer png
        plot.write_image(file=buffer, format="png", engine="kaleido", scale=2)
        # button to download image
        st.download_button(
            label="Download plot",
            data=buffer,
            file_name=f"Amplification curve of {target_filter}.png",
            # mime="application/pdf",
            mime="image/png",
        )


# %%
# Add a title and intro text
st.title("qPCR results explorer")
st.text("Welcome to Abdullah's qPCR results explorer webApp")
st.write("---")
# Sidebar setup
st.sidebar.title("File upload")
# upload_file_amp = st.sidebar.file_uploader('Upload a file containing qPCR amplification data')
upload_file_amp_primary = st.sidebar.file_uploader(
    "Upload a file containing qPCR **amplification primary curve** data",
    type = ["csv"]
)
upload_file_melt = st.sidebar.file_uploader(
    "Upload a file containing qPCR **melting** data",
    type = ["txt", "tsv"]
)
upload_file_reaction_id = st.sidebar.file_uploader(
    "Upload a file containing qPCR **reaction id** data",
    type = ["csv"]
)

# Sidebar navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio(
    "Select what you want to display:",
    [
        "Home",
        "Melting curve",
        "Amplification primary curve",
        "Melting data",
        "Amplification data",
    ],
)
# %%
# Check if file has been uploaded
if (
    (upload_file_amp_primary is not None)
    & (upload_file_melt is not None)
    & (upload_file_melt is not None)
):
    # amp = pd.read_csv(upload_file_amp, sep = '\t')
    amp = pd.read_csv(upload_file_amp_primary)
    melt = pd.read_csv(upload_file_melt, sep="\t")
    reaction_id = pd.read_csv(upload_file_reaction_id)

# Navigation options
if options == "Home":
    home(upload_file_amp_primary)
elif options == "Melting curve":
    melt_plot()
elif options == "Amplification primary curve":
    amp_primary_plot()
elif options == "Melting data":
    melt_df()
elif options == "Amplification data":
    amp_df()
