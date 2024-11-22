# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

from shiny import reactive, render
from shiny.express import ui, input
import random
from datetime import datetime
from faicons import icon_svg
import shinylive
import plotly.express as px
import pandas as pd
from collections import deque
import shinyswatch

# --------------------------------------------
# SET UP THE REACTIVE CONTENT
# --------------------------------------------

# --------------------------------------------
# PLANNING: We want to get a fake air quality reading and 
# Time stamp every N seconds.
# For now, we'll avoid storage and just 
# Try to get the fake live data working and sketch our app.
# ---------------------------------------------------------

# --------------------------------------------
# First, set a constant UPDATE INTERVAL for all live data
# Constants are usually defined in uppercase letters
# Use a type hint to make it clear that it's an integer (: int)
# --------------------------------------------
UPDATE_INTERVAL_SECS: int = 1
# --------------------------------------------

# Store the latest data up to the defined amount
DEQUE_SIZE: int = 25
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# Initialize a REACTIVE CALC that our display components can call
# to get the latest data and display it.
# The calculation is invalidated every UPDATE_INTERVAL_SECS
# to trigger updates.

# It returns everything needed to display the data.
# Very easy to expand or modify.
# --------------------------------------------
ui.page_opts(theme=shinyswatch.theme.darkly)

@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(input.update_interval())

    # Data generation logic. Get random air quality reading for PM2.5, rounded to 1 decimal place
    pm25 = round(random.uniform(0, 55), 1)  # Replace range with realistic PM2.5 values

    # Get a timestamp for "now" and use string format strftime() method to format it
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    latest_dictionary_entry = {"pm25": pm25, "timestamp": timestamp}

    reactive_value_wrapper.get().append(latest_dictionary_entry)    # Appends the latest dictionary entry to the deque
    deque_snapshot = reactive_value_wrapper.get()                   # Gets a snapshot of the deque
    df = pd.DataFrame(deque_snapshot)                               # Converts the deque to a pandas DataFrame
        
    return deque_snapshot, df, latest_dictionary_entry

    # Return everything we need
    return latest_dictionary_entry

# ------------------------------------------------
# Define the Shiny UI Page layout - Page Options
# ------------------------------------------------

ui.div(
    ui.h1("PyShiny Express: Live Air Quality Data", class_="title"), 
    style="display: flex; justify-content: space-between; align-items: center; width: 100%;"
),
ui.hr(),
# ------------------------------------------------
# Define the Shiny UI Page layout - Sidebar
# ------------------------------------------------

with ui.sidebar(open="open"):
    ui.h2("Air Quality Monitor", class_="text-center")
    ui.p(
        "A demonstration of real-time air quality readings.",
        class_="text-center",
    )
    ui.hr()   
    # Input for the update interval in seconds
    ui.input_slider("update_interval", "Select Data Update Interval (seconds):", min=1, max=30, value=3)
    ui.hr()
    ui.div(
        ui.div(
            icon_svg("cloud"), 
            style="font-size: 30px; color: #3498db;"  # Cloud icon styling
        ),
        ui.div(
            "Good Air Quality", 
            style="font-size: 20px; color: #3498db;"  # Text styling
        ),
        style="text-align: center; margin-top: 20px;"  # Center both elements vertically
    )

    ui.div(
        ui.div(
            icon_svg("cloud"), 
            style="font-size: 30px; color: #40916c;"  # Cloud icon styling
        ),
        ui.div(
            "Moderate Air Quality", 
            style="font-size: 20px; color: #40916c;"  # Text styling
        ),
        style="text-align: center; margin-top: 20px;"  # Center both elements vertically
    )

    ui.div(
        ui.div(
            icon_svg("cloud"), 
            style="font-size: 30px; color: #fb8500;"  # Cloud icon styling
        ),
        ui.div(
            "Unhealthy for Sensitive Groups", 
            style="font-size: 20px; color: #fb8500;"  # Text styling
        ),
        style="text-align: center; margin-top: 20px;"  # Center both elements vertically
    )
    ui.div(
        ui.div(
            icon_svg("cloud"), 
            style="font-size: 30px; color: #bf0603;"  # Cloud icon styling
        ),
        ui.div(
            "Dangerous Air Quality", 
            style="font-size: 20px; color: #bf0603;"  # Text styling
        ),
        style="text-align: center; margin-top: 20px;"  # Center both elements vertically
    )
#---------------------------------------------------------------------
# In Shiny Express, everything not in the sidebar is in the main panel
#---------------------------------------------------------------------

with ui.layout_columns():
    
    with ui.value_box(
        showcase=icon_svg("cloud"),
        style="background-color: #000000"
        ):
        ui.h2("Current PM2.5 Level")

        @render.ui
        def display_pm25_colored():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

            # Get the PM2.5 value from the latest entry
            pm25 = latest_dictionary_entry["pm25"]

            # Determine air quality category and color
            if pm25 <= 12.0:
                color = "#3498db"  # Good
            elif pm25 <= 35.4:
                color = "#40916c"  # Moderate
            elif pm25 <= 55.4:
                color = "#fb8500"  # Unhealthy for sensitive groups
            else:
                color = "#bf0603"  # Dangerous Air Quality

            # Return the formatted div with the color and PM2.5 value
            return ui.div(
                f"{pm25} µg/m³",
                style=f"font-size: 2rem; font-weight: bold; color: {color};",
            )

    with ui.value_box(
        showcase=icon_svg("clock"),
        style="background-color: #000000"
        ):
        ui.h2("Current Date and Time")
        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

ui.p("Note:  PM2.5 Values may vary based on conditions.")

ui.hr()


    

with ui.navset_card_tab(id="tab"):
    with ui.nav_panel("Live Air Quality Readings"):
    
        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            # Retrieve the DataFrame
            _, df, _ = reactive_calc_combined()
            
            # Rename columns for better readability
            df = df.rename(columns={"pm25": "PM2.5 Levels", "timestamp": "Timestamp"})
            
            # Adjust pandas display options for better formatting
            pd.set_option('display.width', None)  # Use maximum width

            # Render the data frame as a DataGrid component
            return render.DataGrid(df, width="50%")

    with ui.nav_panel("PM2.5 Scatter Plot"):
        @render.ui
        def plot():
            """Render scatter plot of the last 15 air quality readings."""
            # Retrieve the DataFrame and keep only the last 15 rows
            _, df, _ = reactive_calc_combined()
            df = df.tail(15)

            # Rename columns for readability in the plot
            df = df.rename(columns={"pm25": "PM2.5 Levels", "timestamp": "Timestamp"})

            # Determine air quality category and color for each reading
            def get_color(pm25):
                if pm25 <= 12.0:
                    return "#3498db"  # Good
                elif pm25 <= 35.4:
                    return "#40916c"  # Moderate
                elif pm25 <= 55.4:
                    return "#fb8500"  # Unhealthy for sensitive groups
                else:
                    return "#bf0603"  # Dangerous Air Quality

            # Apply the color function to the DataFrame
            df['Color'] = df['PM2.5 Levels'].apply(get_color)

            # Generate scatter plot using the 'Color' column for marker color
            fig = px.scatter(
                data_frame=df,
                x="PM2.5 Levels",
                y="Timestamp",
                title="Air Quality Levels",
                labels={"PM2.5 Levels": "PM2.5 Levels (µg/m³)", "Timestamp": "Date"},
                color='Color',  # Use the 'Color' column for point color
                color_discrete_map={
                    "#3498db": "#3498db",  # Good
                    "#40916c": "#40916c",  # Moderate
                    "#fb8500": "#fb8500",  # Unhealthy for sensitive groups
                    "#bf0603": "#bf0603"   # Dangerous Air Quality
                }
            ).update_layout(
                title={"text": "PM2.5 Readings over Time", "x": 0.5},
                yaxis_title="Timestamp",
                xaxis=dict(
                    title="PM2.5 Level (µg/m³)",  # Combine xaxis_title here
                    range=[0, 55],  # Set the x-axis range from 0 to 55 µg/m³
                    gridcolor='grey',  # Set x-axis grid lines to grey
                    zerolinecolor='grey'  # Set x-axis zero line to grey
                ),
                height=500,  # Set a fixed height for the graph
                plot_bgcolor="rgba(0, 0, 0, 0)",  # Make the plot background transparent
                paper_bgcolor="rgba(0, 0, 0, 0)",  # Make the paper (outside the plot) background transparent
                font=dict(color="white"),  # Set all text color to white
                yaxis=dict(
                    gridcolor='grey',  # Set y-axis grid lines to grey
                    zerolinecolor='grey',  # Set y-axis zero line to grey
                ),
                showlegend=False  # Disable the legend
            ).update_traces(marker=dict(size=9))
            

            return fig