# Water Usage Signature Detection - ML Plan

## 🌟 Goal
Train a supervised machine learning model to classify household water usage events by appliance or fixture (e.g., shower, faucet, toilet, washing machine, dishwasher, fridge, sprinkler).

---

## 🔎 Step 1: Analyze Events & Engineer Features

### Existing Features:
- `eventVolume`
- `avgFlowRate`
- `eventLength`
- `eventPeaks`
- `peakFlowRate`
- `timestamp`

### Feature Engineering Ideas:
- **Time of Day**: Extract hour, morning/afternoon/evening labels
- **Day of Week**: May help identify routine behaviors (e.g., laundry on weekends)
- **Time Since Last Event**: Useful for session grouping and burst detection
- **Is Weekend**: Boolean feature to separate workday from rest day patterns
- **Burst Indicator**: Label short bursts (for ice maker, toilet flush)
- **Rolling Stats**: Moving average of volume or flow rate across last N events
- **Gap to Next Event**: For future session detection or segmentation
- **Event Group ID**: To tag related events (optional during pre-processing)

---

## ⌚️ Step 2: Group Related Events into Sessions (optional)
Used for appliances with multiple bursts (e.g., washing machine, dishwasher).

### Rules:
- Group events within 30 min of each other
- Total session duration, volume, flow, and event count
- Label the grouped session when patterns match known appliance usage

---

## 📄 Step 3: Label the Dataset for Training
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

## 🧪 Step 4: Train the Classifier

### Models to Try:
- Random Forest
- kNN
- Support Vector Machine (SVM)

### Pipeline:
- Train/test split
- Feature scaling
- Cross-validation
- Accuracy, F1-score, confusion matrix

---

## ⚖️ Step 5: Evaluate and Iterate

- Analyze model performance
- Identify and refine poorly predicted labels
- Revisit labeling rules and session grouping
- Add more labeled data

---

## 🚀 Step 6: Deploy to Mobile (TensorFlow Lite)

- Convert trained model to TFLite
- Optimize with quantization
- Embed in mobile app (Android/iOS)
- Run inference locally for real-time classification

---

## ✅ Next Steps:
1. Implement feature engineering
2. Develop grouping logic for appliance sessions
3. Apply rule-based labeling on dataset
4. Prototype a basic ML model with labeled events

---

