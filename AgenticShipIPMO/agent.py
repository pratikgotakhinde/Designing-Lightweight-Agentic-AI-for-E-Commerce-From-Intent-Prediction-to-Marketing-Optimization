import numpy as np
import shap
import joblib

# thresholds from the training analysis — tuned to balance precision and coverage
HIGH_THRESHOLD = 0.60
MEDIUM_THRESHOLD = 0.40


class IntentScoringAgent:
    # loads the saved xgboost model and scores a single user session
    def __init__(self, model_path="xgb_model.pkl"):
        self.model = joblib.load(model_path)

    def score(self, features_df):
        prob = self.model.predict_proba(features_df)[0][1]
        if prob >= HIGH_THRESHOLD:
            tier = "HIGH"
        elif prob >= MEDIUM_THRESHOLD:
            tier = "MEDIUM"
        else:
            tier = "LOW"
        return round(prob, 4), tier


class ExplanationAgent:
    # uses shap to pull the top 3 features that pushed this score up or down
    def __init__(self, model, feature_names):
        self.explainer = shap.TreeExplainer(model)
        self.feature_names = feature_names

    def explain(self, features_df):
        shap_vals = self.explainer.shap_values(features_df)[0]
        # pair each feature with its shap value and sort by absolute impact
        pairs = sorted(
            zip(self.feature_names, shap_vals),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        top3 = [(name, round(val, 4)) for name, val in pairs[:3]]
        return top3


class MarketingActionAgent:
    # rule-based action assignment — no llm needed here, just fast and auditable
    def decide(self, tier):
        actions = {
            "HIGH":   {"action": "Show Urgency Banner",  "cost": 0.00, "message": "Limited stock — order now!"},
            "MEDIUM": {"action": "Offer 10% Discount",   "cost": 5.00, "message": "Here's 10% off just for you."},
            "LOW":    {"action": "Retargeting Ad",        "cost": 0.50, "message": "Come back — your cart misses you."},
        }
        return actions[tier]


class AgenticOrchestrator:
    # ties all three agents together into one pipeline call
    def __init__(self, model_path="xgb_model.pkl", feature_names=None):
        self.scorer = IntentScoringAgent(model_path)
        self.explainer = ExplanationAgent(self.scorer.model, feature_names)
        self.actor = MarketingActionAgent()

    def run(self, features_df):
        score, tier = self.scorer.score(features_df)
        top_features = self.explainer.explain(features_df)
        action = self.actor.decide(tier)
        return {
            "score": score,
            "tier": tier,
            "top_features": top_features,
            "action": action,
        }