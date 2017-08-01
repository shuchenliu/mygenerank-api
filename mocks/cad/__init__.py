
#pretends to get baseline risk
def get_baseline_risk(sex_response, ancestry_response, age, cholesterol_total, cholesterol_HDL,
                      systolic_blood_pressure_untreated, systolic_blood_pressure_treated, smoker, diabetic):
    return 3

#pretends to get combined risk
def get_combined_risk(baseline_risk, odds_category, average_odds):
    return 5

#pretends to get lifestyle risk
def get_lifestyle_risk(smoking, obese, physically_active, healthy_diet,
                   initial_risk):
    return 7
