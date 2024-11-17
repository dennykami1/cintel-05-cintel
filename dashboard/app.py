# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from faicons import icon_svg

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
UPDATE_INTERVAL_SECS: int = 1.5
# --------------------------------------------

# Initialize a REACTIVE CALC that our display components can call
# to get the latest data and display it.
# The calculation is invalidated every UPDATE_INTERVAL_SECS
# to trigger updates.

# It returns everything needed to display the data.
# Very easy to expand or modify.
# --------------------------------------------

@reactive.calc()
def reactive_calc_combined():

    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic. Get random air quality reading for PM2.5, rounded to 1 decimal place
    pm25 = round(random.uniform(0, 50), 1)  # Replace range with realistic PM2.5 values

    # Get a timestamp for "now" and use string format strftime() method to format it
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    latest_dictionary_entry = {"pm25": pm25, "timestamp": timestamp}

    # Return everything we need
    return latest_dictionary_entry

# ------------------------------------------------
# Define the Shiny UI Page layout - Page Options
# ------------------------------------------------
 
ui.div(
    ui.h2("PyShiny Express: Live Air Quality Data", class_="title"),
    ui.input_dark_mode(), 
    style="display: flex; justify-content: space-between; align-items: center; width: 100%;"
)

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

ui.h2("Current PM2.5 Level")

@render.ui
def display_pm25_colored():
    latest_dictionary_entry = reactive_calc_combined()
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

    return ui.div(
        f"{pm25} µg/m³",
        style=f"font-size: 2rem; font-weight: bold; color: {color};",
    )

ui.p("Note:  Values may vary based on conditions.")

ui.hr()

ui.h2("Current Date and Time")

@render.text
def display_time():
    """Get the latest reading and return a timestamp string"""
    latest_dictionary_entry = reactive_calc_combined()
    return f"{latest_dictionary_entry['timestamp']}"