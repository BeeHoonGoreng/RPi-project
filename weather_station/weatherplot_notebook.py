# %%
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import pandas as pd
import seaborn as sns

############################################################
# PLOTTING NOTEBOOK                                        #
############################################################
# This script is not meant to be run in command dialogue,
# but in your spyder IDE. Here are some examples of plots
# you can make.

####### Reading the data in ################################
# %%
df = pd.read_table("example.tsv",
                   sep = "\t",
                   header=None,
                   names=["Time","Hour","PM2.5","PM10","Temperature","Humidity"])

df["Time"] = pd.to_datetime(df["Time"])

############################################################
# PLOTTING WITH MATPLOTLIB                                 #
############################################################

# %%
# matplotlib code to generate simple plot that displays all variables
fig, axes = plt.subplots(4,1, figsize=(10,8), sharex = True)
variables = [
    ("PM2.5", "PM2.5 (µg/m³)", "green"),
    ("PM10", "PM10 (µg/m³)", "gold"),
    ("Temperature", "Temperature (°C)", "red"),
    ("Humidity", "Humidity (%)", "steelblue")
]

for ax, (col, ylab, colour) in zip(axes, variables):
    ax.plot(df["Time"], df[col], color = colour)
    ax.set_ylabel(ylab)
    ax.grid(True, alpha=0.4)

axes[-1].tick_params(axis="x", rotation=45)
fig.suptitle("PM2.5, PM10, Temperature and Humidity over time")

plt.tight_layout()
plt.show()

# %%
# matplotlib code to make 2 variables in the same plot, with the same axes
fig, ax = plt.subplots(figsize=(7,4))

ax.plot(df["Time"], df["Temperature"], color="red", label="Temperature (°C)")
ax.plot(df["Time"], df["Humidity"], color="steelblue", label="Humidity (%)")

ax.set_ylabel("Value")
ax.legend()
ax.tick_params(axis="x", rotation=45)
fig.suptitle("Temperature and Humidity overlaid")
plt.tight_layout()
plt.show()

############################################################
# PLOTTING WITH SEABORN                                    #
############################################################
# Seaborn is another package that handles plotting and data
# visualisation. It builds off of matplotlib, so the base
# functions are the same. It is far more high level making
# it simpler to use, with less levers to tune, which can be
# a downside if you want more tunability.
#
# With seaborn, you can plot multiple plots with a single
# function, instead of iterating over a loop like with 
# matplotlib.

# %%
# When plotting with seaborn, it is easier to handle in long format.
df_plot = df.melt(
    id_vars=["Time","Hour"],
    var_name="Variable",
    value_name="Value"
)
# Compare df.head() to see the difference
print(df.head())
print(df_plot.sort_values("Time").head())

# Also, it would be easier to rename the column headers to exactly
# what you want the titles to show in the plot.
title_map = {
    "PM2.5":        "PM2.5 (µg/m³)",
    "PM10":        "PM10 (µg/m³)",
    "Temperature": "Temperature (°C)",
    "Humidity":    "Humidity (%)",
}
df_plot1 = df_plot.copy()
df_plot1["Variable"] = df_plot["Variable"].map(title_map)

# %%
sns.set_theme(style="whitegrid")

g = sns.relplot(data=df_plot1,
            kind="line",
            x="Time",
            y="Value",
            col="Variable", # this arg is to separate graphs by the variable column
            hue="Variable", # this arg is to colour lines by the variable column
            col_wrap=2      # new row every col_wrap columns
)

g.set_titles("{col_name}")
g.fig.suptitle("PM2.5, PM10, Temperature and Humidity over time", y=1.05)

plt.show()

# %%
# If you want to combine two or more variables on the same axes
# Combining PM2.5 and PM10
df_plot2 = df_plot[df_plot["Variable"].isin(["PM2.5","PM10"])]

g = sns.relplot(data=df_plot2,
            kind="line",
            x="Time",
            y="Value",
            hue="Variable", # this arg is to colour lines by the variable column
            style="Variable"
)

plt.ylabel("µg/m³")
plt.xticks(rotation=45)
plt.title("PM2.5 and PM10 over time")
plt.show()