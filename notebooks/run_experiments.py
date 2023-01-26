import os
import pyNetLogo
import pandas as pd

os.environ["JAVA_HOME"] = 'C:/Program Files/NetLogo 6.3.0/runtime/bin/server/'

default_values = {
    # variable-name: (number, rounded to int or not)
    "call-limit?": (True, False),
    "earthquake-magnitude": (0.4, False),
    "amount-ambulances": (40, True),
    "amount-drones": (10, True),
    "probability-call-112": (1, False),
    "amount-hospitals": (10, True),
    "hospital-capacity": (100, True),
    "hospital-filling-percentage-t0": (60, False),
    "initial-ambulance-search-radius": (5, True),
    "percentage-concrete-buildings": (70, False),
    "high-damage-road-blocked-chance": (10, False),
    "collapsed-road-blocked-chance": (25, False),
    "max-concurrent-calls": (50, True),
    "average-call-time": (2.5, False),
    "drone-speed": (0.5, False),
    "drone-range": (45, False),
    "ambulance-reroute-frequency": (5, True),
}

replications = 25
ticks = 720
value_to_vary = list(default_values.keys())[14]  # Change this one from 1 to 17 to quickly alter the value varried
amount_to_vary = [0.8, 1.25]

factor = True      # Set false if you want to do custom values, and for the call-limit (True / False)
fixed_values = []  # Put custom values here
gui = False

value_to_vary_name = value_to_vary.replace("?", "")  # File names can't contain question marks

series_reporters = [
    "recovered-hospital",
    "recovered-with-help",
    "recovered-unchecked",
    "fraction-called-in",
    "deaths",
    "number-destroyed-streets-spotted",
    "fraction-destroyed-streets-spotted",
]

single_reporters = [
    'count crossings with [building-status = "collapsed"]',
    'count crossings with [building-status = "high-damage"]',
    "number-destroyed-streets",
]

netlogo = pyNetLogo.NetLogoLink(gui=gui)
netlogo.load_model("C:/Users/Ewout/Documents/GitHub/SEN1211-earthquake-project/models_netlogo/earthquake_model.nlogo")

single_data = {}
series_data = {}

if factor:
    values = [round(default_values[value_to_vary][0] * v, 5) for v in amount_to_vary]
else:
    values = fixed_values

if default_values[value_to_vary][1]:
    print(f"Rounding values to integers: {values}")
    values = [int(v) for v in values]
    print(f"Now rounded: {values}\n")

runs = len(values) * replications
print(f"Starting {len(values)} * {replications} = {runs} runs.")

for v in values:
    print(f"Start with {replications} replications with {value_to_vary} = {v}.")
    single_data[v] = {}
    series_data[v] = {}

    for i in range(replications):
        # Setup model
        netlogo.command("setup")
        netlogo.command(f"set {value_to_vary} {v}")

        # Record initial data and run
        single_data[v][i] = netlogo.report(single_reporters)
        series_data[v][i] = netlogo.repeat_report(series_reporters, ticks)

        print(f"Finished run {i+1} of {replications}.")

    # Combine the series_data to a dataframe and save it
    # Create a list of tuples with the key and dataframe
    dfs = [(k, df) for k, df in series_data[v].items()]

    # Concatenate the DataFrames in the dictionary along axis=1
    result = pd.concat([df for key, df in dfs], keys=[key for key, df in dfs], axis=1)

    # Reorder the levels and sort
    result.columns = result.columns.reorder_levels([1, 0])

    # Save df as pickle
    result.to_pickle(f"../results/sensitivity/sens_series_{value_to_vary_name}_{v}_{replications}r_df.pickle")

netlogo.kill_workspace()

# Combine single_data to a DataFrame
sdf = pd.DataFrame(single_data)
sdf_dict = {}

for column in sdf.columns:
    sdf_dict[column] = pd.DataFrame(sdf[column].to_list(), columns=single_reporters)
sdf2 = pd.concat(sdf_dict.values(), axis=1, keys=sdf_dict.keys())

sdf2.to_pickle(f"../results/sensitivity/sens_single_{value_to_vary_name}_{replications}r_df.pickle")

print("Done. Results are saved in results/sensitivity.")
