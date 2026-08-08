import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="RoamTier AI | Smart Travel Price Predictor",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Enlarged Logo & Dark Theme Hero Banner
st.markdown("""
<style>
    /* Hero Banner Container */
    .hero-container {
        background: linear-gradient(135deg, #1e1e2f 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    .hero-title-wrapper {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    /* Enlarged Badge Logo Icon */
    .hero-logo {
        font-size: 3.5rem;
        background: linear-gradient(135deg, #ff4b4b 0%, #ff8f00 100%);
        padding: 12px 20px;
        border-radius: 18px;
        display: inline-block;
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4);
        line-height: 1;
    }

    /* Main Brand Header */
    .main-header {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #ff4b4b, #ff8f00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 !important;
        line-height: 1.1 !important;
        letter-spacing: -0.5px;
    }

    /* Subtitle Styling */
    .sub-header {
        font-size: 1.25rem !important;
        color: #94a3b8 !important;
        margin-top: 6px !important;
        margin-bottom: 0px !important;
        font-weight: 400;
    }

    /* Price Card Styling */
    .price-card {
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 22px;
        background-color: #1e293b;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .tier-title {
        font-weight: 700;
        font-size: 1.3rem;
        color: #f8fafc;
    }
    .tier-price {
        font-size: 2.1rem;
        font-weight: 800;
        color: #4ade80;
        margin: 8px 0;
    }
    .breakdown-text {
        font-size: 0.92rem;
        color: #cbd5e1;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# PREDICTIVE PRICE ENGINE & ITINERARY DATA
# ==========================================

DESTINATION_DATABASE = {
    "puri": {"type": "coastal_spiritual", "tier_multiplier": 1.0, "cab_daily": 2200},
    "meghalaya": {"type": "hill_nature", "tier_multiplier": 1.25, "cab_daily": 3500},
    "goa": {"type": "coastal_beach", "tier_multiplier": 1.35, "cab_daily": 2800},
    "manali": {"type": "mountain_adventure", "tier_multiplier": 1.3, "cab_daily": 3200},
    "kerala": {"type": "backwaters_nature", "tier_multiplier": 1.2, "cab_daily": 2600},
    "rajasthan": {"type": "heritage_culture", "tier_multiplier": 1.15, "cab_daily": 2500},
    "darjeeling": {"type": "hill_nature", "tier_multiplier": 1.1, "cab_daily": 2800},
    "default": {"type": "standard_tourism", "tier_multiplier": 1.1, "cab_daily": 2500}
}

STAR_RATES_PER_NIGHT = {
    "2_star": {"base": 1400, "label": "2-Star (Budget)", "stay_type": "Guesthouses & Budget Hotels", "transit": "Shared Cabs / Autos"},
    "3_star": {"base": 3200, "label": "3-Star (Standard)", "stay_type": "3-Star Rated Boutique Hotels", "transit": "Dedicated Private Sedan"},
    "4_star": {"base": 6500, "label": "4-Star (Premium)", "stay_type": "4-Star Premium Resorts", "transit": "Private SUV & Airport Transfers"}
}

DAILY_FOOD_ACTIVITY_COST = {
    "2_star": 700,
    "3_star": 1400,
    "4_star": 2800
}

ITINERARY_TEMPLATES = {
    "puri": {
        "highlights": [
            ("Morning", "Jagannath Temple Darshan & Anand Bazar", 100),
            ("Afternoon", "Golden Beach Relax & Stroll", 0),
            ("Evening", "Light & Sound Show at Konark Sun Temple", 350)
        ],
        "balanced": [
            ("Morning", "Raghurajpur Heritage Craft Village Visit", 200),
            ("Afternoon", "Chilika Lake Boat Safari (Satapada Dolphin Watching)", 1200),
            ("Evening", "Local Sea Market & Beachside Dining", 500)
        ],
        "relaxed": [
            ("Morning", "Private Yoga & Sunrise Walk at Swargadwar Beach", 300),
            ("Afternoon", "Sudarshan Crafts Museum & Local Culinary Tour", 400),
            ("Evening", "Relaxed Sunset Cruise on Mangalajodi Backwaters", 800)
        ]
    },
    "meghalaya": {
        "highlights": [
            ("Morning", "Umiam Lake Viewpoint & Elephant Falls", 150),
            ("Afternoon", "Cherrapunji Seven Sisters Falls & Mawsmai Cave", 250),
            ("Evening", "Police Bazar Shillong Shopping & Cafe hopping", 400)
        ],
        "balanced": [
            ("Morning", "Nongriat Double Decker Living Root Bridge Trek", 300),
            ("Afternoon", "Wei Sawdong Three-Tiered Waterfall Hike", 100),
            ("Evening", "Bonfire & Local Khasi Music Night", 600)
        ],
        "relaxed": [
            ("Morning", "Dawki Umngot River Boating (Crystal Clear Water)", 800),
            ("Afternoon", "Mawlynnong Cleanest Village Walk & Bamboo Sky Walk", 200),
            ("Evening", "Shillong Peak Sunset Viewpoint", 150)
        ]
    },
    "default": {
        "highlights": [
            ("Morning", "Top City Landmark & Historical Sightseeing", 200),
            ("Afternoon", "Central Museum & Cultural Hub Visit", 300),
            ("Evening", "Popular Local Market & Food Walk", 500)
        ],
        "balanced": [
            ("Morning", "Guided Nature Walk & Viewpoint Hike", 250),
            ("Afternoon", "Traditional Crafts Village & Artisan Center", 150),
            ("Evening", "Scenic Sunset Point & Fine Dining", 800)
        ],
        "relaxed": [
            ("Morning", "Leisurely Breakfast & Botanical Garden Walk", 100),
            ("Afternoon", "Local Heritage Museum & Art Gallery", 200),
            ("Evening", "River/Lake Boating & Relaxation", 600)
        ]
    }
}


def calculate_price_predictions(dest_key, days, travelers, season_multiplier=1.0):
    """Predicts pricing breakdown for 2-star, 3-star, and 4-star tiers."""
    dest_info = DESTINATION_DATABASE.get(dest_key, DESTINATION_DATABASE["default"])
    multiplier = dest_info["tier_multiplier"] * season_multiplier
    cab_daily = dest_info["cab_daily"] * season_multiplier

    rooms_needed = max(1, (travelers + 1) // 2)
    predictions = {}
    
    for star_key, star_data in STAR_RATES_PER_NIGHT.items():
        hotel_nightly = star_data["base"] * multiplier
        total_hotel = hotel_nightly * (days - 1 if days > 1 else 1) * rooms_needed

        if star_key == "2_star":
            total_transport = (cab_daily * 0.4) * days * travelers
        elif star_key == "3_star":
            total_transport = cab_daily * days
        else:
            total_transport = (cab_daily * 1.6) * days

        food_per_person_day = DAILY_FOOD_ACTIVITY_COST[star_key] * multiplier
        total_food_activities = food_per_person_day * days * travelers

        total_cost = total_hotel + total_transport + total_food_activities

        predictions[star_key] = {
            "label": star_data["label"],
            "stay_type": star_data["stay_type"],
            "transit": star_data["transit"],
            "total_cost": round(total_cost),
            "per_person": round(total_cost / travelers),
            "breakdown": {
                "Accommodation": round(total_hotel),
                "Transport": round(total_transport),
                "Food & Sightseeing": round(total_food_activities)
            }
        }
    return predictions


def generate_itineraries(dest_key, days):
    """Generates 3 customized itineraries (Express, Balanced, Immersive)."""
    dest_data = ITINERARY_TEMPLATES.get(dest_key, ITINERARY_TEMPLATES["default"])
    
    options = [
        {"id": "express", "title": "⚡ Option 1: Express Highlights", "vibe": "Fast-paced, iconic landmarks, maximum coverage", "source": dest_data["highlights"]},
        {"id": "balanced", "title": "⚖️ Option 2: Cultural & Balanced", "vibe": "Medium-paced, local authentic experiences", "source": dest_data["balanced"]},
        {"id": "relaxed", "title": "🌿 Option 3: Scenic Immersion", "vibe": "Relaxed pace, nature trails, offbeat hidden spots", "source": dest_data["relaxed"]}
    ]

    generated = []
    for opt in options:
        days_plan = []
        for d in range(1, days + 1):
            day_activities = []
            for slot, (time, name, cost) in enumerate(opt["source"]):
                adj_cost = cost + ((d - 1) * 20)
                day_activities.append({
                    "time": time,
                    "activity": f"{name} (Day {d} sequence)" if d > 1 else name,
                    "cost": adj_cost
                })
            days_plan.append({"day": d, "activities": day_activities})
        
        generated.append({
            "title": opt["title"],
            "vibe": opt["vibe"],
            "schedule": days_plan
        })

    return generated


# ==========================================
# STREAMLIT USER INTERFACE
# ==========================================

# Header Hero Section with Enlarged Logo
st.markdown("""
<div class="hero-container">
    <div class="hero-title-wrapper">
        <div class="hero-logo">🗺️</div>
        <div>
            <h1 class="main-header">RoamTier AI</h1>
            <p class="sub-header">Intelligent Travel Price Prediction & Dynamic Itinerary Planner</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Inputs
with st.sidebar:
    st.header("⚙️ Trip Parameters")
    
    dest_input = st.text_input("Destination", value="Puri", placeholder="e.g., Puri, Meghalaya, Goa").strip()
    duration_input = st.number_input("Duration (Days)", min_value=1, max_value=14, value=3)
    travelers_input = st.number_input("Travelers Count", min_value=1, max_value=20, value=2)
    
    travel_season = st.selectbox("Travel Season", ["Regular Season", "Peak Season (High)", "Monsoon / Off-Peak"])
    season_mult = 1.25 if "Peak" in travel_season else (0.85 if "Off-Peak" in travel_season else 1.0)

    calc_btn = st.button("🚀 Estimate Prices & Generate Plans", type="primary", use_container_width=True)

# Destination Key Lookup Processing
dest_key = dest_input.lower()
if dest_key not in DESTINATION_DATABASE:
    for key in DESTINATION_DATABASE.keys():
        if key in dest_key:
            dest_key = key
            break
    else:
        dest_key = "default"

# Calculation Trigger & Session State Setup
if calc_btn or "predictions" not in st.session_state:
    st.session_state["predictions"] = calculate_price_predictions(dest_key, duration_input, travelers_input, season_mult)
    st.session_state["itineraries"] = generate_itineraries(dest_key, duration_input)
    st.session_state["current_dest"] = dest_input.title() if dest_input else "Puri"
    st.session_state["days"] = duration_input
    st.session_state["travelers"] = travelers_input

preds = st.session_state["predictions"]
itineraries = st.session_state["itineraries"]
curr_dest = st.session_state["current_dest"]
days = st.session_state["days"]
travelers = st.session_state["travelers"]

# ==========================================
# DISPLAY SECTION 1: PRICE PREDICTIONS
# ==========================================
st.subheader(f"📊 Price Predictions for {curr_dest} ({days} Days, {travelers} Traveler{'s' if travelers > 1 else ''})")

col1, col2, col3 = st.columns(3)
tiers_data = [("2_star", col1, "🥉"), ("3_star", col2, "🥈"), ("4_star", col3, "🥇")]

for star_key, col, badge in tiers_data:
    data = preds[star_key]
    with col:
        st.markdown(f"""
        <div class="price-card">
            <div class="tier-title">{badge} {data['label']}</div>
            <div class="tier-price">₹{data['total_cost']:,}</div>
            <p style="margin-top:-10px; color:#94a3b8; font-size:0.85rem;">₹{data['per_person']:,} per person</p>
            <hr style="border-color: #334155; margin: 10px 0;">
            <div class="breakdown-text">
                🏨 <b>Stay:</b> {data['stay_type']}<br>
                🚗 <b>Transit:</b> {data['transit']}<br><br>
                💰 <b>Accommodation:</b> ₹{data['breakdown']['Accommodation']:,}<br>
                🚕 <b>Transport:</b> ₹{data['breakdown']['Transport']:,}<br>
                🎟️ <b>Food & Passes:</b> ₹{data['breakdown']['Food & Sightseeing']:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Plotly Component Breakdown Chart
chart_data = []
for k, v in preds.items():
    chart_data.append({
        "Tier": v["label"],
        "Accommodation": v["breakdown"]["Accommodation"],
        "Transport": v["breakdown"]["Transport"],
        "Food & Sightseeing": v["breakdown"]["Food & Sightseeing"]
    })

df_chart = pd.DataFrame(chart_data)

fig = go.Figure(data=[
    go.Bar(name='Accommodation', x=df_chart['Tier'], y=df_chart['Accommodation'], marker_color='#38bdf8'),
    go.Bar(name='Transport', x=df_chart['Tier'], y=df_chart['Transport'], marker_color='#facc15'),
    go.Bar(name='Food & Sightseeing', x=df_chart['Tier'], y=df_chart['Food & Sightseeing'], marker_color='#4ade80')
])
fig.update_layout(
    barmode='stack',
    title="Price Component Comparison across Tiers (INR)",
    height=360,
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# DISPLAY SECTION 2: THREE ITINERARY CHOICES
# ==========================================
st.markdown("---")
st.subheader("🗓️ Select Your Itinerary Plan Choice")

tab1, tab2, tab3 = st.tabs([
    itineraries[0]["title"],
    itineraries[1]["title"],
    itineraries[2]["title"]
])

tabs = [tab1, tab2, tab3]

for idx, tab in enumerate(tabs):
    plan = itineraries[idx]
    with tab:
        st.info(f"**Vibe:** {plan['vibe']}")
        
        for day_item in plan["schedule"]:
            with st.expander(f"📌 Day {day_item['day']}: Tour Schedule", expanded=True):
                for act in day_item["activities"]:
                    st.write(f"- **{act['time']}**: {act['activity']} *(Est. Fee: ₹{act['cost']}/person)*")

# JSON Export Option
st.markdown("---")
report_data = {
    "destination": curr_dest,
    "days": days,
    "travelers": travelers,
    "price_predictions": preds,
    "itineraries": itineraries
}

st.download_button(
    label="📥 Export Full Trip Estimation Report (JSON)",
    data=json.dumps(report_data, indent=2),
    file_name=f"{curr_dest.lower()}_travel_plan.json",
    mime="application/json"
)