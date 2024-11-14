import yfinance as yf
from xgboost import XGBClassifier
from sklearn.metrics import precision_score
import pandas as pd


#function cleans and loads the data
def load_data(ticker, start_date="1990-01-01"):
    """Load historical data for a specified ticker and clean unnecessary columns."""
    data = yf.Ticker(ticker).history(period="max")
    data = data.loc[start_date:].copy()
    del data["Dividends"]
    del data["Stock Splits"]
    return data

def add_target(data):
    """Add the target and tomorrow columns for prediction."""
    data["Tomorrow"] = data["Close"].shift(-1)
    data["Target"] = (data["Tomorrow"] > data["Close"]).astype(int)
    return data

def create_rolling_features(data, horizons):
    """Add rolling average and trend features based on specified horizons."""
    for horizon in horizons:
        rolling_averages = data["Close"].rolling(horizon).mean()
        
        ratio_column = f"Close_Ratio_{horizon}"
        data[ratio_column] = data["Close"] / rolling_averages

        trend_column = f"Trend_{horizon}"
        data[trend_column] = data["Target"].shift(1).rolling(horizon).sum()
    
    return data.dropna()

def train_and_predict(train, test, predictors, model):
    """Train the model and predict with a specified probability threshold."""
    model.fit(train[predictors], train["Target"])
    preds = model.predict_proba(test[predictors])[:, 1]
    preds[preds >= 0.5] = 1
    preds[preds < 0.5] = 0
    return pd.Series(preds, index=test.index, name="Predictions")

def backtest(data, model, predictors, start=2500, step=250):
    """Run a backtest over the data by iterating training and testing periods."""
    all_predictions = []
    for i in range(start, data.shape[0], step):
        train = data.iloc[0:i].copy()
        test = data.iloc[i : (i + step)].copy()
        predictions = train_and_predict(train, test, predictors, model)
        combined = pd.concat([test["Target"], predictions], axis=1)
        all_predictions.append(combined)
    
    return pd.concat(all_predictions)

def run_trading_bot(ticker, start_date="1990-01-01", horizons=[2, 5, 60, 250, 1000]):
    """Main function to run the trading bot for any given stock ticker."""
    # Load and prepare data
    data = load_data(ticker, start_date)
    data = add_target(data)
    
    # Model initialization
    model = XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=1)

    
    # Create predictors based on rolling averages and trends
    data = create_rolling_features(data, horizons)
    predictors = [f"Close_Ratio_{h}" for h in horizons] + [f"Trend_{h}" for h in horizons]
    
    # Run backtest and evaluate results
    predictions = backtest(data, model, predictors)
    print(predictions["Predictions"].value_counts() / predictions.shape[0])
    print("Precision:", precision_score(predictions["Target"], predictions["Predictions"]))
    
    


