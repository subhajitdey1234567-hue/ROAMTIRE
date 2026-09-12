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

# Custom CSS for modern responsive mobile & desktop UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF8F00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #6c757d;
        margin-bottom: 20px;
    }
    .price-card {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07);
        margin-bottom: 15px;
        min-height: 290px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .tier-title {
        font-weight: 700;
        font-size: 1.15rem;
        color: #1e293b;
        text-align: center;
    }
    .tier-price {
        font-size: 1.8rem;
        font-weight: 800;
        color: #10b981;
        margin: 6px 0 2px 0;
        text-align: center;
    }
    .per-person-text {
        color: #64748b;
        font-size: 0.85rem;
        text-align: center;
        margin-bottom: 8px;
    }
    .breakdown-box {
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.55;
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 10px;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# PREDICTIVE PRICE ENGINE & ITINERARY DATABASE
# ==========================================

DESTINATION_DATABASE = {
    "kashmir": {"type": "valley_mountain", "tier_multiplier": 1.35, "cab_daily": 3200},
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
    "3_star": {"base": 3200, "label": "3-Star (Standard)", "stay_type": "Rated Boutique Hotels", "transit": "Dedicated Private Sedan"},
    "4_star": {"base": 6500, "label": "4-Star (Premium)", "stay_type": "Premium Resorts", "transit": "Private SUV & Airport Transfers"}
}

DAILY_FOOD_ACTIVITY_COST = {
    "2_star": 700,
    "3_star": 1400,
    "4_star": 2800
}

ITINERARY_TEMPLATES = {
    "kashmir": {
        "highlights": [
            ("Morning", "Shikara Ride on Dal Lake & Boulevard Road", 800),
            ("Afternoon", "Mughal Gardens (Nishat & Shalimar Bagh)", 150),
            ("Evening", "Lal Chowk Walking Tour & Kashmiri Craft Center", 200)
        ],
        "balanced": [
            ("Morning", "Gulmarg Gondola Phase 1 & Meadow Trail", 1450),
            ("Afternoon", "Pahalgam Betaab Valley & Aru Valley Excursion", 850),
            ("Evening", "Local Wazwan Dining Experience", 900)
        ],
        "relaxed": [
            ("Morning", "Doodhpathri (Valley of Milk) Nature Walk", 400),
            ("Afternoon", "Pari Mahal Historic Sunset Overlook", 100),
            ("Evening", "Traditional Saffron Kahwa Tea Session", 250)
        ]
    },
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


def calculate_price_predictions(dest_key, days, travelers, season):
    dest_info = DESTINATION_DATABASE.get(dest_key, DESTINATION_DATABASE["default"])
    multiplier = dest_info["tier_multiplier"]
    cab_daily = dest_info["cab_daily"]

    season_multipliers = {
        "Peak Season (High)": 1.20,
        "Regular Season": 1.00,
        "Monsoon / Off-Peak": 0.85
    }
    season_factor = season_multipliers.get(season, 1.0)
    multiplier *= season_factor

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
            for time, name, cost in opt["source"]:
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

st.markdown('<p class="main-header">🗺️ RoamTier AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Intelligent Travel Price Prediction & Dynamic Itinerary Planner</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Trip Parameters")
    
    dest_input = st.text_input("Destination", value="Kashmir", placeholder="e.g., Kashmir, Puri, Meghalaya, Goa").strip()
    duration_input = st.number_input("Duration (Days)", min_value=1, max_value=14, value=6)
    travelers_input = st.number_input("Travelers Count", min_value=1, max_value=20, value=3)
    travel_season = st.selectbox("Travel Season", ["Peak Season (High)", "Regular Season", "Monsoon / Off-Peak"])
    
    calc_btn = st.button("🚀 Estimate Prices & Generate Plans", type="primary", use_container_width=True)

clean_key = dest_input.lower()
matched_key = "default"
for candidate in DESTINATION_DATABASE:
    if candidate in clean_key:
        matched_key = candidate
        break

if calc_btn or "predictions" not in st.session_state:
    st.session_state["predictions"] = calculate_price_predictions(matched_key, duration_input, travelers_input, travel_season)
    st.session_state["itineraries"] = generate_itineraries(matched_key, duration_input)
    st.session_state["current_dest"] = dest_input.title()
    st.session_state["days"] = duration_input
    st.session_state["travelers"] = travelers_input

preds = st.session_state["predictions"]
itineraries = st.session_state["itineraries"]
curr_dest = st.session_state["current_dest"]
days = st.session_state["days"]
travelers = st.session_state["travelers"]

# ==========================================
# SECTION 1: PRICE PREDICTIONS
# ==========================================
st.subheader(f"📊 Price Predictions for {curr_dest} ({days} Days, {travelers} Traveler{'s' if travelers > 1 else ''})")

col1, col2, col3 = st.columns(3)
tiers_data = [("2_star", col1, "🥉"), ("3_star", col2, "🥈"), ("4_star", col3, "🥇")]

for star_key, col, badge in tiers_data:
    data = preds[star_key]
    with col:
        st.markdown(f"""
        <div class="price-card">
            <div>
                <div class="tier-title">{badge} {data['label']}</div>
                <div class="tier-price">₹{data['total_cost']:,}</div>
                <div class="per-person-text">₹{data['per_person']:,} / person</div>
            </div>
            <div class="breakdown-box">
                🏨 <b>Stay:</b> {data['stay_type']}<br>
                🚗 <b>Transit:</b> {data['transit']}<br>
                💰 <b>Accommodation:</b> ₹{data['breakdown']['Accommodation']:,}<br>
                🚕 <b>Transport:</b> ₹{data['breakdown']['Transport']:,}<br>
                🎟️ <b>Food & Passes:</b> ₹{data['breakdown']['Food & Sightseeing']:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# SECTION 2: CLEAN STACKED BAR CHART (FIXED GLITCH)
# ==========================================
st.markdown("#### 📊 Price Component Comparison across Tiers (INR)")

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
    height=400,
    margin=dict(l=10, r=10, t=10, b=50),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.18,
        xanchor="center",
        x=0.5,
        font=dict(size=12)
    ),
    xaxis=dict(tickfont=dict(size=12)),
    yaxis=dict(title="Amount (₹)", tickformat=","),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# SECTION 3: ITINERARY CHOICES
# ==========================================
st.markdown("---")
st.subheader("🗓️ Select Your Itinerary Plan Choice")

tab1, tab2, tab3 = st.tabs([
    itineraries[0]["title"],
    itineraries[1]["title"],
    itineraries[2]["title"]
])

for idx, tab in enumerate([tab1, tab2, tab3]):
    plan = itineraries[idx]
    with tab:
        st.info(f"**Vibe:** {plan['vibe']}")
        for day_item in plan["schedule"]:
            with st.expander(f"📌 Day {day_item['day']}: Tour Schedule", expanded=True):
                for act in day_item["activities"]:
                    st.write(f"- **{act['time']}**: {act['activity']} *(Est. Fee: ₹{act['cost']}/person)*")

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
