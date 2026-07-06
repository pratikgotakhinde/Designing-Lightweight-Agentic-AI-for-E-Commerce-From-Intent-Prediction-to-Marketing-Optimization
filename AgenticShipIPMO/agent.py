import os, json, pickle, shap

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

def _path(f):
    return os.path.join(MODEL_DIR, f)

with open(_path("thresholds.json")) as f:
    _t = json.load(f)

HIGH_THRESHOLD   = _t["HIGH_THRESHOLD"]
MEDIUM_THRESHOLD = _t["MEDIUM_THRESHOLD"]


class IntentScoringAgent:
    def __init__(self):
        with open(_path("xgb_model.pkl"), "rb") as f:
            self.model = pickle.load(f)

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
    def __init__(self, model, feature_names):
        self.explainer     = shap.TreeExplainer(model)
        self.feature_names = feature_names

    def explain(self, features_df):
        sv = self.explainer.shap_values(features_df)
        shap_vals = sv[1][0] if isinstance(sv, list) else sv[0]
        pairs = sorted(
            zip(self.feature_names, shap_vals),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        return [(name, round(val, 4)) for name, val in pairs[:3]]


class MarketingActionAgent:
    def decide(self, tier):
        return {
            "HIGH":   {"action": "Show Urgency Banner",  "message": "Only a few left — grab yours before it's gone.", "cost": 0.00, "color": "green"},
            "MEDIUM": {"action": "Offer 10% Discount",   "message": "Here's 10% off — just for this session.",        "cost": 5.00, "color": "orange"},
            "LOW":    {"action": "Queue Retargeting Ad", "message": "Come back soon — your cart is waiting.",          "cost": 0.50, "color": "red"},
        }[tier]


class AgenticOrchestrator:
    def __init__(self):
        with open(_path("feature_cols.json")) as f:
            self.feature_names = json.load(f)
        self.scorer    = IntentScoringAgent()
        self.explainer = ExplanationAgent(self.scorer.model, self.feature_names)
        self.actor     = MarketingActionAgent()

    def run(self, features_df):
        score, tier  = self.scorer.score(features_df)
        top_features = self.explainer.explain(features_df)
        action       = self.actor.decide(tier)
        return {
            "score":        score,
            "tier":         tier,
            "top_features": top_features,
            "action":       action,
        }