import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import re
from itertools import islice
import datetime

# Load the workout log file
file_path = 'records_optimized_deadlift.csv'
workout_data = pd.read_csv(file_path)
workout_data.head()

plt.style.use('classic')

START_DATE, END_DATE = "20.12.22", "31.03.24"

colors = {
    "BENCH" : "blue",
    "BENCH Paused" : "#89CFF0",
    "DEADLIFT" : "red",
    "DEADLIFT Paused" : "#FF7F7F",
    "DEADLIFT CONV" : "black",
    "SQUAT" : "green",
    "SQUAT Paused" : "#90EE90",
}

def calculate_1rm(weight, reps):
    if (reps == 1):
        return weight
    return weight / (1.0278 - 0.0278 * reps)


def process_weight_sets_reps(weight_sets_reps_str):
    print(split_complex_string(str(weight_sets_reps_str)))
    weight_sets_reps_str = merge_elements_with_x(split_complex_string(str(weight_sets_reps_str)))
    sets = weight_sets_reps_str
    new_sets = []
    for set_str in sets:
        new_str = set_str
        if '(' in set_str:
            new_str = convert_string(set_str).split(" ")
            new_sets += new_str
        else:
            new_sets.append(new_str)
    sets = new_sets

    total_1rm = 0
    count = 0

    for set_str in sets:
        if '*' in set_str:
            weight, reps = set_str.split('*')
            total_1rm += calculate_1rm(float(weight), int(reps))
            count += 1
        elif 'x' in set_str:
            reps, sets = map(int, set_str.split(" ")[1].split('x'))
            weight = float(set_str.split(" ")[0])
            for _ in range(sets):
                total_1rm += calculate_1rm(weight, reps)
                count += 1
        else:
            reps = 1
            weight = float(set_str)
            total_1rm += calculate_1rm(weight, reps)
            count += 1

    return total_1rm / count if count > 0 else np.nan



def convert_string(input_str):
    base, numbers = input_str.split('(')
    numbers = numbers.strip(')').split()
    result = [f"{base}*{num}" for num in numbers]
    return ' '.join(result)

def split_complex_string(s):
    pattern = r'\d+\.\d+\*\d+|\d+\(\d+(?: \d+)*\)|\d+[x*]\d+|\d+'
    return re.findall(pattern, s)

def merge_elements_with_x(input_list):
    merged_list = []
    for i in range(len(input_list)):
        if 'x' in input_list[i]:
            if merged_list:
                merged_list[-1] += " " + input_list[i]
        else:
            merged_list.append(input_list[i])
    return merged_list



workout_data['1RM'] = workout_data['Weight_Sets_Reps'].apply(process_weight_sets_reps)
workout_data = workout_data.dropna(subset=['1RM'])
plt.figure(figsize=(20, 8))


def generate_dates(start_date, end_date):
    start = datetime.datetime.strptime(start_date, "%d.%m.%y")
    end = datetime.datetime.strptime(end_date, "%d.%m.%y")
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days + 1)]

    return [date.strftime("%d.%m.%y") for date in date_generated]

dates = generate_dates(START_DATE, END_DATE)
for exercise in workout_data['Exercise'].unique():
    # if (not(exercise == "BENCH" or exercise == "DEADLIFT" or exercise == "SQUAT")):
    #     continue
    rms = []
    dummy = []
    for date in dates:
        dummy.append(0)
        filtered_data = workout_data[(workout_data['Date'] == date) & (workout_data['Exercise'] == exercise)]
        if not filtered_data.empty:
            rm = filtered_data.iloc[0]['1RM']
            rms.append(rm)
        else:
            rms.append(None)

    last_date = dates[0]
    last_rm = -1

    plt.plot(dates, dummy, color='black', label='_nolegend_', marker='')

    valid_points = [(x, y) for x, y in zip(dates, rms) if y is not None]

    x_values = [valid_points[0][0], valid_points[1][0]]
    y_values = [valid_points[0][1], valid_points[1][1]]
    plt.plot(x_values, y_values, color=colors[exercise], label=exercise, marker='o')
    for i in range(0, len(valid_points) - 1):
        x_values = [valid_points[i][0], valid_points[i+1][0]]
        y_values = [valid_points[i][1], valid_points[i+1][1]]
        if (exercise == "DEADLIFT" or exercise == "BENCH" or exercise == "SQUAT"):
            plt.plot(x_values, y_values, linewidth=4, markersize=8, markeredgewidth=0, color=colors[exercise], label='_nolegend_', marker='o')
        else:
            plt.plot(x_values, y_values, linewidth=2, markersize=5, color=colors[exercise], label='_nolegend_', marker='o')


plt.xlabel('Date')
plt.ylim(100, 230)
dates_freq = 10
new_dates = dates[::dates_freq]
plt.xticks(ticks=range(0, len(dates), dates_freq), labels=new_dates)
plt.xticks(rotation=45, fontsize=9)
plt.ylabel('Average 1RM (kg) Estimate')
plt.title('1RM Year Progression')
plt.legend(loc='upper left')
plt.grid(True)
ax = plt.gca()
ax.xaxis.grid(True, linewidth=0.5)
ax.yaxis.grid(True, linewidth=1)
plt.show()