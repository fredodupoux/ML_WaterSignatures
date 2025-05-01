# This module will contain utility functions for data preparation.
import pandas as pd
import json

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

# Function to save rules to a file
def save_rules(rules, file_name="rules.json"):
    with open(file_name, "w") as f:
        json.dump(rules, f, indent=4)
    print(f"Rules saved to {file_name}")

# Function to add time-based features
def add_time_features(df):
    df["hour"] = df["time"].dt.hour
    df["day_of_week"] = df["time"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["part_of_day"] = pd.cut(df["hour"],
                               bins=[0, 6, 12, 18, 24],
                               labels=["night", "morning", "afternoon", "evening"],
                               right=False)
    df["time_since_last_event"] = df["time"].diff().fillna(pd.Timedelta(seconds=0)).dt.total_seconds()
    print("Time-based Features added.")
    return df

# Function to group events into sessions
def group_sessions(df, session_threshold_minutes):
    SESSION_THRESHOLD = session_threshold_minutes * 60  # Convert minutes to seconds
    df["session_id"] = (df["time_since_last_event"] > SESSION_THRESHOLD).cumsum()
    session_stats = df.groupby("session_id").agg(
        session_start=("time", "min"),
        session_end=("time", "max"),
        total_volume=("eventVolume", "sum"),
        total_duration=("eventLength", "sum"),
        event_count=("time", "count")
    ).reset_index()
    df = df.merge(session_stats, on="session_id", how="left")
    print("Session grouping added.")
    return df

# Function to add burst indicators
def add_burst_indicator(df, burst_name, conditions):
    df.loc[df.eval(conditions), "burst_indicator"] = burst_name
    print(f"Short burst category '{burst_name}' added based on condition: {conditions}.")
    return df

# Function to label the dataset
def label_dataset(df, label_name, conditions):
    df.loc[df.eval(conditions), "label"] = label_name
    print(f"Label '{label_name}' added based on condition: {conditions}.")
    return df

# Function to remove rows based on a column value
def remove_rows_by_value(df, column, value):
    initial_row_count = len(df)
    df = df[df[column] != value]
    removed_rows = initial_row_count - len(df)
    print(f"Removed {removed_rows} rows where {column} was '{value}'.")
    return df

# Function to remove rows without labels
def remove_unlabeled_rows(df):
    initial_row_count = len(df)
    df = df.dropna(subset=["label"])
    removed_rows = initial_row_count - len(df)
    print(f"Removed {removed_rows} rows without labels.")
    return df

# Function to save the dataframe to a CSV file
def save_dataframe(df, output_file):
    df.to_csv(output_file, index=False)
    print(f"Features saved to {output_file}")