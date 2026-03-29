import streamlit as st

pi = 3.141592

weight = st.session_state.weight
height = st.session_state.height
foot_length = st.session_state.foot_length
foot_width = st.session_state.foot_width
right = st.session_state.right
heel_radius = st.session_state.pylon_radius
ankle_height = st.session_state.ankle_height
toe_height = st.session_state.toe_height
pylon_offset = st.session_state.pylon_offset
pylon_radius = st.session_state.pylon_radius
pylon_height = st.session_state.pylon_height
toe_length = st.session_state.toe_length

t_w = 3 #mm
cost_per_kg_pla = 20
density_pla = 0.0013 #g/mm^3

suggested_infill = (weight / 3.0) / 100.0
estimated_volume_shell = t_w*(2*pylon_radius*(pi*pylon_height+5*ankle_height-foot_length-2*foot_width) #mm^3
estimated_volume_infill = suggested_infill * ((pylon_height*pi*pylon_radius**2 + 2*pylon_radius*ankle_height*foot_width + 0.5*(foot_length-2*pylon_radius)*ankle_height*foot_width) - estimated_volume_shell)
estimated_volume = estimated_volume_shell + estimated_volume_infill #mm^3
estimated_mass = estimated_volume * density_pla #g
estimated_cost = (estimated_mass / 1000) * cost_per_kg_pla #dollars
estimated_savings_dollars = 5000 - estimated_cost
estimated_savings_percent = estimated_savings_dollars / 5000

              
st.set_page_config(initial_sidebar_state="collapsed")

st.title("Download Successful!", text_alignment = "center")
st.divider()
st.space("medium")

left, right = st.columns(2, gap = "large", border = True)

left.header("Printing Your Leg - Next Steps:")
left.space("small")
left.subheader("Slicer")
left.markdown("we recommend Cura")
left.space("small")
left.subheader("Settings")
left.markdown("print the foot upright, with " + suggested_infill + "% infill and " + t_w + "mm wall thickness. 0.3mm layer height is recommended")
left.space("small")
left.header("Wearing Your New Leg")
left.markdown("Simply slide the leg tightly onto your pyramid adapter")

right.header("Estimated Specs")
right.space("small")
right.markdown("Weight: " + (estimated_mass / 1000) + "kg")
right.markdown("Material cost: $" + estimated_cost + " (for PLA at $20/kg)")
right.markdown("Average cost of a below-knee prosthesis: $5,000")
right.markdown("That means you're saving $" + estimated_savings_dollars +  " (" + estimated_savings_percent + "%)")


if st.button("Back to Home Page"):
    st.switch_page("2ft_app.py")
