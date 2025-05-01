import pandas as pd
import json
import os

# List all CSV files in the current directory
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
print("Available CSV files:")
for i, file in enumerate(csv_files, start=1):
    print(f"{i}. {file}")

# Ask the user to select a file
file_index = int(input("Enter the number of the file you want to open: ").strip()) - 1
if 0 <= file_index < len(csv_files):
    file_name = csv_files[file_index]
    print(f"You selected: {file_name}")
else:
    print("Invalid selection. Exiting.")
    exit()

FILE_NAME = file_name
# Load the data from the CSV file
csv_file_path = FILE_NAME
df = pd.read_csv(csv_file_path, parse_dates=["time"])

# Sort by time
df = df.sort_values("time").reset_index(drop=True)

# Ask the user if they want to apply preset rules from the JSON file
apply_preset_rules = input("Do you want to apply preset rules from 'rules.json'? (yes/no): ").strip().lower()
if apply_preset_rules == "yes":
    apply_rules(df)

# Step-by-step user interaction
# Ask the user if they want to add Time-based Features
add_time_features = input("Do you want to add Time-based Features? (yes/no): ").strip().lower()
if add_time_features == "yes":
    # Add Time-based Features
    df["hour"] = df["time"].dt.hour
    df["day_of_week"] = df["time"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["part_of_day"] = pd.cut(df["hour"],
                               bins=[0, 6, 12, 18, 24],
                               labels=["night", "morning", "afternoon", "evening"],
                               right=False)
    df["time_since_last_event"] = df["time"].diff().fillna(pd.Timedelta(seconds=0)).dt.total_seconds()
    print("Time-based Features added.")
    print(df.head(10))

# Ask the user if they want to add a time threshold for grouping events into sessions
add_session_grouping = input("Do you want to add a time threshold for grouping events into sessions? (yes/no): ").strip().lower()
if add_session_grouping == "yes":
    # Ask the user to specify the session threshold in minutes
    session_threshold_minutes = int(input("Enter the session threshold in minutes: ").strip())
    SESSION_THRESHOLD = session_threshold_minutes * 60  # Convert minutes to seconds

    # Group events into sessions
    df["session_id"] = (df["time_since_last_event"] > SESSION_THRESHOLD).cumsum()

    # Calculate session-level statistics
    session_stats = df.groupby("session_id").agg(
        session_start=("time", "min"),
        session_end=("time", "max"),
        total_volume=("eventVolume", "sum"),
        total_duration=("eventLength", "sum"),
        event_count=("time", "count")
    ).reset_index()

    # Merge session stats back into the original dataframe
    df = df.merge(session_stats, on="session_id", how="left")
    print("Session grouping added with a threshold of", session_threshold_minutes, "minutes.")
    print(df.head(10))

# Add a Burst Indicator with user-defined categories and Average Flow Rate
add_burst_indicator = input("Do you want to add a Burst Indicator? (yes/no): ").strip().lower()
if add_burst_indicator == "yes":
    while True:
        # Ask the user to define the conditions for a short burst
        burst_name = input("Enter the name for this short burst category: ").strip()
        max_length = input(f"Enter the maximum event length (in seconds) for {burst_name} (or 'none' to skip): ").strip()
        max_volume = input(f"Enter the maximum event volume (in gallons) for {burst_name} (or 'none' to skip): ").strip()
        max_flow_rate = input(f"Enter the maximum average flow rate (or 'none' to skip): ").strip()

        # Build the condition dynamically
        conditions = []
        if max_length != "none":
            conditions.append(f"eventLength < {max_length}")
        if max_volume != "none":
            conditions.append(f"eventVolume < {max_volume}")
        if max_flow_rate != "none":
            conditions.append(f"avgFlowRate < {max_flow_rate}")

        condition = " and ".join(conditions)

        # Apply the condition and label
        if condition:
            df.loc[df.eval(condition), "burst_indicator"] = burst_name
            print(f"Short burst category '{burst_name}' added based on condition: {condition}.")
        else:
            print("No valid condition provided. Skipping this burst category.")

        print(df[["time", "eventLength", "eventVolume", "avgFlowRate", "burst_indicator"]].head(10))

        # Ask if the user wants to add another category
        add_another = input("Do you want to add another short burst category? (yes/no): ").strip().lower()
        if add_another != "yes":
            break

# Interactive Dataset Labeling with Guided Input and Average Flow Rate
add_labels = input("Do you want to label the dataset? (yes/no): ").strip().lower()
if add_labels == "yes":
    while True:
        # Ask the user to define a label
        label_name = input("Enter the name for this label: ").strip()

        # Guide the user to define conditions step-by-step
        print("Define the conditions for this label step-by-step. Use 'none' to skip any value.")
        min_length = input("Enter the minimum event length (or 'none' to skip): ").strip()
        max_length = input("Enter the maximum event length (or 'none' to skip): ").strip()
        min_volume = input("Enter the minimum event volume (or 'none' to skip): ").strip()
        max_volume = input("Enter the maximum event volume (or 'none' to skip): ").strip()
        min_flow_rate = input("Enter the minimum average flow rate (or 'none' to skip): ").strip()
        max_flow_rate = input("Enter the maximum average flow rate (or 'none' to skip): ").strip()

        # Build the condition string dynamically
        conditions = []
        if min_length != "none":
            conditions.append(f"eventLength >= {min_length}")
        if max_length != "none":
            conditions.append(f"eventLength <= {max_length}")
        if min_volume != "none":
            conditions.append(f"eventVolume >= {min_volume}")
        if max_volume != "none":
            conditions.append(f"eventVolume <= {max_volume}")
        if min_flow_rate != "none":
            conditions.append(f"avgFlowRate >= {min_flow_rate}")
        if max_flow_rate != "none":
            conditions.append(f"avgFlowRate <= {max_flow_rate}")

        condition = " and ".join(conditions)

        # Apply the condition and label
        if condition:
            df.loc[df.eval(condition), "label"] = label_name
            print(f"Label '{label_name}' added based on condition: {condition}.")
        else:
            print("No valid condition provided. Skipping this label.")

        print(df[["time", "eventLength", "eventVolume", "avgFlowRate", "label"]].head(10))

        # Ask if the user wants to add another label
        add_another_label = input("Do you want to add another label? (yes/no): ").strip().lower()
        if add_another_label != "yes":
            break

# Function to save rules to a file
def save_rules(rules, file_name="rules.json"):
    with open(file_name, "w") as f:
        json.dump(rules, f, indent=4)
    print(f"Rules saved to {file_name}")

# Function to load and apply rules
def apply_rules(df, file_name="rules.json"):
    try:
        with open(file_name, "r") as f:
            rules = json.load(f)
        for rule in rules:
            condition = rule["condition"]
            column = rule["column"]
            value = rule["value"]
            df.loc[df.eval(condition), column] = value
        print(f"Rules from {file_name} applied successfully.")
    except FileNotFoundError:
        print(f"No rules file found at {file_name}. Skipping rule application.")

# Collect rules interactively
rules = []
add_rules = input("Do you want to define rules interactively? (yes/no): ").strip().lower()
if add_rules == "yes":
    while True:
        column = input("Enter the column to modify (e.g., 'label' or 'burst_indicator'): ").strip()
        value = input(f"Enter the value to assign to {column}: ").strip()
        print("Define the condition for this rule step-by-step. Use 'none' to skip any value.")
        min_length = input("Enter the minimum event length (or 'none' to skip): ").strip()
        max_length = input("Enter the maximum event length (or 'none' to skip): ").strip()
        min_volume = input("Enter the minimum event volume (or 'none' to skip): ").strip()
        max_volume = input("Enter the maximum event volume (or 'none' to skip): ").strip()
        min_flow_rate = input("Enter the minimum average flow rate (or 'none' to skip): ").strip()
        max_flow_rate = input("Enter the maximum average flow rate (or 'none' to skip): ").strip()

        # Build the condition string dynamically
        conditions = []
        if min_length != "none":
            conditions.append(f"eventLength >= {min_length}")
        if max_length != "none":
            conditions.append(f"eventLength <= {max_length}")
        if min_volume != "none":
            conditions.append(f"eventVolume >= {min_volume}")
        if max_volume != "none":
            conditions.append(f"eventVolume <= {max_volume}")
        if min_flow_rate != "none":
            conditions.append(f"avgFlowRate >= {min_flow_rate}")
        if max_flow_rate != "none":
            conditions.append(f"avgFlowRate <= {max_flow_rate}")

        condition = " and ".join(conditions)

        if condition:
            rules.append({"column": column, "value": value, "condition": condition})
            print(f"Rule added: If {condition}, set {column} to {value}.")
        else:
            print("No valid condition provided. Skipping this rule.")

        add_another_rule = input("Do you want to add another rule? (yes/no): ").strip().lower()
        if add_another_rule != "yes":
            break

    save_rules(rules)

# Apply rules automatically
apply_rules(df)

# Ask the user whether to overwrite the file or save with a new name
# The user is prompted to either overwrite the existing file or provide a new file name.
# If no input is provided, the default file '85day_labeled.csv' is overwritten.
output_file = input("Enter the output file name (or press Enter to overwrite '85day_labeled.csv'): ")
if not output_file:
    output_file = FILE_NAME

# Save the updated dataset to the specified file
df.to_csv(output_file, index=False)
print(f"Features saved to {output_file}")