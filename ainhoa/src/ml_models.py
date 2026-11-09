"""
src/ml_models.py - Algoritmos de Machine Learning optimizados para alta velocidad y fiabilidad.
"""

import math
import random
import time
from typing import List, Tuple, Dict, Any

def calcular_metricas(y_true: List[int], y_pred: List[int]) -> Dict[str, Any]:
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)

    total = max(len(y_true), 1)
    acc = (tp + tn) / total
    rec = tp / max(tp + fn, 1)
    prec = tp / max(tp + fp, 1)
    f1 = 2 * (prec * rec) / max(prec + rec, 1e-9)

    return {
        "accuracy": round(acc, 4),
        "recall": round(rec, 4),
        "precision": round(prec, 4),
        "f1": round(f1, 4),
        "matriz_confusion": {"TP": tp, "TN": tn, "FP": fp, "FN": fn}
    }


class SMOTEBalancer:
    def __init__(self, k_neighbors: int = 5, seed: int = 42):
        self.k = k_neighbors
        self.seed = seed

    def fit_resample(self, X: List[List[float]], y: List[int]) -> Tuple[List[List[float]], List[int]]:
        random.seed(self.seed)
        c0_idx = [i for i, label in enumerate(y) if label == 0]
        c1_idx = [i for i, label in enumerate(y) if label == 1]

        if len(c0_idx) == len(c1_idx):
            return list(X), list(y)

        min_idx = c1_idx if len(c1_idx) < len(c0_idx) else c0_idx
        min_label = y[min_idx[0]]
        diff = abs(len(c0_idx) - len(c1_idx))

        X_resampled = [list(row) for row in X]
        y_resampled = list(y)

        for _ in range(diff):
            base_idx = random.choice(min_idx)
            base_row = X[base_idx]
            vecino_idx = random.choice([idx for idx in min_idx if idx != base_idx] or [base_idx])
            vecino_row = X[vecino_idx]

            alpha = random.random()
            sintetico = [b + alpha * (v - b) for b, v in zip(base_row, vecino_row)]
            X_resampled.append(sintetico)
            y_resampled.append(min_label)

        return X_resampled, y_resampled


class LogisticRegressionModel:
    def __init__(self, lr: float = 0.08, epochs: int = 70, reg_l2: float = 0.01):
        self.lr = lr
        self.epochs = epochs
        self.reg_l2 = reg_l2
        self.weights = []
        self.bias = 0.0

    def fit(self, X: List[List[float]], y: List[int]):
        n_samples = len(X)
        n_features = len(X[0])
        self.weights = [0.0] * n_features
        self.bias = 0.0

        for _ in range(self.epochs):
            for i in range(0, n_samples, 2): # mini-batch step 2
                xi = X[i]
                yi = y[i]
                z = sum(w * x for w, x in zip(self.weights, xi)) + self.bias
                z = max(-20.0, min(20.0, z))
                p = 1.0 / (1.0 + math.exp(-z))
                error = p - yi

                for j in range(n_features):
                    self.weights[j] -= self.lr * (error * xi[j] + self.reg_l2 * self.weights[j])
                self.bias -= self.lr * error
        return self

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        probs = []
        for xi in X:
            z = sum(w * x for w, x in zip(self.weights, xi)) + self.bias
            z = max(-20.0, min(20.0, z))
            probs.append(round(1.0 / (1.0 + math.exp(-z)), 4))
        return probs

    def predict(self, X: List[List[float]], threshold: float = 0.5) -> List[int]:
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]


class KNNClassifier:
    def __init__(self, k: int = 5):
        self.k = k
        self.X_train = []
        self.y_train = []

    def fit(self, X: List[List[float]], y: List[int]):
        # Submuestrear para agilizar búsqueda en memoria
        step = max(len(X) // 200, 1)
        self.X_train = [X[i] for i in range(0, len(X), step)]
        self.y_train = [y[i] for i in range(0, len(y), step)]
        return self

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        probs = []
        for xi in X:
            distancias = [
                (sum((a - b) ** 2 for a, b in zip(xi, xj)), self.y_train[j])
                for j, xj in enumerate(self.X_train)
            ]
            distancias.sort(key=lambda item: item[0])
            k_vecinos = distancias[:self.k]
            p = sum(label for _, label in k_vecinos) / self.k
            probs.append(round(p, 4))
        return probs

    def predict(self, X: List[List[float]], threshold: float = 0.5) -> List[int]:
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]


class SimpleDecisionStump:
    def __init__(self, feat: int, th: float, left: float, right: float):
        self.feat = feat
        self.th = th
        self.left = left
        self.right = right

    def predict_val(self, x: List[float]) -> float:
        return self.left if x[self.feat] <= self.th else self.right

class RandomForestModel:
    def __init__(self, n_estimators: int = 15, seed: int = 42):
        self.n_estimators = n_estimators
        self.seed = seed
        self.trees: List[SimpleDecisionStump] = []

    def fit(self, X: List[List[float]], y: List[int]):
        random.seed(self.seed)
        n_samples = len(X)
        n_features = len(X[0])
        self.trees = []

        for _ in range(self.n_estimators):
            boot_idx = [random.randint(0, n_samples - 1) for _ in range(n_samples // 2)]
            feat = random.randint(0, n_features - 1)
            vals = [X[i][feat] for i in boot_idx]
            vals.sort()
            th = vals[len(vals) // 2]

            left_y = [y[i] for i in boot_idx if X[i][feat] <= th]
            right_y = [y[i] for i in boot_idx if X[i][feat] > th]

            left_val = sum(left_y) / max(len(left_y), 1)
            right_val = sum(right_y) / max(len(right_y), 1)
            self.trees.append(SimpleDecisionStump(feat, th, left_val, right_val))
        return self

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        probs = []
        for xi in X:
            votes = [t.predict_val(xi) for t in self.trees]
            probs.append(round(sum(votes) / len(votes), 4))
        return probs

    def predict(self, X: List[List[float]], threshold: float = 0.5) -> List[int]:
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]


class XGBoostModel:
    def __init__(self, n_estimators: int = 20, lr: float = 0.12, seed: int = 42):
        self.n_estimators = n_estimators
        self.lr = lr
        self.seed = seed
        self.base_pred = 0.0
        self.trees: List[SimpleDecisionStump] = []

    def fit(self, X: List[List[float]], y: List[int]):
        random.seed(self.seed)
        n_samples = len(X)
        n_features = len(X[0])
        self.base_pred = sum(y) / n_samples
        residuals = [float(y[i] - self.base_pred) for i in range(n_samples)]
        self.trees = []

        for _ in range(self.n_estimators):
            feat = random.randint(0, n_features - 1)
            vals = [X[i][feat] for i in range(0, n_samples, 3)]
            vals.sort()
            th = vals[len(vals) // 2]

            left_res = [residuals[i] for i in range(n_samples) if X[i][feat] <= th]
            right_res = [residuals[i] for i in range(n_samples) if X[i][feat] > th]

            left_avg = (sum(left_res) / max(len(left_res), 1)) * self.lr
            right_avg = (sum(right_res) / max(len(right_res), 1)) * self.lr

            stump = SimpleDecisionStump(feat, th, left_avg, right_avg)
            self.trees.append(stump)

            for i in range(n_samples):
                residuals[i] -= stump.predict_val(X[i])
        return self

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        probs = []
        for xi in X:
            val = self.base_pred + sum(t.predict_val(xi) for t in self.trees)
            val = max(0.01, min(0.99, val))
            probs.append(round(val, 4))
        return probs

    def predict(self, X: List[List[float]], threshold: float = 0.5) -> List[int]:
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]


class SVMClassifier:
    def __init__(self, c_param: float = 1.0, epochs: int = 50, lr: float = 0.015):
        self.C = c_param
        self.epochs = epochs
        self.lr = lr
        self.w = []
        self.b = 0.0

    def fit(self, X: List[List[float]], y: List[int]):
        n_samples = len(X)
        n_features = len(X[0])
        self.w = [0.0] * n_features
        self.b = 0.0
        y_svm = [1 if val == 1 else -1 for val in y]

        for _ in range(self.epochs):
            for i in range(0, n_samples, 2):
                xi = X[i]
                yi = y_svm[i]
                margin = yi * (sum(w * x for w, x in zip(self.w, xi)) + self.b)
                if margin >= 1.0:
                    for j in range(n_features):
                        self.w[j] -= self.lr * (2.0 / self.C * self.w[j])
                else:
                    for j in range(n_features):
                        self.w[j] -= self.lr * (2.0 / self.C * self.w[j] - yi * xi[j])
                    self.b += self.lr * yi
        return self

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        probs = []
        for xi in X:
            raw_margin = sum(w * x for w, x in zip(self.w, xi)) + self.b
            p = 1.0 / (1.0 + math.exp(-max(-15.0, min(15.0, raw_margin * 1.5))))
            probs.append(round(p, 4))
        return probs

    def predict(self, X: List[List[float]], threshold: float = 0.5) -> List[int]:
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]


class MLPNeuralNetwork:
    def __init__(self, hidden_layers: Tuple[int, ...] = (16,), activation: str = "relu",
                 alpha: float = 0.0001, lr: float = 0.03, epochs: int = 25, seed: int = 42):
        self.hidden_layers = hidden_layers
        self.activation = activation
        self.alpha = alpha
        self.lr = lr
        self.epochs = epochs
        self.seed = seed
        self.weights = []
        self.biases = []

    def _act(self, z: float) -> float:
        return math.tanh(z) if self.activation == "tanh" else max(0.0, z)

    def _act_deriv(self, a: float) -> float:
        return 1.0 - a * a if self.activation == "tanh" else (1.0 if a > 0 else 0.0)

    def fit(self, X: List[List[float]], y: List[int]):
        random.seed(self.seed)
        n_features = len(X[0])
        layer_sizes = [n_features] + list(self.hidden_layers) + [1]

        self.weights = []
        self.biases = []
        for i in range(len(layer_sizes) - 1):
            fan_in = layer_sizes[i]
            fan_out = layer_sizes[i+1]
            scale = math.sqrt(2.0 / fan_in)
            W = [[random.gauss(0, scale) for _ in range(fan_out)] for _ in range(fan_in)]
            b = [0.0] * fan_out
            self.weights.append(W)
            self.biases.append(b)

        n_samples = len(X)
        for _ in range(self.epochs):
            for idx in range(0, n_samples, 2):
                xi = X[idx]
                target = y[idx]

                activations = [xi]
                for l in range(len(self.weights)):
                    W = self.weights[l]
                    b = self.biases[l]
                    prev_act = activations[-1]
                    next_act = []
                    for out_idx in range(len(b)):
                        z = sum(prev_act[in_idx] * W[in_idx][out_idx] for in_idx in range(len(prev_act))) + b[out_idx]
                        if l == len(self.weights) - 1:
                            z = max(-20.0, min(20.0, z))
                            next_act.append(1.0 / (1.0 + math.exp(-z)))
                        else:
                            next_act.append(self._act(z))
                    activations.append(next_act)

                output = activations[-1][0]
                delta = [output - target]

                for l in reversed(range(len(self.weights))):
                    W = self.weights[l]
                    b = self.biases[l]
                    prev_act = activations[l]

                    next_delta = [0.0] * len(prev_act)
                    for in_idx in range(len(prev_act)):
                        for out_idx in range(len(b)):
                            next_delta[in_idx] += W[in_idx][out_idx] * delta[out_idx]
                            grad = prev_act[in_idx] * delta[out_idx] + self.alpha * W[in_idx][out_idx]
                            W[in_idx][out_idx] -= self.lr * grad

                    for out_idx in range(len(b)):
                        b[out_idx] -= self.lr * delta[out_idx]

                    if l > 0:
                        delta = [next_delta[k] * self._act_deriv(prev_act[k]) for k in range(len(prev_act))]
        return self

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        probs = []
        for xi in X:
            act = xi
            for l in range(len(self.weights)):
                W = self.weights[l]
                b = self.biases[l]
                next_act = []
                for out_idx in range(len(b)):
                    z = sum(act[in_idx] * W[in_idx][out_idx] for in_idx in range(len(act))) + b[out_idx]
                    if l == len(self.weights) - 1:
                        z = max(-20.0, min(20.0, z))
                        next_act.append(1.0 / (1.0 + math.exp(-z)))
                    else:
                        next_act.append(self._act(z))
                act = next_act
            probs.append(round(act[0], 4))
        return probs

    def predict(self, X: List[List[float]], threshold: float = 0.5) -> List[int]:
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]
