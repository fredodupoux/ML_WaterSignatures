# Water Usage Signature Detection - ML Plan
This project is designed to add a machine learning feature for an iOS App that is paired with an IoT device that monitors water usage in a household. The IoT device stores high-resolution data in a time series database through InfluxDB integration, featuring real-time data visualization and usage tracking.

## 🌟 Goal
Train a supervised machine learning model to classify household water usage events by appliance or fixture (e.g., shower, faucet, toilet, washing machine, dishwasher, fridge, sprinkler). 

---

## 🔍 Analyze Events & Engineer Features

### 🛠️ Existing Features:
- `eventVolume`
- `avgFlowRate`
- `eventLength`
- `eventPeaks`
- `peakFlowRate`
- `timestamp`

### 💡 Feature Engineering Ideas:
- **⏰ Time of Day**: Extract hour, morning/afternoon/evening labels
- **📅 Day of Week**: May help identify routine behaviors (e.g., laundry on weekends)
- **⏳ Time Since Last Event**: Useful for session grouping and burst detection
- **🏖️ Is Weekend**: Boolean feature to separate workday from rest day patterns
- **💥 Burst Indicator**: Label short bursts (for ice maker, toilet flush)
- **📈 Rolling Stats**: Moving average of volume or flow rate across last N events
- **➡️ Gap to Next Event**: For future session detection or segmentation
- **🔗 Event Group ID**: To tag related events (optional during pre-processing)

---

## 🔗 Group Related Events into Sessions (optional)
Used for appliances with multiple bursts (e.g., washing machine, dishwasher).

### 📜 Rules:
- Group events within 30 min of each other
- Total session duration, volume, flow, and event count
- Label the grouped session when patterns match known appliance usage

---

## 🏷️ Label the Dataset for Training
Start by applying rule-based heuristics to label ~200–300 samples manually.

| Condition | Label |
|----------|-------|
| `eventLength > 300`, `eventVolume > 10` | `shower` |
| `eventLength < 10`, `eventVolume < 1` | `faucet` or `toilet` |
| Multiple bursts over 30 min, 5–10 gal total | `washing_machine` |
| Single long event, 3–6 gal, >20 min | `dishwasher` |
| Very short, low volume (<0.2 gal) | `fridge/ice` |
| Long duration, high volume (>50 gal) | `sprinkler` |

---

## 🤖 Train the Classifier

### 🧪 Models to Try:
- Random Forest
- kNN
- Support Vector Machine (SVM)

### 🛠️ Pipeline:
- Train/test split
- Feature scaling
- Cross-validation
- Accuracy, F1-score, confusion matrix

---

## 📊 Evaluate and Iterate

- Analyze model performance
- Identify and refine poorly predicted labels
- Revisit labeling rules and session grouping
- Add more labeled data

---

## 📱 Deploy to Mobile (TensorFlow Lite)

- Convert trained model to TFLite
- Optimize with quantization
- Embed in mobile app (Android/iOS)
- Run inference locally for real-time classification

---

## 🐍 Python Script Overview
The `feature_engineering.py` script is an interactive tool for preprocessing and feature engineering of water usage datasets. It allows users to:

- Add time-based features (e.g., hour, day of the week, part of the day).
- Group events into sessions based on a time threshold.
- Add burst indicators for specific event patterns.
- Apply preset rules from a JSON file.
- Label the dataset interactively based on user-defined conditions.
- Remove rows without labels or specific burst indicators.
- Save the processed dataset to a new file.

---

## 🚀 How to Run the Script

To use the `dataPreparation.py` script for preprocessing and feature engineering, follow these steps:

1. **Install Dependencies**:
   Ensure you have Python 3.8 or later installed. Install the required libraries using pip:
   ```bash
   pip install pandas
   ```

2. **Prepare Your Dataset**:
   Place your CSV file(s) in the same directory as the script or specify the path when prompted.

3. **Run the Script**:
   Execute the script in your terminal:
   ```bash
   python3 dataPreparation.py
   ```

4. **Follow the Interactive Prompts**:
   - Select the dataset file to process.
   - Choose whether to add time-based features, group events into sessions, or add burst indicators.
   - Apply preset rules or label the dataset interactively.
   - Save the processed dataset to a new file or overwrite the existing one.

5. **Output**:
   The processed dataset will be saved in the specified output file, ready for further analysis or model training.

