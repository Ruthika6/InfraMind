import datetime
import google.generativeai as genai
from typing import List, Dict, Any
from app.config.settings import settings
from app.schemas.schemas import SHAPFeatureImportance, PredictResponse, ExplainResponse

# Configure Gemini if key is provided
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_shap_values(asset_type: str, sensor_values: Dict[str, float], risk_score: float) -> List[SHAPFeatureImportance]:
    """
    Simulates SHAP values indicating feature importance based on telemetry divergence from normal values.
    """
    shap_list = []
    
    # Simple heuristics to calculate relative feature influence
    for metric, val in sensor_values.items():
        importance = 0.0
        direction = "Neutral"
        
        # Calculate deviation from midpoint of safety bounds
        if asset_type == "Bridge":
            if metric == "vibration":
                importance = val * 35.0
                direction = "Positive" if val > 0.25 else "Neutral"
            elif metric == "strain":
                importance = val / 10.0
                direction = "Positive" if val > 300.0 else "Neutral"
            elif metric == "load":
                importance = val / 5.0
                direction = "Positive" if val > 60.0 else "Negative"
        elif asset_type == "Dam":
            if metric == "water_level":
                importance = (val - 180.0) * 8.0
                direction = "Positive" if val > 198.0 else "Negative"
            elif metric == "seepage_rate":
                importance = val * 12.0
                direction = "Positive" if val > 6.0 else "Neutral"
        elif asset_type == "Pipeline":
            if metric == "gas_leak_ppm":
                importance = val * 0.8
                direction = "Positive" if val > 50.0 else "Neutral"
            elif metric == "pressure":
                # Low pressure or extremely high pressure is bad
                if val < 500.0:
                    importance = (500.0 - val) * 0.2
                    direction = "Positive" # adds to risk
                else:
                    importance = (val - 700.0) * 0.1
                    direction = "Positive" if val > 1100.0 else "Negative"
        elif asset_type == "PowerGrid":
            if metric == "temperature":
                importance = (val - 40.0) * 1.5
                direction = "Positive" if val > 80.0 else "Negative"
            elif metric == "voltage":
                dev = abs(val - 500.0)
                importance = dev * 2.0
                direction = "Positive" if dev > 15.0 else "Negative"
        else:
            importance = val * 5.0
            direction = "Positive" if val > 50.0 else "Negative"
            
        shap_list.append(
            SHAPFeatureImportance(
                feature_name=metric,
                importance_value=float(round(importance, 2)),
                impact_direction=direction
            )
        )
        
    # Sort by absolute importance value
    shap_list.sort(key=lambda x: abs(x.importance_value), reverse=True)
    return shap_list

def explain_prediction(asset_id: str, asset_name: str, asset_type: str, predict_res: PredictResponse, sensor_values: Dict[str, float]) -> ExplainResponse:
    shap_vals = generate_shap_values(asset_type, sensor_values, predict_res.risk_score)
    
    # Generate explanation text (Gemini or Fallback)
    explanation_text = ""
    alternative_scenarios = {}
    
    if settings.GEMINI_API_KEY:
        explanation_text, alternative_scenarios = explain_with_gemini(
            asset_name, asset_type, predict_res, shap_vals, sensor_values
        )
    else:
        explanation_text, alternative_scenarios = explain_with_templates(
            asset_name, asset_type, predict_res, shap_vals, sensor_values
        )
        
    return ExplainResponse(
        asset_id=asset_id,
        prediction=predict_res,
        shap_values=shap_vals,
        explanation_text=explanation_text,
        alternative_scenarios=alternative_scenarios,
        timestamp=datetime.datetime.utcnow()
    )

def explain_with_gemini(asset_name: str, asset_type: str, predict_res: PredictResponse, shap_vals: List[SHAPFeatureImportance], sensor_values: Dict[str, float]) -> tuple[str, Dict[str, str]]:
    prompt = f"""
    You are InfraMind AI, an expert structural engineering assistant and risk analyst for National Critical Infrastructure.
    Provide a professional engineering summary explaining the following health risk assessment:
    
    Asset Name: {asset_name}
    Asset Type: {asset_type}
    Risk Score: {predict_res.risk_score}%
    Remaining Useful Life: {predict_res.remaining_life_months} months
    Anomaly Detected: {predict_res.anomaly_detected}
    Failure Classification: {predict_res.failure_classification}
    Recommended Priority: {predict_res.recommended_repair_priority}
    
    Current Telemetry Metrics:
    {sensor_values}
    
    SHAP Feature Importance (influencing factors):
    {[f"{s.feature_name}: {s.importance_value} (Direction: {s.impact_direction})" for s in shap_vals]}
    
    Provide your output in exactly this format:
    ---
    ENGINEERING NARRATIVE:
    [Explain the mechanical reason for this prediction, why certain features triggered it, and the safety impact in a professional, authoritative paragraph.]
    
    ALTERNATIVE SCENARIOS:
    - Worst-Case: [Brief worst case scenario if ignored]
    - Mitigated: [Brief scenario if maintenance is performed immediately]
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text
        
        # Parse output
        narrative = ""
        worst_case = "Sudden structural failure if inspection dates are deferred."
        mitigated = "System health score restored to >90% upon component replacement."
        
        if "ENGINEERING NARRATIVE:" in text:
            parts = text.split("ALTERNATIVE SCENARIOS:")
            narrative = parts[0].replace("ENGINEERING NARRATIVE:", "").strip()
            if len(parts) > 1:
                scenarios_text = parts[1]
                for line in scenarios_text.split("\n"):
                    if "Worst-Case:" in line:
                        worst_case = line.replace("- Worst-Case:", "").strip()
                    elif "Mitigated:" in line:
                        mitigated = line.replace("- Mitigated:", "").strip()
        else:
            narrative = text
            
        return narrative, {"Worst-Case": worst_case, "Mitigated": mitigated}
    except Exception as e:
        print(f"Gemini API failure: {e}. Falling back to templates.")
        return explain_with_templates(asset_name, asset_type, predict_res, shap_vals, sensor_values)

def explain_with_templates(asset_name: str, asset_type: str, predict_res: PredictResponse, shap_vals: List[SHAPFeatureImportance], sensor_values: Dict[str, float]) -> tuple[str, Dict[str, str]]:
    top_feature = shap_vals[0].feature_name if len(shap_vals) > 0 else "Unknown"
    top_val = sensor_values.get(top_feature, 0.0)
    
    narrative = f"The risk model predicted a {predict_res.risk_score}% failure risk for {asset_name} ({asset_type}). " \
                f"The assessment was primarily driven by deviations in the parameter '{top_feature}' which is currently registered at {top_val:.2f}. " \
                f"This telemetry deviation correlates with historical signatures of the class '{predict_res.failure_classification}'. " \
                f"Recommended action is scheduled with {predict_res.recommended_repair_priority} priority before the target date of {predict_res.recommended_inspection_date.strftime('%Y-%m-%d')}."
                
    worst_case = f"A critical collapse or complete shutdown of {asset_name} resulting in substantial utility disruption and local traffic gridlocks."
    mitigated = f"Perform targeted repairs on components affecting {top_feature} to reduce stress indices, extending Remaining Useful Life by up to 36 months."
    
    return narrative, {"Worst-Case": worst_case, "Mitigated": mitigated}
