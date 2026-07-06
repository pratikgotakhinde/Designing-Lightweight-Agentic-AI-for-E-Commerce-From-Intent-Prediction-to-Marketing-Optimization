import os, json
import pandas as pd

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

with open(os.path.join(MODEL_DIR, "feature_cols.json")) as f:
    FEATURE_COLUMNS = json.load(f)

# month encoding matches what was used during training — order matters
MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "June": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

VISITOR_MAP = {
    "Returning_Visitor": 1,
    "New_Visitor": 0,
    "Other": 0
}

# these are the exact columns the xgb model was trained on after get_dummies
FEATURE_COLUMNS = [
    'Administrative', 'Administrative_Duration', 'Informational',
    'Informational_Duration', 'ProductRelated', 'ProductRelated_Duration',
    'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay',
    'OperatingSystems', 'Browser', 'Region', 'TrafficType', 'Weekend',
    'Month_Aug', 'Month_Dec', 'Month_Feb', 'Month_Jul', 'Month_June',
    'Month_Mar', 'Month_May', 'Month_Nov', 'Month_Oct', 'Month_Sep',
    'VisitorType_Other', 'VisitorType_Returning_Visitor'
]

MONTHS        = ["Feb", "Mar", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
VISITOR_TYPES = ["New_Visitor", "Returning_Visitor", "Other"]

def build_feature_row(inputs: dict) -> pd.DataFrame:
    row = {col: 0 for col in FEATURE_COLUMNS}

    # fill numeric fields directly
    for col in ['Administrative', 'Administrative_Duration', 'Informational',
                'Informational_Duration', 'ProductRelated', 'ProductRelated_Duration',
                'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay',
                'OperatingSystems', 'Browser', 'Region', 'TrafficType']:
        row[col] = inputs.get(col, 0)

    row['Weekend'] = 1 if inputs.get('Weekend') else 0

    # one-hot encode month
    month = inputs.get('Month', '')
    month_col = f"Month_{month}"
    if month_col in row:
        row[month_col] = 1

    # one-hot encode visitor type
    vtype = inputs.get('VisitorType', 'New_Visitor')
    vtype_col = f"VisitorType_{vtype}"
    if vtype_col in row:
        row[vtype_col] = 1

    return pd.DataFrame([row])[FEATURE_COLUMNS]