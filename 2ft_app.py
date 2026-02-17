import streamlit as st
import cadquery as cq
from cadquery import exporters
import tempfile
import os

def PageContents():
    #standard bounds in metric (mm, kg)
    height_lb = 200
    height_ub = 500
    foot_length_lb = 120
    foot_length_ub = 280
    weight_lb = 20
    weight_ub = 100
    predicted_width_intercept = 17.3

    #conversion factors
    in_per_mm = 1/25.4
    lb_per_kg = 2.20462

    #page elements
    st.title("2ft Custom Prosthesis")
    metric = st.toggle("Use metreic units (mm, kg)", value = True)
    if metric:
        height = st.slider("Height (mm)", height_lb, height_ub)
        foot_length = st.slider("Foot Length (mm)", foot_length_lb, foot_length_ub)
        predicted_width = 0.32 * foot_length + predicted_width_intercept
        width_lb = predicted_width * 0.6
        width_ub = predicted_width * 1.4
        foot_width = st.slider("Foot Width (mm)", width_lb, width_ub, value = predicted_width)
        weight = st.slider("Weight (kg)", weight_lb, weight_ub)
    else:
        height = st.slider("Height (in)", height_lb*in_per_mm, height_ub*in_per_mm)
        foot_length = st.slider("Foot Length (in)", foot_length_lb*in_per_mm, foot_length_ub*in_per_mm)
        predicted_width = 0.32 * foot_length + predicted_width_intercept*in_per_mm
        width_lb = predicted_width * 0.6
        width_ub = predicted_width * 1.4
        foot_width = st.slider("Foot Width (in)", width_lb, width_ub, value = predicted_width)
        weight = st.slider("Weight (lbs)", weight_lb*lb_per_kg, weight_ub*lb_per_kg)
        
    right = st.toggle("Right foot")
    advanced_options = st.toggle("Use advanced measurements")
        
    return height, foot_length, foot_width, weight, right, advanced_options
    

def GetShape():
    def getAdvancedMeasurements():
        predicted_pylon_radius = 30 #TODO make this reflect weight or proportional to given measurement
        predicted_ankle_height = foot_length*0.3 # height where foot meets pylon
        predicted_toe_height = predicted_ankle_height*0.5
        predicted_pylon_offset = predicted_pylon_radius*1.2
        return ankle_height, toe_height, pylon_offset, pylon_radius
    
    height, foot_length, foot_width, weight, right, advanced_options  = PageContents()
    heel_radius = 0.4 * foot_width
    ankle_height, toe_height, pylon_offset, pylon_radius = getAdvancedMeasurements()
    pylon_height = height - ankle_height
    toe_radius = 0.6 * heel_radius

    #pyramid adapter
    ball_base_radius = 47.8/2
    ball_depth = 10.7
    dove_depth = 11.1
    dove_tail_width = 18.3
    dove_base_width = 14
    
    lateral_vector = (heel_radius - 0.6*foot_width, heel_radius - 0.66*foot_length)
    toe_vector = (1, -0.7)

    #defines back of the heel curvature
    heel_spline_pts = [
        (heel_radius, heel_radius), #right side of heel
        (0.5*heel_radius, 0.2*heel_radius),
        (0, 0),#base of heel
        (-heel_radius, heel_radius), #left side
    ]
    
    heel_tangents = [
        (lateral_vector), #forces tangecy with right (lateral) edge of foot
        (None),
        (-1, 0),
        (0,1), #tangent with medial edge
    ]
    
    #Big toe spline part
    big_toe_pt = (-0.3*heel_radius, foot_length)# TODO make toe end exactly at foot_length
    little_toe_pt = (0, foot_length*0.99)
    toe_spline_pts = [
        (-heel_radius, foot_length - (toe_radius)), #
        (big_toe_pt),
        (little_toe_pt),
        (0.6*foot_width, 0.66*foot_length),
    ]
    
    toe_tangents = [
        (0, 1),
        (1, 0),
        (toe_vector),
        (lateral_vector),
    ]

    #defines top of foot
    arch_spline_pts = [
        (foot_length, toe_height), #
        (pylon_radius*2+(foot_length-pylon_radius*2)*0.7, toe_height+((ankle_height-toe_height)*0.1)),
        (pylon_radius*2, ankle_height) #end of the arch, where the front of the pylon will connect
    ]
    
    arch_tangents = [
        (-1, 0),
        (None),
        (None),
    ]
    
    def getArch():
        arch = (
            cq.Workplane("right")
            .spline(arch_spline_pts, arch_tangents)
            .lineTo(foot_length*2, ankle_height)
            .lineTo(foot_length*2, toe_height)
            .close()
            .extrude(foot_width, both = True)
        )
        return arch
    
    def CutPyramidAdapter(foot):
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
    
    def Foot():
        foot = (
            cq.Workplane("top")
            .spline(heel_spline_pts, heel_tangents)
            .lineTo(-heel_radius, foot_length - toe_radius)
            .spline(toe_spline_pts, toe_tangents)
            .close()
            .extrude(ankle_height)
            .cut(getArch())
            .faces("<<Y[1]")
            .edges("not |X")
            .fillet(toe_height/2)
            .faces("<Y")
            .fillet(toe_height/5)
        )
        return foot
        
    def AssembleFoot():
        foot = Foot()
        foot = AddPylon(foot)
        foot = CutPyramidAdapter(foot)
        
        if (right == False):
            foot = foot.mirror("YZ")
        
        return foot
    
    foot = AssembleFoot()
    return foot

#end of CadQuery script





def ExportSTL(result):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
            tmp_path = tmp.name
            result.val().export(tmp_path)
        
        with open(tmp_path, "rb") as f:
            stl_bytes = f.read()
        
    except Exception:
        pass
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    st.download_button("Download STL", stl_bytes, "leg2.stl")


ExportSTL(GetShape())





















