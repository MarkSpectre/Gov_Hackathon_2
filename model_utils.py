import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

def run_model_pipeline(df):
    X = df.select_dtypes(include=np.number)
    y = X["total_activity"]

    X = X.drop(columns=["total_activity"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    return r2_score(y_test, preds), mean_absolute_error(y_test, preds)
