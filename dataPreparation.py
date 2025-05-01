# Importing the utility functions from the module
from feature_engineering_utils import (
    apply_rules,
    save_rules,
    add_time_features,
    group_sessions,
    add_burst_indicator,
    label_dataset,
    remove_rows_by_value,
    remove_unlabeled_rows,
    save_dataframe
)

import pandas as pd
import os

# Ask the user to select a file or specify a path
file_path = input("Enter the full path of the file you want to open (or press Enter to select from the current directory): ").strip()
if not file_path:
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
        file_path = file_name
    else:
        print("Invalid selection. Exiting.")
        exit()
else:
    if not os.path.isfile(file_path):
        print("The specified file does not exist. Exiting.")
        exit()

FILE_NAME = file_path
# Load the data from the CSV file
csv_file_path = FILE_NAME
df = pd.read_csv(csv_file_path, parse_dates=["time"])

# Adjusted to handle both 'time' and '_time' column names
if 'time' in df.columns:
    df = df.sort_values("time").reset_index(drop=True)
elif '_time' in df.columns:
    df = df.rename(columns={'_time': 'time'})
    df = df.sort_values("time").reset_index(drop=True)
else:
    print("Error: Neither 'time' nor '_time' column found in the dataset.")
    exit()

# Step-by-step user interaction
# Ask the user if they want to add Time-based Features
add_time_features_input = input("Do you want to add Time-based Features? (yes/no): ").strip().lower()
if add_time_features_input == "yes":
    df = add_time_features(df)
    print(df.head(10))

# Ask the user if they want to add a time threshold for grouping events into sessions
add_session_grouping = input("Do you want to add a time threshold for grouping events into sessions? (yes/no): ").strip().lower()
if add_session_grouping == "yes":
    session_threshold_minutes = int(input("Enter the session threshold in minutes: ").strip())
    df = group_sessions(df, session_threshold_minutes)
    print(df.head(10))

# Add a Burst Indicator with user-defined categories
add_burst_indicator_input = input("Do you want to add a Burst Indicator? (yes/no): ").strip().lower()
if add_burst_indicator_input == "yes":
    while True:
        burst_name = input("Enter the name for this short burst category: ").strip()
        max_length = input(f"Enter the maximum event length (in seconds) for {burst_name} (or 'none' to skip): ").strip()
        max_volume = input(f"Enter the maximum event volume (in gallons) for {burst_name} (or 'none' to skip): ").strip()
        max_flow_rate = input(f"Enter the maximum average flow rate (or 'none' to skip): ").strip()

        conditions = []
        if max_length != "none":
            conditions.append(f"eventLength < {max_length}")
        if max_volume != "none":
            conditions.append(f"eventVolume < {max_volume}")
        if max_flow_rate != "none":
            conditions.append(f"avgFlowRate < {max_flow_rate}")

        condition = " and ".join(conditions)

        if condition:
            df = add_burst_indicator(df, burst_name, condition)
        else:
            print("No valid condition provided. Skipping this burst category.")

        add_another = input("Do you want to add another short burst category? (yes/no): ").strip().lower()
        if add_another != "yes":
            break

# Ask the user if they want to remove rows based on a specific Burst Indicator value
remove_rows = input("Do you want to remove rows with a specific Burst Indicator value? (yes/no): ").strip().lower()
if remove_rows == "yes":
    burst_value = input("Enter the Burst Indicator value to remove: ").strip()
    df = remove_rows_by_value(df, "burst_indicator", burst_value)

# Ask the user if they want to apply preset rules from the JSON file
apply_preset_rules = input("Do you want to apply preset rules from 'rules.json'? (yes/no): ").strip().lower()
if apply_preset_rules == "yes":
    apply_rules(df, file_name="rules.json")

# Interactive Dataset Labeling
add_labels = input("Do you want to label the dataset? (yes/no): ").strip().lower()
if add_labels == "yes":
    while True:
        label_name = input("Enter the name for this label: ").strip()
        print("Define the conditions for this label step-by-step. Use 'none' to skip any value.")
        min_length = input("Enter the minimum event length (or 'none' to skip): ").strip()
        max_length = input("Enter the maximum event length (or 'none' to skip): ").strip()
        min_volume = input("Enter the minimum event volume (or 'none' to skip): ").strip()
        max_volume = input("Enter the maximum event volume (or 'none' to skip): ").strip()
        min_flow_rate = input("Enter the minimum average flow rate (or 'none' to skip): ").strip()
        max_flow_rate = input("Enter the maximum average flow rate (or 'none' to skip): ").strip()

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
            df = label_dataset(df, label_name, condition)
        else:
            print("No valid condition provided. Skipping this label.")

        add_another_label = input("Do you want to add another label? (yes/no): ").strip().lower()
        if add_another_label != "yes":
            break

# Check if the 'label' column exists before summarizing
if 'label' in df.columns:
    label_summary = df['label'].value_counts()
    print("Labeling Summary:")
    print(label_summary)

    summary_file = "labeling_summary.txt"
    with open(summary_file, "w") as f:
        f.write("Labeling Summary:\n")
        f.write(label_summary.to_string())
    print(f"Labeling summary saved to {summary_file}")

# Ask the user if they want to remove rows without labels
remove_unlabeled_rows_input = input("Do you want to remove rows without labels? (yes/no): ").strip().lower()
if remove_unlabeled_rows_input == "yes":
    df = remove_unlabeled_rows(df)

# Ask the user whether to overwrite the file or save with a new name
output_file = input("Enter the output file name (or press Enter to overwrite '85day_labeled.csv'): ")
if not output_file:
    output_file = FILE_NAME

save_dataframe(df, output_file)
print(f"Features saved to {output_file}")