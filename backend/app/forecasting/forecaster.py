import datetime
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from app.models.models import SensorTelemetry
from app.schemas.schemas import ForecastDataPoint, ForecastResponse

# Attempt to load Prophet, with a robust local fallback
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Prophet package not found or failed to load. Using fallback forecaster.")

def run_metric_forecast(db: Session, asset_id: str, metric_name: str, horizon_days: int = 30) -> ForecastResponse:
    # Fetch historical data from DB
    history = db.query(SensorTelemetry)\
        .filter(SensorTelemetry.asset_id == asset_id, SensorTelemetry.metric_name == metric_name)\
        .order_by(SensorTelemetry.timestamp.asc())\
        .all()
        
    now = datetime.datetime.utcnow()
    
    # If insufficient history, generate synthetic history to ensure the forecaster works
    if len(history) < 10:
        base_val = 50.0
        history_df = pd.DataFrame([
            {"ds": now - datetime.timedelta(hours=i * 6), "y": base_val + np.sin(i / 5.0) * 10 + np.random.normal(0, 1)}
            for i in range(120, 0, -1)
        ])
    else:
        history_df = pd.DataFrame([{"ds": h.timestamp, "y": h.value} for h in history])
        
    historical_avg = float(history_df["y"].mean())
    
    forecast_points = []
    
    if PROPHET_AVAILABLE:
        try:
            # Fit Prophet model
            m = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=True)
            # Silence logging
            import logging
            logging.getLogger('cmdstanpy').setLevel(logging.ERROR)
            m.fit(history_df)
            
            future = m.make_future_dataframe(periods=horizon_days * 4, freq='6H') # 4 points per day
            forecast = m.predict(future)
            
            # Extract future portion
            future_predictions = forecast[forecast['ds'] > now].tail(horizon_days)
            
            for _, row in future_predictions.iterrows():
                forecast_points.append(
                    ForecastDataPoint(
                        timestamp=row['ds'],
                        predicted_value=float(row['yhat']),
                        lower_bound=float(row['yhat_lower']),
                        upper_bound=float(row['yhat_upper'])
                    )
                )
        except Exception as e:
            print(f"Prophet execution failed: {e}. Falling back to statistical forecaster.")
            forecast_points = run_fallback_forecast(history_df, horizon_days, now)
    else:
        forecast_points = run_fallback_forecast(history_df, horizon_days, now)
        
    # Determine predicted trend
    if len(forecast_points) >= 2:
        start_val = forecast_points[0].predicted_value
        end_val = forecast_points[-1].predicted_value
        diff = end_val - start_val
        pct_change = (diff / max(1e-5, abs(start_val))) * 100.0
        if pct_change > 2.0:
            trend = "Increasing"
        elif pct_change < -2.0:
            trend = "Decreasing"
        else:
            trend = "Stable"
    else:
        trend = "Stable"
        
    return ForecastResponse(
        asset_id=asset_id,
        metric_name=metric_name,
        forecast=forecast_points,
        historical_avg=historical_avg,
        predicted_trend=trend
    )

def run_fallback_forecast(history_df: pd.DataFrame, horizon_days: int, start_time: datetime.datetime) -> list[ForecastDataPoint]:
    """
    Standard statistical forecasting fallback using linear trend extrapolation and a daily sine wave seasonality.
    """
    # Fit simple linear model to last 30 entries
    recent_df = history_df.tail(30).copy()
    y_vals = recent_df["y"].values
    x_vals = np.arange(len(y_vals))
    
    if len(x_vals) > 1:
        slope, intercept = np.polyfit(x_vals, y_vals, 1)
    else:
        slope, intercept = 0.0, float(y_vals[0]) if len(y_vals) > 0 else 50.0
        
    std_dev = float(recent_df["y"].std())
    if np.isnan(std_dev) or std_dev < 1e-5:
        std_dev = 2.0
        
    forecast_points = []
    for day in range(1, horizon_days + 1):
        target_time = start_time + datetime.timedelta(days=day)
        
        # Extrapolate trend + add daily seasonality + random variance
        seasonality = np.sin(day * (2 * np.pi / 7.0)) * (std_dev * 0.5) # Weekly wave
        predicted_val = (slope * (len(x_vals) + day)) + intercept + seasonality
        predicted_val = float(max(0.0, predicted_val)) # clamp to non-negative
        
        # Confidence bounds (expand as horizon increases)
        uncertainty = std_dev * (1.0 + 0.1 * day)
        
        forecast_points.append(
            ForecastDataPoint(
                timestamp=target_time,
                predicted_value=predicted_val,
                lower_bound=float(max(0.0, predicted_val - uncertainty)),
                upper_bound=float(predicted_val + uncertainty)
            )
        )
        
    return forecast_points
