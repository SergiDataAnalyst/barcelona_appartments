import pandas as pd
import pydeck as pdk
import streamlit as st
from streamlit_option_menu import option_menu


st.set_page_config(layout="wide", page_title="Apartment Visualization", page_icon=":house:")



@st.cache_data
def load_data():
    # Replace with your actual data file path or URL
    df = pd.read_csv("barcelona_selling_cleaned.csv")
    df = df.dropna(subset=['price'])
    print(df.head(4))
    return df


def handle_click(event):
    clicked_coordinates = event["coordinates"]
    st.session_state["clicked_coordinates"] = clicked_coordinates


def filter_df(df, price_range, filter_options):
    df = df[df['surface'] < 900]
    df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
    columns_to_check = filter_options
    mask = df[columns_to_check].eq(1).all(axis=1)
    df = df[mask]
    count = len(df) if not df.empty else 0
    mean = int(df['price'].mean()) if not df.empty else 0
    mean_price_sqm = int((df['price'] / df['surface']).mean()) if not df.empty else 0
    return count, mean, mean_price_sqm


# Function to display map
def mapping(df, lat, lon, zoom):
    min_price = df['price'].min()
    max_price = df['price'].max()
    df['normalized_price'] = (df['price'] - min_price) / (max_price - min_price)

    def price_to_color(normalized_price):
        # Red stays at 255
        red = 255
        # Interpolate green between 0 and 255
        green = int((1-normalized_price) * 255)
        # Blue is always 0
        blue = 0
        # Alpha value
        alpha = 180
        return [red, green, blue, alpha]

    df['color'] = df['normalized_price'].apply(price_to_color)
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v8",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },

        layers=[
            pdk.Layer(
           "ColumnLayer",
                data=df,
                get_position=["long", "lat"],
                radius=100,
                get_elevation="price_mean_100m",
                elevation_scale=0.002,
                get_fill_color="color",
                pickable=True,
                extruded=True,  # 3D (Mandatory)
                auto_highlight=True,
            ),
        ],
        tooltip={
            "html": "<b>Price:</b> {price_mean_50m}€ <b>RGB color is:</b> {color}",
            "style": {
                "color": "white"
            }
        }
    ))


def mapping_hexagon(df, lat, lon, zoom):
    min_price = df['price'].min()
    max_price = df['price'].max()
    df['normalized_price'] = (df['price'] - min_price) / (max_price - min_price)
    price_mean_50m = df['price_mean_50m']

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v8",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
           "HexagonLayer",
                df,
                get_position=["long", "lat"],
                auto_highlight=True,
                radius=100,
                elevation_scale=5,
                pickable=True,
                elevation_range=[0, 300],
                extruded=True,
                coverage=1,
            ),
        ],
        tooltip={
            "html": f"<b>{min_price}</b>",
            "style": {
                "color": "white"
            }
        }
    ))
    return


def mapping_heatmap(df, lat, lon, zoom):
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v8",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },

        layers=[
            pdk.Layer(
                "HeatmapLayer",
                data=df,
                get_position=["long", "lat"],
                opacity=0.3,
                threshold=0.05,
                aggregation="MEAN",
                get_weight="price",

            ),
        ],
        tooltip={
            "html": "<b>Price:</b> {price_mean_50m}€ <b>RGB color is:</b> {color}",
            "style": {
                "color": "white"
            }
        }
    ))


def mapping_scatter(df, lat, lon, zoom, price_range, filter_options, surface_range):

    # filtering the df
    if not df.empty:
        df = df[(df['surface'] < 1801) & (df['surface'] > 19)]
        df = df[(df['surface'] >= surface_range[0]) & (df['surface'] <= surface_range[1])]
        df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
        columns_to_check = filter_options
        mask = df[columns_to_check].eq(1).all(axis=1)
        df = df[mask]

        min_price = price_range[1]
        max_price = price_range[0]
        df['normalized_price'] = (df['price'] - min_price) / (max_price - min_price)

        def price_to_color_green(normalized_price):

            green = [109, 255, 45]
            red = [255, 115, 45]
            red_component = int(green[0] + (red[0] - green[0]) * normalized_price)
            green_component = int(green[1] + (red[1] - green[1]) * normalized_price)
            blue_component = int(green[2] + (red[2] - green[2]) * normalized_price)
            # Alpha value
            alpha = 180
            return [red_component, green_component, blue_component, alpha]

        df['color'] = df['normalized_price'].apply(price_to_color_green)
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v8",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 50,
            },

            layers=[
                pdk.Layer(
               "ScatterplotLayer",
                    data=df,
                    get_position=["long", "lat"],
                    radius_scale=50,
                    get_elevation="price_mean_100m",
                    elevation_scale=0.002,
                    get_fill_color="color",
                    pickable=True,
                    extruded=True,  # 3D (Mandatory)
                    auto_highlight=True,
                ),
            ],
            tooltip={
                "html": "<b>Mean price in the area is:</b> {price_mean_50m}€",
                "style": {
                    "color": "white"
                }
            }
        ))
    if df.empty or not all(item in df.columns for item in filter_options):
        st.write("No results found")
    return


# Main app layout
data = load_data()

st.title("🏠 Apartment Price Explorer. In development 🔧")
df2 = pd.read_csv("barcelona_selling_cleaned.csv")
df2 = df2.dropna(subset=['price'])

selected = option_menu(menu_title=None, options=["City Overview", "Supply and Demand Map", " 🥇 Top"],
                       icons=["map", "bar-chart", ""],
                       orientation="horizontal",)

if selected == "City Overview":

    row1_1, row1_2, row1_3, row1_4 = st.columns((2, 1, 1, 1))

    with row1_1:
        st.markdown("""
        ### How to Use This App
        - **Adjust Filters**: Select your desired price range, surface area, and features.
        - **Apply Filters**: Click the 'Apply Filters' button to update the map and listings.
        - **Explore Results**: View the updated map and listings based on your selections.
        """)

    with row1_2:
        st.header("Price selector")
        values = st.slider("Select price in euros", int(df2['price'].min()), 2000000, (75000, 450000),
                           step=1000,  key="mean_price")

    with row1_3:
        st.header("Amenities selector")
        options = st.multiselect(
            'Filter by feature',
            ['elevator', 'terrace', 'balcony', 'air-conditioning', 'heater'],
            ['elevator', 'air-conditioning'],)

    with row1_4:
        st.subheader("Surface selector")
        surface = st.slider("Select the surface range", 20, 300, (55, 120),
                            step=1, key="surface")

    row2_1, row2_2, row2_3 = st.columns((2, 2, 1))

    with row2_1:
        st.header("Add Density Map")
        midpoint = (data["lat"].mean(), data["long"].mean())
        mapping_hexagon(data, midpoint[0], midpoint[1], 12)

    with row2_2:
        st.header("Search results view")
        midpoint = (data["lat"].mean(), data["long"].mean())
        mapping_scatter(data, midpoint[0], midpoint[1], 12, values, options, surface)

    with row2_3:
        count, mean, mean_price_sqm = filter_df(data, values, options)
        st.header("Search results summary")
        st.subheader(f"There are {count} apartments")
        st.divider()
        st.subheader(f"Mean price is {mean}€")
        st.divider()
        st.subheader(f"Mean price per sqm is {mean_price_sqm}€")


if selected == "Supply and Demand Map":

    row1_1, row1_2, row1_3, row1_4 = st.columns((2, 1, 1, 1))

    with row1_1:
        st.header("Price range selector")
        hour_selected = st.slider(
            "Select price range", 0, 23, key="price_range_scatter")

    with row1_2:
        st.header("Price selector")
        values = st.slider("Select price in euros", int(df2['price'].min()), int(df2['price'].max()), (75000, 200000),
                           step=100,  key="mean_price_scatter")

    with row1_3:
        st.header("Amenities selector")
        options = st.multiselect(
            'Filter by feature',
            ['elevator', 'terrace', 'balcony', 'air-conditioning', 'heater'],
            ['elevator', 'air-conditioning'],)

    with row1_4:
        st.subheader("Surface selector")
        surface = st.slider("Select the surface range", 20, 1800, (55, 110),
                            step=1, key="surface_scatter")

    row2_1, row2_2 = st.columns((2, 2))

    with row2_1:
        st.header("Map view")
        midpoint = (df2["lat"].mean(), df2["long"].mean())
        mapping_heatmap(df2, midpoint[0], midpoint[1], 12)
