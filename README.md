# AI Travel Itinerary Generator

A Python-based travel planning application that creates personalized day-by-day itineraries based on a traveller's destination, trip duration, budget, travel type, interests, and preferred pace.

The application uses a rule-based recommendation engine to select suitable attractions, organize activities into morning, afternoon, and evening schedules, and provide estimated costs, travel tips, and a destination-specific packing checklist.

Built with Python, Streamlit, and Pandas, the project demonstrates how user preferences can be combined with structured travel data to generate practical and personalized travel plans.

---

## Project description

Travellers enter a destination, trip length, budget, group type, interests and pace. The app filters a curated set of attractions, matches them to those preferences, and lays out morning, afternoon and evening plans with estimated costs, travel tips and a packing checklist.

It is designed to be easy to demo in an interview: change the sidebar inputs, click generate, and explain the rules behind the plan.

---

## Features

- Modern Streamlit dashboard
- Sidebar trip preferences (destination, days, budget, type, interests, pace)
- Rule-based recommendation engine in a separate module
- Day-by-day itinerary with morning / afternoon / evening slots
- Estimated daily cost and total trip cost
- Travel summary (places, interests covered, average daily spend)
- Smart tips that change with budget, group type, destination and duration
- Destination-aware packing checklist
- Download itinerary as a text file
- Friendly error message for cities not in the catalogue
- No paid APIs and no API keys

---

## Technologies used

| Layer | Choice |
| --- | --- |
| Language | Python 3 |
| UI | Streamlit |
| Tabular filtering | Pandas |
| Data | Local Python dictionaries (`travel_data.py`) |
| Intelligence | Rule-based scoring and scheduling |

---

## How it works

1. The user fills **Trip Preferences** in the sidebar and clicks **Generate My Itinerary**.
2. `app.py` sends those inputs to `generate_itinerary()` in `recommendation_engine.py`.
3. The engine resolves the city name (including aliases such as Bangalore → Bengaluru).
4. Attractions are filtered and scored against interests, budget and travel type.
5. Unique places are assigned to days and time-of-day slots according to travel pace.
6. Costs, tips and a packing list are calculated and rendered as cards in the UI.

---

## Rule-based recommendation logic

The engine is deterministic. Given the same inputs, it produces the same plan.

| Rule | What it does |
| --- | --- |
| Destination filter | Only attractions stored for that city are used |
| Interest match | Categories such as Food, History or Nature are preferred when selected |
| Budget cap | Low budget drops expensive tickets; High budget allows premium activities |
| Cost multiplier | Low slightly reduces printed costs; High increases them (cabs / nicer meals) |
| Travel type | Nightlife-heavy spots are skipped for Family plans when marked adult-only |
| Travel pace | Relaxed = 2 slots/day; Balanced & Packed = 3 slots/day (Packed prefers shorter stops) |
| No repeats | Each named attraction is used at most once |
| Time of day | Activities prefer their `best_time` (Morning / Afternoon / Evening) |
| Variety | The same category is slightly penalised if already used that day |
| Fallback | If the catalogue runs short, a generic local filler keeps the day complete |

---

## Project structure

```
travel-itinerary-generator/
├── app.py                      # Streamlit UI
├── recommendation_engine.py    # Rule-based planner
├── travel_data.py              # Destinations and attractions
├── requirements.txt
├── README.md
└── .gitignore
```

Supported destinations: **Bengaluru, Mysuru, Goa, Mumbai, Delhi, Jaipur, Hyderabad, Chennai, Kochi, Ooty, Manali, Munnar**.

---

## Installation

From the project folder ( **Terminal → New Terminal**):

```bash
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## How to run

```bash
streamlit run app.py
```

Streamlit prints a local URL (usually `http://localhost:8501`). Open it in the browser.

Demo path that photographs well:

1. Destination: `Bengaluru`
2. Days: `3`
3. Budget: `Medium`
4. Travel type: `Couple`
5. Interests: `Culture`, `Food`, `Nature`
6. Pace: `Balanced`
7. Click **✨ Generate My Itinerary**

To show error handling, type `Paris` (or any city not in the list) and generate again.

---

## Example output

For a 3-day Bengaluru trip you should see:

- Summary cards for destination, days, estimated budget and interests
- **DAY 1 / DAY 2 / DAY 3** cards with morning, afternoon and evening activities
- Per-day estimated cost and a trip total
- Smart tips (crowds, emergency buffer, couple-friendly sunset slot)
- A packing checklist (ID, shoes, water bottle, power bank, and so on)

Costs are **indicative estimates in INR**, not live ticket prices.

---

## Future enhancements

- Add more Indian and international cities to the catalogue
- Cluster attractions by neighbourhood to reduce travel time
- Optional weather-based clothing tips from a free public API
- Export the itinerary as PDF or CSV
- User accounts to save favourite plans
- Optional LLM rewrite of activity blurbs *on top of* the same rule-based schedule

---

