from enum import Enum

class Formula(Enum):
    BRZYCKI = 1
    LANDER = 2
    EPLEY = 3

class PLOT_VARIANT(Enum):
    ALL = 1
    DATA_ONLY = 2
    TREND_ONLY = 3

# general settings
FILE_PATH = 'records.csv'
START_DATE, END_DATE = "20.12.22", "15.08.24"
DATE_FORMAT = "%d.%m.%y"
CURRENT_FORMULA = Formula.EPLEY
CURRENT_PLOT_VARIANT = PLOT_VARIANT.ALL

# plot settings
INCLUDE_ALL = True
EXERCISES_TO_INCLUDE = ["DEADLIFT", "BENCH", "SQUAT"]

# visuals settings
COLORS = {
    "BENCH": "blue",
    "BENCH Paused": "#00CED1",
    "DEADLIFT": "red",
    "DEADLIFT Paused": "orange",
    "DEADLIFT C": "black",
    "SQUAT": "green",
    "SQUAT Paused": "#32CD32",
}
SMOOTH_LINEWIDTH = 5
MAIN_MARKERSIZE = 6
MAIN_LINEWIDTH = 2.5
MARKERSIZE = 4
LINEWIDTH = 1.75
MAIN_ALPHA = 1
SMOOTH_ALPHA = 0.05