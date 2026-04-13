"""
generate_data.py
Generates synthetic LinkinReachly user funnel data for the analytics dashboard.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# ── CONFIG ────────────────────────────────────────────────────────────────
N_USERS = 1200
START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2024, 12, 31)

SOURCES = {
    "Organic Search": 0.35,
    "LinkedIn Ad":    0.25,
    "Referral":       0.18,
    "Product Hunt":   0.12,
    "Twitter/X":      0.10,
}

PLANS = {
    "Free":    0.70,
    "Pro":     0.22,
    "Team":    0.08,
}

# A/B test variants
AB_VARIANTS = {
    "A - Control (Old Onboarding)": 0.50,
    "B - Variant (AI Job Match)":   0.50,
}

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def weighted_choice(d):
    keys = list(d.keys())
    weights = list(d.values())
    return random.choices(keys, weights=weights, k=1)[0]

# ── GENERATE USERS ────────────────────────────────────────────────────────
users = []

for i in range(N_USERS):
    signup_date = random_date(START_DATE, END_DATE)
    source      = weighted_choice(SOURCES)
    plan        = weighted_choice(PLANS)
    ab_variant  = weighted_choice(AB_VARIANTS)

    # Conversion rates — variant B is better
    base_activate  = 0.72 if ab_variant == "B - Variant (AI Job Match)" else 0.58
    base_first_app = 0.85 if ab_variant == "B - Variant (AI Job Match)" else 0.74
    base_retain_7  = 0.52 if ab_variant == "B - Variant (AI Job Match)" else 0.38
    base_retain_30 = 0.31 if ab_variant == "B - Variant (AI Job Match)" else 0.22

    # Source adjustments
    source_mult = {
        "Referral": 1.15, "Product Hunt": 1.10,
        "Organic Search": 1.0, "LinkedIn Ad": 0.92, "Twitter/X": 0.85
    }.get(source, 1.0)

    # Plan adjustments
    plan_mult = {"Pro": 1.25, "Team": 1.40, "Free": 1.0}.get(plan, 1.0)

    def p(base):
        return min(0.98, base * source_mult * plan_mult + np.random.normal(0, 0.03))

    activated     = random.random() < p(base_activate)
    first_applied = activated and random.random() < p(base_first_app)
    retained_7    = first_applied and random.random() < p(base_retain_7)
    retained_30   = retained_7 and random.random() < p(base_retain_30)

    # Engagement metrics (only for activated users)
    sessions_per_week = 0
    applies_per_session = 0
    ai_applies_pct = 0
    msg_open_rate = 0
    followup_click_rate = 0

    if activated:
        sessions_per_week = max(1, int(np.random.poisson(3.5 if retained_7 else 1.5)))
        applies_per_session = round(max(0.5, np.random.normal(
            4.2 if ab_variant == "B - Variant (AI Job Match)" else 2.8, 1.2)), 1)
        ai_applies_pct = round(min(1.0, max(0.1, np.random.normal(
            0.72 if plan == "Free" else 0.88, 0.12))), 2)
        msg_open_rate = round(min(1.0, max(0.05, np.random.normal(0.34, 0.10))), 2)
        followup_click_rate = round(min(1.0, max(0.02, np.random.normal(0.18, 0.07))), 2)

    users.append({
        "user_id":             f"U{i+1:05d}",
        "signup_date":         signup_date.strftime("%Y-%m-%d"),
        "signup_month":        signup_date.strftime("%Y-%m"),
        "source":              source,
        "plan":                plan,
        "ab_variant":          ab_variant,
        "activated":           int(activated),
        "first_applied":       int(first_applied),
        "retained_7d":         int(retained_7),
        "retained_30d":        int(retained_30),
        "sessions_per_week":   sessions_per_week,
        "applies_per_session": applies_per_session,
        "ai_applies_pct":      ai_applies_pct,
        "msg_open_rate":       msg_open_rate,
        "followup_click_rate": followup_click_rate,
    })

df = pd.DataFrame(users)
df.to_csv("data/users.csv", index=False)
print(f"Generated {len(df)} users → data/users.csv")
print(df[["activated","first_applied","retained_7d","retained_30d"]].mean().round(3))
