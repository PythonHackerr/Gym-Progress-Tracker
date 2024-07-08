import numpy as np
import pandas as pd
import re
import datetime
from scipy.interpolate import make_interp_spline  # For spline interpolation
from settings import DATE_FORMAT, CURRENT_FORMULA, Formula


def calculate_1rm(weight, reps, formula=CURRENT_FORMULA):
    if formula == Formula.BRZYCKI:
        if reps == 1:
            return weight
        return weight / (1.0278 - 0.0278 * reps)
    elif formula == Formula.LANDER:
        return (100 * weight) / (101.3 - 2.67123 * reps)
    elif formula == Formula.EPLEY:
        return weight * (1 + 0.0333*reps)
    else:
        raise ValueError("Unsupported formula. Please use Formula.BRZYCKI or Formula.LANDER")


def process_weight_sets_reps(weight_sets_reps_str):
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
            total_1rm += calculate_1rm(float(weight), int(reps), formula=CURRENT_FORMULA)
            count += 1
        elif 'x' in set_str:
            reps, sets = map(int, set_str.split(" ")[1].split('x'))
            weight = float(set_str.split(" ")[0])
            for _ in range(sets):
                total_1rm += calculate_1rm(weight, reps, formula=CURRENT_FORMULA)
                count += 1
        else:
            reps = 1
            weight = float(set_str)
            total_1rm += calculate_1rm(weight, reps, formula=CURRENT_FORMULA)
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


def generate_dates(start_date, end_date):
    start = datetime.datetime.strptime(start_date, DATE_FORMAT)
    end = datetime.datetime.strptime(end_date, DATE_FORMAT)
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days + 1)]
    return [date.strftime(DATE_FORMAT) for date in date_generated]


def moving_average(data, window_size):
    return data.rolling(window=window_size).mean()


# print(calculate_1rm(100, 18, formula=Formula.BRZYCKI))
# print(calculate_1rm(180, 5, formula=Formula.BRZYCKI))
# print(calculate_1rm(100, 18, formula=Formula.LANDER))
# print(calculate_1rm(180, 5, formula=Formula.LANDER))
# print(calculate_1rm(100, 18, formula=Formula.EPLEY))
# print(calculate_1rm(180, 5, formula=Formula.EPLEY))
