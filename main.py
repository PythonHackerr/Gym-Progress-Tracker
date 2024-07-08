import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from helpers import process_weight_sets_reps, generate_dates, moving_average
from settings import START_DATE, END_DATE, DATE_FORMAT, FILE_PATH, COLORS, INCLUDE_ALL, EXERCISES_TO_INCLUDE, MAIN_MARKERSIZE, MAIN_LINEWIDTH, MARKERSIZE, LINEWIDTH, SMOOTH_LINEWIDTH, CURRENT_PLOT_VARIANT, MAIN_ALPHA, SMOOTH_ALPHA, PLOT_VARIANT


def interpolate_data(dates, values, date_format):
    date_range = pd.date_range(start=pd.to_datetime(dates[0], format=date_format), end=pd.to_datetime(dates[-1], format=date_format))
    df = pd.DataFrame({'Date': pd.to_datetime(dates, format=date_format), 'Value': values})
    df = df.set_index('Date').reindex(date_range).interpolate(method='time').reset_index()
    df.columns = ['Date', 'Value']
    return df


def plot_data(dates):
    plt.ylim(100, 230)
    dates_freq = 10
    plt.xticks(ticks=range(0, len(dates), dates_freq), labels=dates[::dates_freq])
    plt.xticks(rotation=45, fontsize=9)
    plt.xlabel('Date', fontsize=16)
    plt.ylabel('Set average 1RM estimate [kg]', fontsize=16)
    plt.title('Set 1RM estimate progression [kg]')
    plt.legend(loc='upper left')
    plt.grid(True)
    ax = plt.gca()
    ax.xaxis.grid(True, linewidth=0.5)
    ax.yaxis.grid(True, linewidth=1)
    plt.show()


def main():
    plt.style.use('bmh')#classic | dark_background | seaborn-v0_8-dark
    plt.figure(figsize=(20, 8))


    workout_data = pd.read_csv(FILE_PATH)
    workout_data['1RM'] = workout_data['Weight_Sets_Reps'].apply(process_weight_sets_reps)
    workout_data = workout_data.dropna(subset=['1RM'])

    dates = generate_dates(START_DATE, END_DATE)

    for exercise in workout_data['Exercise'].unique() if INCLUDE_ALL else EXERCISES_TO_INCLUDE:
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

        plt.plot(dates, dummy, color=COLORS[exercise], label="DEADLIFT S" if exercise == "DEADLIFT" else exercise)

        valid_points = [(x, y) for x, y in zip(dates, rms) if y is not None]

        if (CURRENT_PLOT_VARIANT == PLOT_VARIANT.DATA_ONLY or CURRENT_PLOT_VARIANT == PLOT_VARIANT.ALL):

            for i in range(0, len(valid_points) - 1):
                x_values = [valid_points[i][0], valid_points[i+1][0]]
                y_values = [valid_points[i][1], valid_points[i+1][1]]

                date1 = datetime.datetime.strptime(valid_points[i+1][0], DATE_FORMAT)
                date2 = datetime.datetime.strptime(valid_points[i][0], DATE_FORMAT)

                if abs((date2 - date1).days) <= 30:
                    if exercise in ["DEADLIFT", "BENCH", "SQUAT"]:
                        plt.plot(x_values, y_values, linewidth=MAIN_LINEWIDTH, markersize=MAIN_MARKERSIZE, markeredgewidth=0, color=COLORS[exercise], label='_nolegend_', marker='o', alpha=MAIN_ALPHA)
                    else:
                        plt.plot(x_values, y_values, linewidth=LINEWIDTH, markersize=MARKERSIZE, color=COLORS[exercise], label='_nolegend_', marker='o', alpha=MAIN_ALPHA)
                else: # Plot single points if they are isolated
                    if exercise in ["DEADLIFT", "BENCH", "SQUAT"]:
                        plt.plot(x_values[0], y_values[0], linewidth=MAIN_LINEWIDTH, markersize=MAIN_MARKERSIZE, markeredgewidth=0, color=COLORS[exercise], label='_nolegend_', marker='o', alpha=MAIN_ALPHA)
                    else:
                        plt.plot(x_values[0], y_values[0], linewidth=LINEWIDTH, markersize=MARKERSIZE, color=COLORS[exercise], label='_nolegend_', marker='o', alpha=MAIN_ALPHA)

            date_last1, date_last2 = datetime.datetime.strptime(valid_points[::-1][0][0], DATE_FORMAT), datetime.datetime.strptime(valid_points[::-1][1][0], DATE_FORMAT)
            if abs((date_last2 - date_last1).days) > 30: # Plot last single point if isolated
                if exercise in ["DEADLIFT", "BENCH", "SQUAT"]:
                    plt.plot(x_values[::-1][0], y_values[::-1][0], linewidth=MAIN_LINEWIDTH, markersize=MAIN_MARKERSIZE, markeredgewidth=0, color=COLORS[exercise], label='_nolegend_', marker='o', alpha=MAIN_ALPHA)
                else:
                    plt.plot(x_values[::-1][0], y_values[::-1][0], linewidth=LINEWIDTH, markersize=MARKERSIZE, color=COLORS[exercise], label='_nolegend_', marker='o', alpha=MAIN_ALPHA)

        if len(valid_points) > 2 and (CURRENT_PLOT_VARIANT == PLOT_VARIANT.TREND_ONLY or CURRENT_PLOT_VARIANT == PLOT_VARIANT.ALL):
            interpolated_df = interpolate_data([x for x, _ in valid_points], [y for _, y in valid_points], DATE_FORMAT)
            smoothed_y_values = moving_average(interpolated_df['Value'], window_size=20).tolist()
            smoothed_points = [(interpolated_df['Date'][i].strftime(DATE_FORMAT), smoothed_y_values[i]) for i in range(len(smoothed_y_values))]
            for i in range(0, len(smoothed_points) - 1):
                x_values = [smoothed_points[i][0], smoothed_points[i+1][0]]
                y_values = [smoothed_points[i][1], smoothed_points[i+1][1]]
                plt.plot(x_values, y_values, color=COLORS[exercise], linewidth=SMOOTH_LINEWIDTH, alpha=SMOOTH_ALPHA)

    plot_data(dates)


if __name__ == '__main__':
    main()
