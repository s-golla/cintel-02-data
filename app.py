import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny.express import ui, input, render
import plotly.express as px
from shiny import render
from shiny.render import plot as render_plot
from shinywidgets import render_plotly

# --- 1. Data Loading ---
penguins = load_penguins()

# --- 2. User Interface (UI) Definition ---
ui.page_opts(title="Interactive Data Visualizations", fillable=True)

with ui.sidebar(open="open"):
    ui.h2("Sidebar")
    ui.input_selectize(
        "selected_attribute",
        "Select Attribute",
        choices=["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
    )
    ui.input_numeric("plotly_bin_count", "Plotly Histogram Bins", 20)
    ui.input_slider("seaborn_bin_count", "Seaborn Histogram Bins", 0, 100, 20)
    ui.input_checkbox_group(
        "selected_species_list",
        "Filter Species",
        choices=["Adelie", "Gentoo", "Chinstrap"],
        selected=["Adelie", "Gentoo", "Chinstrap"],
        inline=True,
    )
    ui.hr()
    ui.a("GitHub", href="https://github.com/s-golla/cintel-02-data", target="_blank")

    # These two inputs were part of the original code, make sure they are still desired
    ui.input_slider("selected_number_of_bins", "Number of Bins", 0, 100, 20)
    ui.hr()
    ui.h6("Penguin Plot Filters")
    all_species = ["All"] + sorted(penguins["species"].dropna().unique().tolist())
    ui.input_select("selected_species", "Select Species", choices=all_species, selected="All")


# --- 3. Server Logic and Output Definitions ---

# This still uses matplotlib, so @render.plot is correct
@render_plot(alt="Histogram using the selected number of bins for random data")
def plot_histogram():
    data = np.random.randn(800)
    plt.hist(data, bins=input.selected_number_of_bins(), density=True, color="darkorange", edgecolor="black")

    plt.title("Frequency Distribution of Randomly Generated Data")
    plt.xlabel("Value")
    plt.ylabel("Density")

# This still uses seaborn (which is built on matplotlib), so @render.plot is correct
@render_plot(alt="Scatterplot of Penguin Flipper Length vs Body Mass")
def penguin_scatter():
    selected_species = input.selected_species()

    if selected_species == "All":
        filtered_penguins = penguins
    else:
        filtered_penguins = penguins[penguins["species"] == selected_species]

    sns.scatterplot(
        data=filtered_penguins,
        x="flipper_length_mm",
        y="body_mass_g",
        hue="species",
        style="sex",
        palette={"Adelie": "red", "Chinstrap": "blue", "Gentoo": "green"}
    )

    plt.title(f"Penguin Flipper Length vs Body Mass by Species and Sex ({selected_species})")
    plt.xlabel("Flipper Length (mm)")
    plt.ylabel("Body Mass (g)")


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Penguin Data Table")

        @render.data_frame
        def penguin_data_table():
            return render.DataTable(penguins)

    with ui.card(full_screen=True):
        ui.card_header("Penguin Data Grid")

        @render.data_frame
        def penguin_data_grid():
            return render.DataGrid(penguins)

with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Plotly Histogram: All Species")

        # CHANGED: Use @render_plotly for Plotly figures
        @render_plotly
        def plotly_histogram():
            selected_attribute = input.selected_attribute()
            return px.histogram(
                penguins,
                x=selected_attribute,
                nbins=input.plotly_bin_count(),
                title=f"Distribution of {selected_attribute}",
            )

    with ui.card(full_screen=True):
        ui.card_header("Seaborn Histogram: All Species")

        # This still uses seaborn (matplotlib), so @render_plot is correct
        @render_plot
        def seaborn_histogram():
            selected_attribute = input.selected_attribute()
            sns.histplot(
                data=penguins,
                x=selected_attribute,
                bins=input.seaborn_bin_count(),
                kde=True,
            )
            plt.title(f"Distribution of {selected_attribute}")
            plt.xlabel(selected_attribute)
            plt.ylabel("Count")

    with ui.card(full_screen=True):
        ui.card_header("Plotly Scatterplot: Species")

        # CHANGED: Use @render_plotly for Plotly figures
        @render_plotly
        def plotly_scatterplot():
            # Filter data based on selected species
            filtered_penguins = penguins[penguins["species"].isin(input.selected_species_list())]

            return px.scatter(
                filtered_penguins,
                x="flipper_length_mm",
                y="body_mass_g",
                color="species",
                symbol="sex",
                title="Penguin Flipper Length vs Body Mass by Species and Sex",
                labels={
                    "flipper_length_mm": "Flipper Length (mm)",
                    "body_mass_g": "Body Mass (g)",
                },
                hover_data=["island", "bill_length_mm", "bill_depth_mm"],
            )
