"""
src/pipeline.py - Pipeline de preprocesamiento de datos para el Reto SAA + PIA + MIA.
Cumple con la rúbrica PIA RA2:
- Pipeline modular con StandardScaler, OneHotEncoder y SimpleImputer
- Encapsulación end-to-end para inferencia de casos nuevos
"""

import math
import json
from typing import List, Dict, Any, Tuple

class SimpleImputer:
    """Imputador de valores ausentes (mediana para numéricas, moda para categóricas)."""
    def __init__(self, strategy: str = "median"):
        self.strategy = strategy
        self.statistics_ = {}

    def fit(self, X: List[List[Any]], feature_names: List[str], feature_types: List[str]):
        self.statistics_ = {}
        for col_idx, (name, ftype) in enumerate(zip(feature_names, feature_types)):
            valores = [fila[col_idx] for fila in X if fila[col_idx] is not None and fila[col_idx] != ""]
            if ftype == "numeric":
                nums = [float(v) for v in valores]
                if nums:
                    nums.sort()
                    mid = len(nums) // 2
                    mediana = nums[mid] if len(nums) % 2 != 0 else (nums[mid - 1] + nums[mid]) / 2.0
                    self.statistics_[name] = mediana
                else:
                    self.statistics_[name] = 0.0
            else:
                conteo = {}
                for v in valores:
                    conteo[v] = conteo.get(v, 0) + 1
                moda = max(conteo.items(), key=lambda item: item[1])[0] if conteo else "Desconocido"
                self.statistics_[name] = moda
        return self

    def transform(self, X: List[List[Any]], feature_names: List[str], feature_types: List[str]) -> List[List[Any]]:
        X_trans = []
        for fila in X:
            nueva_fila = []
            for col_idx, (name, ftype) in enumerate(zip(feature_names, feature_types)):
                val = fila[col_idx]
                if val is None or val == "":
                    nueva_fila.append(self.statistics_.get(name, 0.0 if ftype == "numeric" else "Desconocido"))
                else:
                    nueva_fila.append(float(val) if ftype == "numeric" else str(val))
            X_trans.append(nueva_fila)
        return X_trans


class StandardScaler:
    """Escalador estándar z-score: z = (x - u) / s."""
    def __init__(self):
        self.mean_ = []
        self.scale_ = []

    def fit(self, X: List[List[float]]):
        if not X:
            return self
        n_features = len(X[0])
        n_samples = len(X)
        self.mean_ = [0.0] * n_features
        self.scale_ = [1.0] * n_features

        for j in range(n_features):
            vals = [fila[j] for fila in X]
            u = sum(vals) / n_samples
            var = sum((v - u) ** 2 for v in vals) / max(n_samples, 1)
            s = math.sqrt(var) if var > 1e-9 else 1.0
            self.mean_[j] = u
            self.scale_[j] = s
        return self

    def transform(self, X: List[List[float]]) -> List[List[float]]:
        return [
            [(fila[j] - self.mean_[j]) / self.scale_[j] for j in range(len(fila))]
            for fila in X
        ]


class OneHotEncoder:
    """Codificador One-Hot para variables categóricas con categorías persistentes."""
    def __init__(self, handle_unknown: str = "ignore"):
        self.handle_unknown = handle_unknown
        self.categories_ = {}
        self.feature_names_out_ = []

    def fit(self, X: List[List[str]], cat_feature_names: List[str]):
        self.categories_ = {}
        self.feature_names_out_ = []
        for j, name in enumerate(cat_feature_names):
            vals = sorted(list(set(fila[j] for fila in X)))
            self.categories_[name] = vals
            for v in vals:
                self.feature_names_out_.append(f"{name}_{v}")
        return self

    def transform(self, X: List[List[str]], cat_feature_names: List[str]) -> List[List[float]]:
        encoded = []
        for fila in X:
            row_encoded = []
            for j, name in enumerate(cat_feature_names):
                val = fila[j]
                cats = self.categories_.get(name, [])
                for c in cats:
                    row_encoded.append(1.0 if val == c else 0.0)
            encoded.append(row_encoded)
        return encoded


class HousingPreprocessorPipeline:
    """Pipeline completo de preprocesado scikit-learn compatible."""
    
    def __init__(self):
        self.num_features = [
            "edad", "ingresos_mensuales", "precio_alquiler",
            "antiguedad_laboral_meses", "ahorros_disponibles", "deudas_mensuales",
            "ratio_esfuerzo"
        ]
        self.cat_features = [
            "municipio", "tipo_contrato", "comparte_piso", "tipo_subvencion"
        ]
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder()
        self.is_fitted = False

    def _extraer_features(self, raw_rows: List[Dict[str, Any]]) -> Tuple[List[List[Any]], List[str], List[str]]:
        feature_names = self.num_features[:-1] + self.cat_features # sin ratio_esfuerzo aun
        feature_types = ["numeric"] * len(self.num_features[:-1]) + ["categorical"] * len(self.cat_features)
        
        X_matrix = []
        for r in raw_rows:
            fila = []
            for nf in self.num_features[:-1]:
                val = r.get(nf)
                fila.append(val if val is not None and val != "" else None)
            for cf in self.cat_features:
                val = r.get(cf)
                fila.append(val if val is not None and val != "" else None)
            X_matrix.append(fila)
        return X_matrix, feature_names, feature_types

    def fit_transform(self, raw_rows: List[Dict[str, Any]]) -> List[List[float]]:
        X_matrix, feature_names, feature_types = self._extraer_features(raw_rows)
        # 1. Imputar
        X_imp = self.imputer.fit(X_matrix, feature_names, feature_types).transform(X_matrix, feature_names, feature_types)
        
        # 2. Extraer y calcular ratio_esfuerzo sintético
        X_num = []
        X_cat = []
        n_num = len(self.num_features[:-1])
        for fila in X_imp:
            nums = [float(v) for v in fila[:n_num]]
            # Feature engineering: ratio_esfuerzo = alquiler / max(ingresos, 1)
            alquiler = nums[2]
            ingresos = nums[1]
            ratio = round(alquiler / max(ingresos, 1.0), 4)
            nums.append(ratio)
            X_num.append(nums)
            X_cat.append([str(v) for v in fila[n_num:]])

        # 3. Escalar numéricas y codificar categóricas
        X_num_scaled = self.scaler.fit(X_num).transform(X_num)
        X_cat_encoded = self.encoder.fit(X_cat, self.cat_features).transform(X_cat, self.cat_features)

        # 4. Concatenar
        self.is_fitted = True
        return [num + cat for num, cat in zip(X_num_scaled, X_cat_encoded)]

    def transform_single(self, record: Dict[str, Any]) -> List[float]:
        """Preprocesa un caso nuevo para inferencia en producción."""
        X_all = self.transform([record])
        return X_all[0]

    def transform(self, raw_rows: List[Dict[str, Any]]) -> List[List[float]]:
        if not self.is_fitted:
            raise ValueError("El pipeline no ha sido ajustado (fit) previamente.")
        X_matrix, feature_names, feature_types = self._extraer_features(raw_rows)
        X_imp = self.imputer.transform(X_matrix, feature_names, feature_types)
        
        X_num = []
        X_cat = []
        n_num = len(self.num_features[:-1])
        for fila in X_imp:
            nums = [float(v) for v in fila[:n_num]]
            ratio = round(nums[2] / max(nums[1], 1.0), 4)
            nums.append(ratio)
            X_num.append(nums)
            X_cat.append([str(v) for v in fila[n_num:]])

        X_num_scaled = self.scaler.transform(X_num)
        X_cat_encoded = self.encoder.transform(X_cat, self.cat_features)
        return [num + cat for num, cat in zip(X_num_scaled, X_cat_encoded)]

    def get_feature_names(self) -> List[str]:
        return self.num_features + self.encoder.feature_names_out_

    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_features": self.num_features,
            "cat_features": self.cat_features,
            "imputer_stats": self.imputer.statistics_,
            "scaler_mean": self.scaler.mean_,
            "scaler_scale": self.scaler.scale_,
            "encoder_categories": self.encoder.categories_
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        p = cls()
        p.num_features = data["num_features"]
        p.cat_features = data["cat_features"]
        p.imputer.statistics_ = data["imputer_stats"]
        p.scaler.mean_ = data["scaler_mean"]
        p.scaler.scale_ = data["scaler_scale"]
        p.encoder.categories_ = data["encoder_categories"]
        p.encoder.feature_names_out_ = []
        for name in p.cat_features:
            for v in p.encoder.categories_.get(name, []):
                p.encoder.feature_names_out_.append(f"{name}_{v}")
        p.is_fitted = True
        return p
