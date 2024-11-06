import numpy as np
from func import gaussian_membership_function


def d_rule(selected_func, num_intervals, data_from_csv, intervals_data):
    intervals = {}

    for var, terms in intervals_data.items():
        intervals[var] = np.linspace(min(data_from_csv[var]), max(data_from_csv[var]), num_intervals)

    rules = []

    for i in range(len(data_from_csv)):
        rule = []

        for var in data_from_csv.columns[:-1]:
            value = data_from_csv.iloc[i][var]
            membership_values = [
                gaussian_membership_function(value, mean, (intervals[var][1] - intervals[var][0]) / 2)
                for mean in intervals[var]
            ]

            max_membership_index = np.argmax(membership_values)
            rule.append((var, f'{var}_term{max_membership_index + 1}'))

        result_value = data_from_csv.iloc[i]["price_range"]
        rules.append((rule, f'price_range_term{result_value + 1}'))

    print(rules)





