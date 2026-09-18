from app.anomaly_detector import detect_anomalies

anomalies = detect_anomalies()

print("Number of anomalies:", len(anomalies))
print("First 5 anomalies:")

for anomaly in anomalies[:5]:
    print(anomaly)