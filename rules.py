import numpy as np
import pandas as pd


def d_rule(selected_func, num_intervals, data_from_csv, intervals_data):
    intervals = {}
    for var, bounds in intervals_data.items():
        bounds = list(map(int, bounds))
        intervals[var] = np.linspace(min(data_from_csv[var]), max(data_from_csv[var]), num_intervals)

    rules = []
    for i in range(len(data_from_csv)):
        rule = []
        for var in data_from_csv.columns[:-1]:
            value = data_from_csv.iloc[i][var]
            membership_values = [selected_func(value, mean, (intervals[var][1] - intervals[var][0]) / 2) 
                                 for mean in intervals[var]]
            max_membership_index = np.argmax(membership_values)
            rule.append((var, f'{var}_{max_membership_index + 1}'))
        rules.append((rule, f'price_range_{data_from_csv.iloc[i]["price_range"] + 1}'))

    return rules




