"""
Rule-based recommendation engine.

This module does not call any paid or generative AI APIs.
It scores, filters and schedules attractions using transparent rules
that a student can explain in an interview.
"""

from copy import deepcopy

import pandas as pd

from travel_data import DESTINATIONS, SUPPORTED_DESTINATIONS, resolve_destination

# How many time slots to fill per travel pace.
PACE_SLOTS = {
    "Relaxed": ["Morning", "Evening"],
    "Balanced": ["Morning", "Afternoon", "Evening"],
    "Packed": ["Morning", "Afternoon", "Evening"],
}

# Maximum attraction cost kept for each budget band (INR, per person-ish).
BUDGET_COST_CAP = {
    "Low": 500,
    "Medium": 1200,
    "High": 10_000,
}

# Multiplier applied to printed estimates (transport + meals style).
BUDGET_MULTIPLIER = {
    "Low": 0.85,
    "Medium": 1.0,
    "High": 1.35,
}

SLOT_EMOJI = {
    "Morning": "🌅",
    "Afternoon": "🍴",
    "Evening": "🌆",
}


def filter_attractions(destination, interests, budget, travel_type, min_needed=6):
    """
    Keep attractions that fit destination, interests, budget and group type.

    Steps:
    1. Load the destination catalogue into a pandas DataFrame.
    2. Drop activities that are a poor match for the travel type
       (for example, heavy nightlife for a family trip).
    3. Prefer activities whose category is in the user's interest list.
    4. Soft-filter by budget cap, then widen the pool if too few remain.
    """
    city = DESTINATIONS[destination]
    frame = pd.DataFrame(city["attractions"])

    # Travel-type rule: keep rows that list this group type.
    type_mask = frame["suitable_types"].apply(lambda types: travel_type in types)
    typed = frame[type_mask].copy()
    if typed.empty:
        typed = frame.copy()

    interest_set = set(interests or [])
    typed["interest_match"] = typed["category"].isin(interest_set) if interest_set else True

    cap = BUDGET_COST_CAP.get(budget, BUDGET_COST_CAP["Medium"])
    affordable = typed[typed["estimated_cost"] <= cap].copy()

    # Widen gradually so a 7-day packed trip still has unique places.
    if len(affordable) >= min_needed:
        pool = affordable
    elif len(typed) >= min_needed:
        pool = typed
    else:
        extra = frame.copy()
        extra["interest_match"] = extra["category"].isin(interest_set) if interest_set else True
        if travel_type == "Family":
            extra = extra[extra["category"] != "Nightlife"]
        pool = extra if not extra.empty else typed

    # Low budget: cheapest first among matches. High budget: allow premium picks.
    pool = pool.sort_values(
        by=["interest_match", "estimated_cost"],
        ascending=[False, budget == "Low"],
    )
    return pool.reset_index(drop=True)


def _score_row(row, interests, budget, travel_pace, slot):
    """Give a simple numeric score used when picking the next activity."""
    score = 0
    if row["category"] in (interests or []):
        score += 4
    if row["best_time"] == slot:
        score += 3
    if budget == "Low" and row["estimated_cost"] <= 300:
        score += 2
    if budget == "High" and row["estimated_cost"] >= 400:
        score += 1
    if travel_pace == "Relaxed" and row["duration_hours"] <= 2.5:
        score += 2
    if travel_pace == "Packed" and row["duration_hours"] <= 2.0:
        score += 2
    if travel_pace == "Packed" and row["duration_hours"] >= 4.0:
        score -= 2
    return score


def assign_activities_to_days(pool, num_days, travel_pace, interests, budget):
    """
    Spread unique attractions across days and time slots.

    Never repeats the same attraction. If the catalogue runs short,
    a light local filler is added so the day still feels complete.
    """
    slots = PACE_SLOTS.get(travel_pace, PACE_SLOTS["Balanced"])
    remaining = pool.to_dict("records")
    days = []

    for day_number in range(1, num_days + 1):
        day_plan = {"day": day_number, "slots": []}
        used_categories_today = []

        for slot in slots:
            pick = _pick_for_slot(
                remaining, slot, interests, budget, travel_pace, used_categories_today
            )
            if pick is None:
                pick = _filler_activity(slot, interests, day_number)
            else:
                remaining = [row for row in remaining if row["name"] != pick["name"]]
                used_categories_today.append(pick["category"])

            activity = deepcopy(pick)
            activity["slot"] = slot
            activity["emoji"] = SLOT_EMOJI.get(slot, "📍")
            day_plan["slots"].append(activity)

        days.append(day_plan)

    return days


def _pick_for_slot(remaining, slot, interests, budget, travel_pace, used_categories_today):
    """Choose the highest-scoring unused attraction for a time of day."""
    if not remaining:
        return None

    ranked = []
    for row in remaining:
        score = _score_row(row, interests, budget, travel_pace, slot)
        # Light variety rule: avoid the same category twice in one day when possible.
        if row["category"] in used_categories_today:
            score -= 2
        ranked.append((score, row))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[0][1]


def _filler_activity(slot, interests, day_number):
    """Generic local experience used only when named attractions run out."""
    choices = interests or ["Culture"]
    interest = choices[(day_number - 1) % len(choices)]
    templates = {
        "Morning": {
            "name": f"Local breakfast trail (day {day_number})",
            "category": interest if interest in ("Food", "Culture", "Relaxation") else "Food",
            "estimated_cost": 200,
            "duration_hours": 1.5,
            "best_time": "Morning",
            "note": "A flexible buffer so the morning is never empty.",
        },
        "Afternoon": {
            "name": f"Cafe or park free time (day {day_number})",
            "category": "Relaxation",
            "estimated_cost": 250,
            "duration_hours": 1.5,
            "best_time": "Afternoon",
            "note": "Built-in rest window — useful on longer trips.",
        },
        "Evening": {
            "name": f"Sunset walk or night market (day {day_number})",
            "category": interest if interest in ("Food", "Nightlife", "Shopping") else "Food",
            "estimated_cost": 300,
            "duration_hours": 1.5,
            "best_time": "Evening",
            "note": "Easy evening plan that fits most cities.",
        },
    }
    filler = deepcopy(templates.get(slot, templates["Afternoon"]))
    filler["suitable_types"] = ["Solo", "Couple", "Family", "Friends"]
    return filler


def calculate_budget(days, budget_level):
    """
    Apply the budget multiplier and return daily + trip totals.

    Low budget slightly reduces printed costs (public transport, simple meals).
    High budget increases them (cabs, nicer restaurants).
    """
    multiplier = BUDGET_MULTIPLIER.get(budget_level, 1.0)
    daily_totals = []
    grand_total = 0

    for day in days:
        raw = sum(slot["estimated_cost"] for slot in day["slots"])
        adjusted = int(round(raw * multiplier))
        day["estimated_cost"] = adjusted
        for slot in day["slots"]:
            slot["display_cost"] = int(round(slot["estimated_cost"] * multiplier))
        daily_totals.append(adjusted)
        grand_total += adjusted

    average = int(round(grand_total / len(days))) if days else 0
    return {
        "daily_totals": daily_totals,
        "grand_total": grand_total,
        "average_daily": average,
        "multiplier": multiplier,
    }


def get_travel_tips(destination, num_days, budget, travel_type, travel_pace, city_meta):
    """Build a short list of practical tips from simple if/else rules."""
    tips = [
        "Start popular sights early to avoid crowds and afternoon heat.",
        "Keep 10–15% of your budget as an emergency buffer for tickets, snacks or rain.",
    ]

    if budget == "Low":
        tips.append("Use metro, local buses or shared autos and choose thali / street-food meals.")
        tips.append("Book government museums and gardens first — they are often the best value.")
    elif budget == "Medium":
        tips.append("Mix one paid highlight each day with free walks, temples and viewpoints.")
    else:
        tips.append("A private cab for half-day clusters saves time on a high-budget trip.")

    if travel_type == "Family":
        tips.append("For family travel, keep transfers short and add a rest slot after lunch.")
        tips.append("Carry snacks, a light first-aid pouch and confirm child ticket rules.")
    elif travel_type == "Solo":
        tips.append("Share your daily plan with someone at home and prefer busy, well-lit areas at night.")
    elif travel_type == "Couple":
        tips.append("Save one sunset viewpoint or cafe evening with no packed schedule.")
    elif travel_type == "Friends":
        tips.append("Agree on a daily spend cap before nightlife or adventure add-ons.")

    if travel_pace == "Relaxed":
        tips.append("Two solid activities a day is enough — leave room to wander.")
    elif travel_pace == "Packed":
        tips.append("Group nearby attractions on the same day so you are not crossing the city twice.")

    if num_days <= 2:
        tips.append("With only a couple of days, pick one neighbourhood cluster instead of city-wide hopping.")
    elif num_days >= 5:
        tips.append("On a longer stay, keep one half-day completely unplanned.")

    if city_meta.get("is_hill_station"):
        tips.append(f"{destination} is a hill station — pack warm layers and start mountain roads early.")
    if city_meta.get("is_beach"):
        tips.append("Carry sunscreen, a hat and extra water; schedule indoor time at peak noon heat.")
    if city_meta.get("weather_note"):
        tips.append(city_meta["weather_note"])

    # Keep the list short enough to read in a demo.
    return tips[:8]


def get_packing_checklist(destination, travel_type, interests, city_meta):
    """Return a destination-aware packing list."""
    items = [
        "Government-issued photo ID",
        "Comfortable walking shoes",
        "Reusable water bottle",
        "Power bank and charger",
        "Phone with offline maps downloaded",
        "Basic medicines and a small first-aid kit",
        "Weather-appropriate clothing",
    ]

    if city_meta.get("is_hill_station"):
        items.extend(["Warm jacket or fleece", "Light rain jacket", "Moisturiser / lip balm"])
    elif city_meta.get("is_beach"):
        items.extend(["Sunscreen and sunglasses", "Hat / cap", "Quick-dry extra clothes"])
    else:
        items.append("Light cotton outfits for daytime heat")

    if "Adventure" in (interests or []):
        items.append("Sport sandals or extra grip shoes")
    if "Nightlife" in (interests or []):
        items.append("One smart-casual outfit")
    if travel_type == "Family":
        items.extend(["Snacks for children", "Photocopies of IDs"])
    if travel_type == "Solo":
        items.append("A small lock and a photocopy of your hotel address")

    items.append(f"Any booking printouts or QR tickets for {destination}")
    # Preserve order while removing duplicates.
    seen = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


def itinerary_as_text(result):
    """Plain-text export used by the download button in the UI."""
    lines = [
        f"AI Travel Itinerary — {result['destination']} ({result['num_days']} days)",
        result["tagline"],
        f"Budget band: {result['budget']} | Travel type: {result['travel_type']} | Pace: {result['travel_pace']}",
        f"Interests: {', '.join(result['interests']) or 'mixed'}",
        "",
    ]
    for day in result["days"]:
        lines.append(f"DAY {day['day']}")
        lines.append("━━━━━━━━━━━━━━━━")
        for slot in day["slots"]:
            hours = slot.get("duration_hours", 1)
            hour_label = "hour" if hours == 1 else "hours"
            cost = slot.get("display_cost", slot["estimated_cost"])
            lines.append(f"{slot['emoji']} {slot['slot']}")
            lines.append(slot["name"])
            lines.append(f"Duration: {hours:g} {hour_label}")
            lines.append(f"Estimated Cost: ₹{int(cost):,}")
            lines.append("")
        lines.append(f"💰 Day {day['day']} Estimated Cost: ₹{int(day['estimated_cost']):,}")
        lines.append("")
    lines.append(f"Total estimated cost: ₹{int(result['grand_total']):,}")
    lines.append(f"Number of places: {result['place_count']}")
    lines.append(f"Approximate daily budget: ₹{int(result['average_daily']):,}")
    return "\n".join(lines)


def generate_itinerary(destination_input, num_days, budget, travel_type, interests, travel_pace):
    """
    Main entry point used by the Streamlit app.

    Returns a dictionary the UI can render, or an error payload
    when the destination is not in the catalogue.
    """
    official = resolve_destination(destination_input)
    if official is None:
        listed = ", ".join(SUPPORTED_DESTINATIONS[:-1]) + " or " + SUPPORTED_DESTINATIONS[-1]
        return {
            "ok": False,
            "error": (
                "Currently, this destination is not in our recommendation database. "
                f"Try {listed}."
            ),
        }

    num_days = int(num_days)
    num_days = max(1, min(7, num_days))
    interests = list(interests or [])
    city_meta = DESTINATIONS[official]

    slots_per_day = len(PACE_SLOTS.get(travel_pace, PACE_SLOTS["Balanced"]))
    pool = filter_attractions(
        official,
        interests,
        budget,
        travel_type,
        min_needed=num_days * slots_per_day,
    )
    days = assign_activities_to_days(pool, num_days, travel_pace, interests, budget)
    money = calculate_budget(days, budget)

    all_places = [slot["name"] for day in days for slot in day["slots"]]
    covered = sorted({slot["category"] for day in days for slot in day["slots"]})

    return {
        "ok": True,
        "destination": official,
        "state": city_meta["state"],
        "tagline": city_meta["tagline"],
        "num_days": num_days,
        "budget": budget,
        "travel_type": travel_type,
        "interests": interests,
        "travel_pace": travel_pace,
        "days": days,
        "grand_total": money["grand_total"],
        "average_daily": money["average_daily"],
        "place_count": len(all_places),
        "unique_place_count": len(set(all_places)),
        "interests_covered": covered,
        "tips": get_travel_tips(official, num_days, budget, travel_type, travel_pace, city_meta),
        "packing": get_packing_checklist(official, travel_type, interests, city_meta),
    }
