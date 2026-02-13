import streamlit as st
import cadquery as cq
from cadquery import exporters
import tempfile
import os

def PageContents():
    st.title("2ft Custom Prosthesis")
    height = st.slider("Height (cm)", 20.0, 50.0)*10
    foot_length = st.slider("Foot Length (cm)", 12.0, 30.0)*10
    foot_width = st.slider("Foot Width", 5.0, 12.0)*10
    right = st.toggle("Right foot?")
    
    return height, foot_length, foot_width, right

def GetShape():
    height, foot_length, foot_width, right = PageContents()

    weight = 100
    # foot_length = 250
    # foot_width = 100
    # height = 250
    pylon_radius = 30
    # right = True
    
    foot_height = 25 #change to support load or match trends
    ankle_height = 85 # height where foot meets pylon
    toe_height = 35
    pylon_height = height - foot_height
    ankle_radius = 0.4 * foot_width
    toe_radius = 0.6 * ankle_radius
    heel_radius = 0.4 * foot_width
    # t_offset = 0.01
    
    lateral_vector = (ankle_radius - 0.6*foot_width, ankle_radius - 0.66*foot_length)
    toe_vector = (1, -0.7)
    
    
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
    
    #Big toe part
    big_toe_pt = (-0.1 * ankle_radius, foot_length*0.99)# TODO make toe end exactly at foot_length
    medial_toe_spline_pts = [
        (-ankle_radius, foot_length - (toe_radius)), #
        (big_toe_pt),
    ]
    
    medial_toe_tangents = [
        (0, 1),
        (toe_vector),
    ]
    
    #little toes part
    lateral_toe_spline_pts = [ #TODO make lateral edge end exactly at 0.6foot_width
        (big_toe_pt),
        (0.6*foot_width, 0.66*foot_length),
    ]
    
    lateral_toe_tangents = [
        (toe_vector),
        (lateral_vector),
    ]
    
    arch_spline_pts = [
        (foot_length, toe_height), #
        (foot_length*0.7, toe_height*1.2),
        (pylon_radius*3, ankle_height) #end of the arch, where the front of the pylon will connect
    ]
    
    arch_tangents = [
        (-1, 0),
        (None),
        (None),
    ]
    
    arch = (
        cq.Workplane("right")
        .spline(arch_spline_pts, arch_tangents)
        .lineTo(foot_length*2, ankle_height)
        .lineTo(foot_length*2, toe_height)
        .close()
        .extrude(foot_width, both = True)
    )
    
    arch_face = arch.faces("<Y").val()
    
    #foot
    result = (
        cq.Workplane("top")
        .spline(heel_spline_pts, heel_tangents)
        .lineTo(-ankle_radius, foot_length - toe_radius)
        .spline(medial_toe_spline_pts, medial_toe_tangents)
        .spline(lateral_toe_spline_pts, lateral_toe_tangents)
        .close()
        .extrude(ankle_height)
        .cut(arch)
        .faces(">Y[1]")
        .fillet(20)
        .faces("<Y")
        .fillet(5)
    )
    
    #pylon
    result = (
        result.faces(">Y")
        .edges()
        .toPending()
        .offset2D(0)
        .workplane(offset = pylon_height)
        .center(0, foot_length*0.2)
        .ellipse(pylon_radius, pylon_radius*1.2)
        .loft(combine = True)
    )
    
    if (right == False):
        result = result.mirror("YZ")
        
    return result

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








