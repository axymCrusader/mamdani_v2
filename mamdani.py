import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def mamnadi_start(selected_func, num_intervals, data_from_csv, intervals_data):
    #пока работает с только этими полями
    array_battery_power = data_from_csv["battery_power"].to_numpy()
    array_ram = data_from_csv["ram"].to_numpy()
    array_px = data_from_csv["px"].to_numpy()
    array_price_range = data_from_csv["price_range"].to_numpy()


    battery_power = ctrl.Antecedent(np.linspace(array_battery_power.min(), array_battery_power.max(), 100),
                                    'battery_power')
    ram = ctrl.Antecedent(np.linspace(array_ram.min(), array_ram.max(), 100), 'ram')
    px = ctrl.Antecedent(np.linspace(array_px.min(), array_px.max(), 100), 'px')
    price_range = ctrl.Consequent(np.linspace(array_price_range.min(), array_price_range.max(), 100), 'price_range')

    variables = [battery_power, ram, px, price_range]

    for var, (var_name, terms) in zip(variables, intervals_data.items()):
        intervals = np.linspace(var.universe.min(), var.universe.max(), num_intervals + 1)

        for term, (start, end) in zip(terms, zip(intervals, intervals[1:])):
            if selected_func == 'trimf':
                var[term] = fuzz.trimf(var.universe, [start, (start + end) / 2, end])
            elif selected_func == 'trapmf':
                var[term] = fuzz.trapmf(var.universe, [start, start + (end - start) / 4, end - (end - start) / 4, end])
            elif selected_func == 'gaussmf':
                var[term] = fuzz.gaussmf(var.universe, (start + end) / 2, (end - start) / 4)

    rules = []
    for bp_term in intervals_data['battery_power']:
        for ram_term in intervals_data['ram']:
            for px_term in intervals_data['px']:
                for pr_term in intervals_data['price_range']:
                    if bp_term in battery_power and ram_term in ram and px_term in px and pr_term in price_range:
                        rule = ctrl.Rule(
                            battery_power[bp_term] & ram[ram_term] & px[px_term],
                            price_range[pr_term]
                        )
                        rules.append(rule)

    price_control_system = ctrl.ControlSystem(rules)

    price_control_simulation = ctrl.ControlSystemSimulation(price_control_system)


    price_control_simulation.input['battery_power'] = data_from_csv["battery_power"].iloc[0]
    price_control_simulation.input['ram'] = data_from_csv["ram"].iloc[0]
    price_control_simulation.input['px'] = data_from_csv["px"].iloc[0]

    price_control_simulation.compute()

    result = price_control_simulation.output['price_range']
    print(result)

