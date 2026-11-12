import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Dummy training data
X = np.array([
    [30, 40, 0],
    [45, 20, 0],
    [20, 80, 10],
    [35, 30, 0],
    [25, 60, 5]
])

y = np.array([1, 1, 0, 1, 0])

model = RandomForestClassifier()
model.fit(X, y)

# ✅ THIS FUNCTION MUST EXIST
def predict_fire(temp, humidity, rainfall):
    data = np.array([[temp, humidity, rainfall]])
    pred = model.predict(data)[0]
    prob = model.predict_proba(data)[0][1]

    result = "🔥 Fire" if pred == 1 else "✅ No Fire"
    return result, round(prob * 100, 2)