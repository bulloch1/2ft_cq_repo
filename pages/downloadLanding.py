import streamlit as st

# 1. Page Config MUST be first
st.set_page_config(initial_sidebar_state="collapsed")

# 2. Add safety checks for session state (in case user refreshes)
if "weight_copy" not in st.session_state:
    st.error("Please go back and enter your measurements first.")
    st.stop()

pi = 3.141592

# Pulling from session state
weight = st.session_state.weight_copy
pylon_radius = st.session_state.pylon_radius_copy
pylon_height = st.session_state.pylon_height_copy
ankle_height = st.session_state.ankle_height_copy
foot_length = st.session_state.foot_length_copy
foot_width = st.session_state.foot_width_copy

t_w = 3 #mm
cost_per_kg_pla = 20
density_pla = 0.0013 #g/mm^3

# Logic Fixes: Use f-strings or str() for display, and fix parentheses
suggested_infill = (weight / 3.0) 
# Fixed missing closing parenthesis below
estimated_volume_shell = t_w * (2 * pylon_radius * (pi * pylon_height + 5 * ankle_height - foot_length - 2 * foot_width)) 

estimated_volume_infill = (suggested_infill / 100.0) * ((pylon_height * pi * pylon_radius**2 + 2 * pylon_radius * ankle_height * foot_width + 0.5 * (foot_length - 2 * pylon_radius) * ankle_height * foot_width) - estimated_volume_shell)

estimated_volume = estimated_volume_shell + estimated_volume_infill #mm^3
estimated_mass = estimated_volume * density_pla #g
estimated_cost = (estimated_mass / 1000) * cost_per_kg_pla #dollars
estimated_savings_dollars = 5000 - estimated_cost
estimated_savings_percent = (estimated_savings_dollars / 5000) * 100

st.title("Download Successful!")
st.divider()

left, right_col = st.columns(2, gap="large", border=True) # Renamed 'right' to 'right_col' to avoid conflict with foot side

with left:
    st.header("Printing Your Leg")
    st.subheader("Slicer")
    st.markdown("We recommend **Cura**.")
    st.page_link("https://curaslicer.com/#download-cura-slicer", label="Download Cura", icon="external-link")
    st.subheader("Settings")
    # Using f-strings to prevent TypeErrors
    st.markdown(f"Print the foot upright, with **{suggested_infill:.1f}%** infill and **{t_w}mm** wall thickness.")
    st.markdown("0.3mm layer height is recommended.")
    st.header("Wearing Your New Leg")
    st.markdown("Simply slide the leg tightly onto your pyramid adapter.")

with right_col:
    st.header("Estimated Specs")
    st.markdown(f"**Mass:** {(estimated_mass / 1000):.2f} kg")
    st.markdown(f"**Material cost:** ${estimated_cost:.2f} (PLA)")
    st.markdown("**Average cost of a transtibial prosthesis:** $5,000")
    st.success(f"**Estimated savings:** ${estimated_savings_dollars:,.2f} ({estimated_savings_percent:.1f}%)")

if st.button("Back to Home Page"):
    st.switch_page("2ft_app.py")
