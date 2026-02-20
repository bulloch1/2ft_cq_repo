import streamlit as st
import cadquery as cq
from cadquery import exporters
import tempfile
import os

def PageContents():
#     #standard bounds in metric (mm, kg)
    height_lb = 150
    height_ub = 400
    foot_length_lb = 150
    foot_length_avg = 200
    foot_length_ub = 300
    weight_lb = 20
    weight_ub = 100
    predicted_width_intercept = 17.3

#     #conversion factors
    in_per_mm = 1/25.4
    lb_per_kg = 2.20462
        
#     #page elements
    st.title("2ft Custom Prosthesis 902")
    metric = st.toggle("Use metric units (mm, kg)", value = True)
    if metric:
        foot_length = st.slider("Foot Length (mm)", foot_length_lb, foot_length_ub, value = foot_length_avg)
#         height_lb = int(foot_length*0.5) #height must be greater than ankle height (foot_length*0.4)
        
#         height = st.slider("Height of Residual Limb (mm)", height_lb, height_ub)
        predicted_width = 0.32 * foot_length + predicted_width_intercept
        # predicted_width = 72
        width_lb = int(predicted_width * 0.85)
        width_ub = int(predicted_width * 1.4)
        foot_width = st.slider("Foot Width (mm)", width_lb, width_ub, value = predicted_width)
#         weight = st.slider("Weight (kg)", weight_lb, weight_ub)
#     else:
#         st.title("make sure imperial is working")
#         # height = st.slider("Height (in)", height_lb*in_per_mm, height_ub*in_per_mm)/in_per_mm
#         # foot_length = st.slider("Foot Length (in)", foot_length_lb*in_per_mm, foot_length_ub*in_per_mm)/in_per_mm
#         # predicted_width = 0.32 * foot_length + predicted_width_intercept*in_per_mm
#         # width_lb = predicted_width * 0.6
#         # width_ub = predicted_width * 1.4
#         # foot_width = st.slider("Foot Width (in)", width_lb, width_ub, value = predicted_width)/in_per_mm
#         # weight = st.slider("Weight (lbs)", weight_lb*lb_per_kg, weight_ub*lb_per_kg)/lb_per_kg
        
#     right = st.toggle("Right foot")
#     advanced_options = st.toggle("Use advanced measurements", value = False)


    weight = 20
    # foot_length = 200
    # foot_width = 72
    height = 130
    right = True
    advanced_options = False
        
    return height, foot_length, foot_width, weight, right, advanced_options    

def GetShape():
    def getAdvancedMeasurements():
        # predicted_pylon_radius = heel_radius #TODO make this reflect weight or proportional to given measurement
        # predicted_ankle_height = foot_length*0.4 # height where foot meets pylon. Currently arbitrary. TODO? 
        # predicted_toe_height = foot_length*0.15 # Arbitrary
        # predicted_pylon_offset = predicted_pylon_radius*1.2 #makes the back of the heel line up with the back of the pylon
        
        # if (advanced_options):
        #     pylon_radius = st.slider("Ankle radius", predicted_pylon_radius * 0.8, predicted_pylon_radius * 1.2, value = predicted_pylon_radius)
        #     ankle_height = st.slider("Ankle Height", predicted_ankle_height * 0.8, predicted_ankle_height * 1.2, value = predicted_ankle_height)
        #     toe_height = st.slider("Toe height", predicted_toe_height * 0.8, predicted_toe_height*1.2, value = predicted_toe_height)
        #     pylon_offest = st.slider("forward leg offset", predicted_pylon_offset * 0.8, predicted_pylon_offset * 1.2, value = predicted_pylon_offset)
        # else:
        #     ankle_height = predicted_ankle_height
        #     toe_height = predicted_toe_height
        #     pylon_offset = predicted_pylon_offset
        #     pylon_radius = predicted_pylon_radius


        pylon_radius = heel_radius #TODO make this reflect weight or proportional to given measurement
        ankle_height = foot_length*0.4 # height where foot meets pylon
        toe_height = foot_length*0.15
        pylon_offset = pylon_radius*1.2
        return ankle_height, toe_height, pylon_offset, pylon_radius

    # Start of CadQuery script
    
    height, foot_length, foot_width, weight, right, advanced_options = PageContents()
    
    heel_radius = 0.4 * foot_width #this value makes the medial edge of the heel vertical (40% of foot is medial, 60% is lateral)
    ankle_height, toe_height, pylon_offset, pylon_radius = getAdvancedMeasurements()
    
    pylon_height = height - ankle_height
    toe_length = 0.14 * foot_length
     
    #pyramid adapter
    ball_base_radius = 47.8/2
    ball_depth = 10.7
    dove_depth = 11.1
    dove_tail_width = 18.3
    dove_base_width = 14
    
    lateral_vector = (heel_radius - 0.6*foot_width, heel_radius - 0.66*foot_length)
    toe_vector = (1, -0.6)
     
    #defines footprint shape
    big_toe_pt = (-0.2*heel_radius, foot_length)#
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
        # (ankle_x+(foot_length-ankle_x)*0.55, toe_height+((ankle_height-toe_height)*0.12)), #((55% between ankle and toe), (12% between toe height and ankle height))
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
            .clean()
            .faces("<<Y[1]")
            .edges("not |X")
            .chamfer(toe_height*0.4)
            .faces("<<Y[2]")
            .edges("not <<Y[1] or <<Y[0]")
            .chamfer(toe_height*0.2)
            .faces("<Y")
            .chamfer(toe_height*0.1)
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


































































