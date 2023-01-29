import os
import pyNetLogo
import pandas as pd

os.environ["JAVA_HOME"] = 'C:/Program Files/NetLogo 6.3.0/runtime/bin/server/'

default_values = {
    "call-limit?": True,
    "earthquake-magnitude": 0.4,
    "amount-ambulances": 40,
    "amount-drones": 10,
    "probability-call-112": 1,
    "amount-hospitals": 10,
    "hospital-capacity": 100,
    "hospital-filling-percentage-t0": 60,
    "initial-ambulance-search-radius": 5,
    "percentage-concrete-buildings": 70,
    "high-damage-road-blocked-chance": 10,
    "collapsed-road-blocked-chance": 25,
    "max-concurrent-calls": 50,
    "average-call-time": 2.5,
    "amount-drones": 10,
    "drone-speed": 0.5,  # This is multiplied by 10, so 0.5 is 5 m/s
    "drone-range": 45,
    "ambulance-reroute-frequency": 5,
    "drone-view-radius": 25,  # This is multiplied by 10, so 25 is 250 meter
}

replications = 25
ticks = 720
gui = False

exp_nr = 0
exp_names = ["no-drones", "short-range", "slow-reroute", "more-drones", "large-view", "fast-reroute", "many-long-range"]
exp_name = f"{exp_nr}_{exp_names[exp_nr]}"
exp = {
    "amount-drones": [0, 10, 10, 20, 20, 20, 40],
    "drone-view-radius": [25, 25, 25, 25, 50, 50, 50],
    "drone-range": [30, 30, 45, 45, 45, 45, 60],
    "ambulance-reroute-frequency": [10, 10, 10, 10, 10, 5, 5],
}

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

print(f"Starting experiment {exp_name} with {replications} runs.")
for var, val in exp.items():
    print(f"Using {var} = {val[exp_nr]}")
print("")

for i in range(replications):
    # Change sliders (global variables)
    for var, val in exp.items():
        netlogo.command(f"set {var} {val[exp_nr]}")

    # Setup model
    netlogo.command("setup")

    # Record initial data and run
    single_data[i] = netlogo.report(single_reporters)
    series_data[i] = netlogo.repeat_report(series_reporters, ticks)

    print(f"Finished run {i+1} of {replications}.")

netlogo.kill_workspace()

# Combine the series_data to a dataframe and save it
# Create a list of tuples with the key and dataframe
dfs = [(k, df) for k, df in series_data.items()]

# Concatenate the DataFrames in the dictionary along axis=1
result = pd.concat([df for key, df in dfs], keys=[key for key, df in dfs], axis=1)

# Reorder the levels and sort
result.columns = result.columns.reorder_levels([1, 0])

# Save df as pickle
result.to_pickle(f"../results/experiments/exp_series_{exp_name}_{replications}r_df.pickle")


# Combine single_data to a DataFrame
sdf = pd.DataFrame(single_data)
sdf = sdf.T
sdf.columns = single_reporters
sdf.to_pickle(f"../results/experiments/exp_single_{exp_name}_{replications}r_df.pickle")

print("Done. Results are saved in results/experiments.")
