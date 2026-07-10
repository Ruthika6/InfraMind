import os
import pickle
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional
from sklearn.ensemble import IsolationForest, RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb

import torch
import torch.nn as nn
import torch.optim as optim

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
ISOLATION_FOREST_PATH = os.path.join(MODEL_DIR, "isolation_forest.pkl")
RUL_MODEL_PATH = os.path.join(MODEL_DIR, "rul_regressor.pkl")
PYTORCH_CLASSIFIER_PATH = os.path.join(MODEL_DIR, "pytorch_classifier.pt")

# PyTorch Network Definition for Failure Classification
class FailureClassifierNet(nn.Module):
    def __init__(self, input_dim: int = 5, num_classes: int = 5):
        super(FailureClassifierNet, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, num_classes)
        )
        
    def forward(self, x):
        return self.network(x)

class MLServicesManager:
    def __init__(self):
        self.anomaly_detector: Optional[IsolationForest] = None
        self.rul_regressor: Optional[Any] = None
        self.failure_classifier: Optional[FailureClassifierNet] = None
        self.classes = ["No Failure", "Structural Fracture", "Thermal Overheating", "Insulation Breakdown", "Seepage/Leakage"]
        
        # Load or initialize models
        self.initialize_models()
        
    def initialize_models(self):
        # Ensure model directory exists
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        # Initialize Anomaly Detector
        if os.path.exists(ISOLATION_FOREST_PATH):
            with open(ISOLATION_FOREST_PATH, "rb") as f:
                self.anomaly_detector = pickle.load(f)
        else:
            print("Training Anomaly Detector (Isolation Forest)...")
            self.train_anomaly_detector()
            
        # Initialize RUL Regressor
        if os.path.exists(RUL_MODEL_PATH):
            with open(RUL_MODEL_PATH, "rb") as f:
                self.rul_regressor = pickle.load(f)
        else:
            print("Training RUL Regressor (XGBoost/LightGBM/RF)...")
            self.train_rul_regressor()
            
        # Initialize Failure Classifier
        self.failure_classifier = FailureClassifierNet(input_dim=5, num_classes=len(self.classes))
        if os.path.exists(PYTORCH_CLASSIFIER_PATH):
            try:
                self.failure_classifier.load_state_dict(torch.load(PYTORCH_CLASSIFIER_PATH, weights_only=True))
                self.failure_classifier.eval()
            except Exception as e:
                print(f"Error loading PyTorch classifier weights: {e}, retraining...")
                self.train_pytorch_classifier()
        else:
            print("Training PyTorch Failure Classifier...")
            self.train_pytorch_classifier()

    def train_anomaly_detector(self):
        # Generate dummy sensor features: [vibration, temperature, load, strain, pressure]
        np.random.seed(42)
        normal_data = np.random.normal(loc=0.5, scale=0.1, size=(200, 5))
        anomalous_data = np.random.uniform(low=0.0, high=1.2, size=(20, 5))
        X = np.vstack([normal_data, anomalous_data])
        
        detector = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
        detector.fit(X)
        self.anomaly_detector = detector
        
        with open(ISOLATION_FOREST_PATH, "wb") as f:
            pickle.dump(detector, f)

    def train_rul_regressor(self):
        # Predict remaining useful life (in months) based on [age, health_score, vibration, temperature, load]
        np.random.seed(42)
        X = np.random.uniform(low=1.0, high=100.0, size=(300, 5))
        # Simple formula: age + health_score determines RUL
        y = (100.0 - X[:, 0]) * (X[:, 1] / 100.0) * 2.4
        y = np.clip(y, 1.0, 240.0) # between 1 and 240 months
        
        # Attempt to train with XGBoost
        try:
            regressor = xgb.XGBRegressor(n_estimators=50, max_depth=3, random_state=42)
            regressor.fit(X, y)
        except Exception:
            # Fallback to LightGBM or RandomForest
            try:
                regressor = lgb.LGBMRegressor(n_estimators=50, max_depth=3, random_state=42)
                regressor.fit(X, y)
            except Exception:
                regressor = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
                regressor.fit(X, y)
                
        self.rul_regressor = regressor
        with open(RUL_MODEL_PATH, "wb") as f:
            pickle.dump(regressor, f)

    def train_pytorch_classifier(self):
        # Features: [vibration, temperature, pressure, strain, frequency]
        # Labels: 0 (No Failure), 1 (Structural Fracture), 2 (Thermal Overheating), 3 (Insulation Breakdown), 4 (Seepage/Leakage)
        np.random.seed(42)
        torch.manual_seed(42)
        
        X = np.random.uniform(low=0.0, high=1.0, size=(500, 5))
        y = np.zeros(500, dtype=int)
        
        # Define mock heuristics for classification
        for i in range(500):
            if X[i, 0] > 0.8: # high vibration
                y[i] = 1 # Structural Fracture
            elif X[i, 1] > 0.8: # high temperature
                y[i] = 2 # Thermal Overheating
            elif X[i, 3] > 0.85: # high voltage/frequency anomaly
                y[i] = 3 # Insulation Breakdown
            elif X[i, 2] > 0.85: # pressure anomaly
                y[i] = 4 # Seepage/Leakage
                
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.long)
        
        optimizer = optim.Adam(self.failure_classifier.parameters(), lr=0.01)
        criterion = nn.CrossEntropyLoss()
        
        self.failure_classifier.train()
        for epoch in range(100):
            optimizer.zero_grad()
            outputs = self.failure_classifier(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
            
        self.failure_classifier.eval()
        torch.save(self.failure_classifier.state_dict(), PYTORCH_CLASSIFIER_PATH)

    def predict_anomaly(self, features: np.ndarray) -> bool:
        # returns True if anomalous
        if self.anomaly_detector is None:
            return False
        # IsolationForest returns -1 for anomalies, 1 for normal
        pred = self.anomaly_detector.predict(features.reshape(1, -1))
        return bool(pred[0] == -1)

    def predict_rul(self, features: np.ndarray) -> float:
        if self.rul_regressor is None:
            return 120.0
        pred = self.rul_regressor.predict(features.reshape(1, -1))
        return float(np.clip(pred[0], 0.0, 240.0))

    def predict_failure_mode(self, features: np.ndarray) -> Tuple[str, float]:
        # returns (failure_name, confidence)
        if self.failure_classifier is None:
            return "No Failure", 1.0
        
        tensor_feats = torch.tensor(features.reshape(1, -1), dtype=torch.float32)
        with torch.no_grad():
            outputs = self.failure_classifier(tensor_feats)
            probabilities = torch.softmax(outputs, dim=1)
            pred_idx = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0, pred_idx].item()
            
        return self.classes[pred_idx], float(confidence)

ml_manager = MLServicesManager()
