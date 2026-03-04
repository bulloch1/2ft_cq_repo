import streamlit as st

st.set_page_config(initial_sidebar_state="collapsed")



st.title("Download Successful!")
st.divider()
st.space("medium")

left, right = st.columns(2, gap = "large")

left.header("Printing Your Leg - Next Steps:")
left.space("small")
left.subheader("Slicer")
left.markdown("we recommend Cura (link)")
left.space("small")
left.subheader("Settings")
left.markdown("print the foot upright, with __% infill and __ wall thickness. ___ layer height is recommended")
left.space("small")
left.header("Wearing Your New Leg")
left.markdown("Simply slide the leg tightly onto your pyramid adapter")

right.header("Estimated Specs")
right.space("small")
right.markdown("weight: __kg")
right.markdown("material cost: $__ (for PLA at $20/kg)")
right.markdown("printing time: __hrs (on a ___ printer)")
right.markdown("estimated lifetime: not very long")
right.markdown("allowable weight: lots of kilos")
right.markdown("other cool facts: None")


if st.button("Back to Home Page"):
    st.switch_page("2ft_app.py")
