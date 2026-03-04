import streamlit as st
import cadquery as cq
from cadquery import exporters
import tempfile
import os
import traceback

def PageContents(): #collects and calculates all foot measurements
    #title page elements
    st.title("OpenGait", text_alignment = "center")
    st.caption("The world's first fully customizable, downloadable prosthetic leg", text_alignment = "center")
    st.divider()
    st.space("medium")
    
    #standard bounds in metric (mm, kg)
    foot_length_lb = 150
    foot_length_avg = 200
    if "foot_length" not in st.session_state:
        st.session_state.foot_length = foot_length_avg
    foot_length_ub = 300
    
    predicted_width_intercept = 17.3
    width_avg = int(0.32 * st.session_state.foot_length + predicted_width_intercept)
    width_lb = int(width_avg * 0.85)
    width_ub = int(width_avg * 1.4)
    
    height_lb = 150
    height_avg = 240
    height_ub = 400
    
    weight_lb = 20
    weight_avg = 70
    weight_ub = 100

    #conversion factors
    in_per_mm = 1/25.4
    lb_per_kg = 2.20462
    
    #VALUE PAGE ELEMENTS
    #length
    st.slider("Foot Length (mm)", foot_length_lb, foot_length_ub, key = "foot_length") # starting value not defined here because st.session_State.foot_length is already defined
    st.space("small")
    
    #height
    height_lb = int(st.session_state.foot_length*0.5) #height must be greater than ankle height (foot_length*0.4)
    st.slider("Limb Height (mm)", height_lb, height_ub, value = height_avg, key = "height")
    st.space("small")
    
    #width
    st.slider("Foot Width (mm)", width_lb, width_ub, value = width_avg, key = "foot_width")
    st.space("small")

    #weight
    st.slider("Weight (kg)", weight_lb, weight_ub, value = weight_avg, key = "weight")
    st.space("small")

    #sidebar
    st.sidebar.toggle("Use advanced measurements", value = False, key = "advanced_options")
    st.sidebar.toggle("Use metric units (mm, kg)", value = True, key = "metric")
    st.sidebar.divider()
    st.sidebar.title("Instructions")
    st.sidebar.subheader("Foot Length")
    st.sidebar.text("Measure the distance from the back of your heel to the tip of your big toe")
    st.sidebar.space("small")
    st.sidebar.subheader("Foot Width")
    st.sidebar.text("Measure the width of your foot directly across at the widest point")
    st.sidebar.space("small")
    st.sidebar.subheader("Limb Height")
    st.sidebar.text("Measure the distance from the plate of your pyramid adapter (at the base of your socket) to the ground")
    st.sidebar.space("small")

    #predicted secondary values
    avg_pr = st.session_state.foot_width * 0.3 #pylon radius #this value used to make the medial edge of the heel vertical (40% of foot wass medial, 60% was lateral)
    avg_ah = st.session_state.foot_length * 0.4 #ankle height
    avg_th = st.session_state.foot_length * 0.1 #toe height
    avg_po = avg_pr * 1.2 #pylon offset
    ub = 1.2 #upper bound coefficient
    lb = 0.8 #lower bound coeffcient
    
    #optional advanced settings
    if (st.session_state.advanced_options):
        st.subheader("Advanced Measurements")
        st.caption("Warning, changing these values may cause model to fail to build")
        st.slider("Ankle radius", avg_pr*lb, avg_pr*ub, value = avg_pr, key = "pylon_radius")
        st.slider("Ankle Height", avg_ah*lb, avg_ah*ub, value = avg_ah, key = "ankle_height")
        st.slider("Toe height", avg_th*lb, avg_th*ub, value = avg_th, key = "toe_height")
        st.slider("forward leg offset", avg_po*lb, avg_po*ub, value = avg_po, key = "pylon_offset")
    else:
        st.session_state.pylon_radius = avg_pr
        st.session_state.ankle_height = avg_ah
        st.session_state.toe_height = avg_th
        st.session_state.pylon_offset = avg_po
    
    #other user-defined variables
    side = st.radio("Which foot?", ("Left", "Right"))
    st.session_state.right = (side == "Right")
    st.space("small")

    #other calculated variables
    st.session_state.pylon_height = st.session_state.height - st.session_state.ankle_height
    st.session_state.toe_length = st.session_state.foot_length * 0.2

def GetShape():
    height = st.session_state.height
    foot_length = st.session_state.foot_length
    foot_width = st.session_state.foot_width
    weight = st.session_state.weight
    right = st.session_state.right
    heel_radius = st.session_state.pylon_radius
    ankle_height = st.session_state.ankle_height
    toe_height = st.session_state.toe_height
    pylon_offset = st.session_state.pylon_offset
    pylon_radius = st.session_state.pylon_radius
    pylon_height = st.session_state.pylon_height
    toe_length = st.session_state.toe_length
    # Start of CadQuery script
    
    #pyramid adapter
    tolerance = 0.12
    base_plate_thickness = 4.1
    ball_base_radius = 40.9/2 + tolerance #this tolerance may be different since its a curve
    ball_depth = 13.36 - base_plate_thickness + tolerance
    dove_depth = 24.36 - ball_depth - base_plate_thickness
    dove_tail_width = 16.26 + tolerance * 2
    dove_base_width = 13.0 + tolerance * 2
    
    lateral_vector = (heel_radius - 0.6*foot_width, heel_radius - 0.66*foot_length)
    # toe_vector = (1, -0.6) #old value, seemed to help chamfer problems, but less realistic
    toe_vector = (1, -1)
     
    #defines footprint shape
    big_toe_pt = (0, foot_length)#
    little_toe_pt = (0.4*foot_width, foot_length*0.94)
    ball_y = 0.66*foot_length # y distance of the widest part of the foot, where foot_width is measured
    footprint_spline_pts = [
        (0, 0),#base of heel
        (-heel_radius, heel_radius), #left side
        (-heel_radius, foot_length - (toe_length)),#connects medial edge to big toe
        (big_toe_pt),
        (little_toe_pt),
        (0.6*foot_width, ball_y), #TODO make right side end exactly at foot_width*0.6
        (heel_radius, heel_radius), #right side of heel
        (0.5*heel_radius, 0.2*heel_radius),
        (0, 0),#back to starting pt
    ]
    
    footprint_tangents = [
        (-1, 0), #back of heel is horizontal
        (0, 1), #tangent with medial edge
        (0, 1),
        (1, 0),#toe must be horizontal at foot_length
        (toe_vector),
        (lateral_vector),
        (lateral_vector), #forces tangecy with right (lateral) edge of foot
        (None),
        (-1, 0)
    ]
    
    #defines top of foot
    ankle_x = pylon_radius*2.4
    ankle_point = (ankle_x, ankle_height) #end of the arch, where the front of the pylon will connect
    arch_spline_pts = [
        (foot_length, toe_height), 
        (ball_y, toe_height+((ankle_height-toe_height)*0.2)), #((55% between ankle and toe), (12% between toe height and ankle height))
        (ankle_point) 
    ]
    
    arch_tangents = [
        (-1, 0),
        (None),
        (-0.4, 1),
    ]
    
    def getArch():
        arch = (
            cq.Workplane("right")
            .workplane(offset = -0.4*foot_width)
            .spline(arch_spline_pts, arch_tangents)
            .lineTo(foot_length*2, ankle_height)
            .lineTo(foot_length*2, toe_height)
            .close()
            .extrude(foot_width*2)
        )
        return arch
    
    def Foot():
        foot = (
            cq.Workplane("top")
            .spline(footprint_spline_pts, footprint_tangents)
            .close()
            .extrude(ankle_height)
            .cut(getArch())
            .combine()
            .faces("<<Y[1]")
            .edges("not |X")
            .chamfer(toe_height*0.4)
            .faces("<<Y[2]")
            .edges("not <<Y[1] or <<Y[0]")
            .chamfer(toe_height*0.2)
            # .faces("<Y")
            # .chamfer(toe_height*0.1)
        )
        return foot
    
    def AddPylon(foot):
        foot = (
            foot.faces(">Y")
            .edges()
            .toPending()
            .offset2D(0)
            .workplane(offset = pylon_height)
            .center(0, pylon_offset)
            .ellipse(pylon_radius, pylon_radius*1.2)
            .loft(combine = True)
        )
        return foot
    
    def CutPyramidAdapter(foot):
        base_height = 8
        adapter_base = (
            cq.Workplane("right")
            .center(pylon_offset, pylon_height+ankle_height - base_height/2)
            .box(62, base_height, pylon_radius*2)
            .edges("|Y")
            .fillet(8)
        )
        foot = foot.union(adapter_base).clean()
        
        adapter = (
            cq.Workplane("right")
            .center(pylon_offset, pylon_height+ankle_height)
            .lineTo(24, 0) # build ball joint profile
            .threePointArc((17, -7.5), (11.4, -10.8))
            .lineTo(0, -10.8)
            .close()
            .revolve(90, (0, 0), (0, -1)) #revolve ball joint
            .center(0, -ball_depth)
            .lineTo(dove_base_width/2, 0)#dove tail outline
            .lineTo(dove_tail_width/2, -dove_depth)
            .lineTo(0, -dove_depth)
            .close()
            .extrude(dove_base_width/2)
            .faces("<X")
            .extrude(-pylon_radius*2)
        )
        adapter = (
            adapter
            .mirror(adapter.faces(">Z"), union = True)
            .faces("<Y")
            .fillet(2)
            .faces("<<Y[4]")
            .edges("|X")
            .fillet(1)
        )
        foot = foot.cut(adapter)
        return foot
    
    def AssembleFoot():
        foot = Foot()
        # foot = AddPylon(foot)
        # foot = CutPyramidAdapter(foot)
        
        if (right == False):
            foot = foot.mirror("YZ")
        
        return foot
    
    foot = AssembleFoot()
    return foot
    
#end of CadQuery script

def BuildModel():
    if st.button("Generate File"):
        st.switch_page("downloadLanding.py")
        try:
            st.session_state.foot = GetShape()

            with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
                tmp_path = tmp.name
                st.session_state.foot.val().export(tmp_path)
    
            with open(tmp_path, "rb") as f:
                st.session_state.stl_bytes = f.read()
    
            os.unlink(tmp_path)

            download = False
            if "stl_bytes" in st.session_state:
                download = st.download_button(
                    "Download STL",
                    st.session_state.stl_bytes,
                    "OpenGaitLeg.stl"
                )
            if download:
                st.switch_page("downloadLanding.py")
                
        except Exception as e:
            st.error("Model generation failed")
            st.code(traceback.format_exc())
            raise
    

PageContents()
BuildModel()




















