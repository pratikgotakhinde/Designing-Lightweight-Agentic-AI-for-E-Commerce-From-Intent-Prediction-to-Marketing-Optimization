import os, json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

# Load the exact feature columns the model was trained on
with open(os.path.join(MODEL_DIR, "feature_cols.json")) as f:
    FEATURE_COLUMNS = json.load(f)

# Month labels shown in UI → must match the one-hot columns in FEATURE_COLUMNS
# e.g. if training used "Month_June", the UI value must be "June"
MONTHS = ["Feb", "Mar", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

VISITOR_TYPES = ["New_Visitor", "Returning_Visitor", "Other"]

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "June": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

VISITOR_MAP = {
    "Returning_Visitor": 1,
    "New_Visitor": 0,
    "Other": 0
}

def build_feature_row(inputs: dict) -> pd.DataFrame:
    row = {col: 0 for col in FEATURE_COLUMNS}

    # Fill numeric fields directly
    for col in [
        'Administrative', 'Administrative_Duration',
        'Informational', 'Informational_Duration',
        'ProductRelated', 'ProductRelated_Duration',
        'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay',
        'OperatingSystems', 'Browser', 'Region', 'TrafficType'
    ]:
        row[col] = inputs.get(col, 0)

    row['Weekend'] = 1 if inputs.get('Weekend') else 0

    # One-hot encode Month — use exact value from UI as suffix
    month = inputs.get('Month', '')
    month_col = f"Month_{month}"
    if month_col in row:
        row[month_col] = 1

    # One-hot encode VisitorType
    vtype = inputs.get('VisitorType', 'New_Visitor')
    vtype_col = f"VisitorType_{vtype}"
    if vtype_col in row:
        row[vtype_col] = 1

    # Reindex to exact model feature order (safety net)
    df = pd.DataFrame([row])
    df = df.reindex(columns=FEATURE_COLUMNS, fill_value=0)
    return df
