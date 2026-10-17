"""Train, compare and save the wine quality model.   Usage: python train_model.py"""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.ml import DATA_PATH, FEATURE_KEYS, METRICS_PATH, MODEL_PATH, MODEL_VERSION


def scores(y_true, y_pred):
    return dict(rmse=float(np.sqrt(mean_squared_error(y_true, y_pred))),
                mae=float(mean_absolute_error(y_true, y_pred)),
                r2=float(r2_score(y_true, y_pred)),
                within_half=float(np.mean(np.abs(y_true - y_pred) <= 0.5)))


def main():
    df = pd.read_csv(DATA_PATH, sep=";")
    X, y = df[FEATURE_KEYS], df["quality"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y.clip(upper=7))

    candidates = {
        "Ridge Regression": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
        "Extra Trees": ExtraTreesRegressor(n_estimators=300, random_state=42, n_jobs=-1),
        "Random Forest": RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
    }
    comparison = []
    for name, m in candidates.items():
        cv = -cross_val_score(m, Xtr, ytr, cv=5, scoring="neg_root_mean_squared_error").mean()
        m.fit(Xtr, ytr)
        comparison.append(dict(model=name, cv_rmse=float(cv), **scores(yte, m.predict(Xte))))
        print(f"{name:20s} CV-RMSE {cv:.3f}  test {comparison[-1]['rmse']:.3f}  R2 {comparison[-1]['r2']:.3f}")

    # Deployed model: tuned Random Forest (its trees give a per-prediction confidence)
    grid = GridSearchCV(RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
                        {"max_depth": [None, 12, 20], "min_samples_leaf": [1, 2, 3], "max_features": ["sqrt", 0.5]},
                        cv=5, scoring="neg_root_mean_squared_error", n_jobs=-1).fit(Xtr, ytr)
    best = grid.best_estimator_
    pred = best.predict(Xte)
    final = scores(yte, pred)
    print("Tuned Random Forest:", grid.best_params_, final)

    hi = df[df.quality >= 7]
    bundle = dict(
        model=best, features=FEATURE_KEYS,
        stats=dict(min=X.min().to_dict(), max=X.max().to_dict(), mean=X.mean().to_dict(),
                   ideal=hi[FEATURE_KEYS].mean().to_dict()),
        importances=dict(zip(FEATURE_KEYS, map(float, best.feature_importances_))))
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(bundle, MODEL_PATH, compress=3)
    METRICS_PATH.write_text(json.dumps(dict(
        version=MODEL_VERSION, best_params=grid.best_params_, final=final, comparison=comparison,
        n_train=len(Xtr), n_test=len(Xte), test_actual=yte.tolist(), test_pred=[float(p) for p in pred],
        importances=bundle["importances"]), indent=2))


if __name__ == "__main__":
    main()
