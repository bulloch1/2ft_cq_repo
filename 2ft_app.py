import streamlit as st
import cadquery as cq
from cadquery import exporters
import tempfile
import os

def PageContents():
    st.title("2ft Custom Prosthesis")
    height = st.slider("Height (cm)", 20.0, 50.0)*100
    foot_length = st.slider("Height (cm)", 12.0, 30.0)*100
    foot_width = st.slider("Foot Width", 5.0, 12.0)*100
    right = st.toggle("Right foot?")
    
    return height, foot_length, foot_width, right

def GetShape():
    height, length, foot_width, right = PageContents()
    weight = 100
    # length = 25
    # foot_width = 10
    # height = 25
    pylon_radius = 3
    # right = True
    
    foot_height = 2.5 #change to support load or match trends
    pylon_height = height - foot_height
    ankle_radius = 0.4 * foot_width
    toe_radius = 0.6 * ankle_radius
    heel_radius = 0.4 * foot_width
    t_offset = 0.01
    
    lateral_vector = (ankle_radius - 0.6*foot_width, ankle_radius - 0.66*length)
    toe_vector = (1, -0.7)
    
    heel_spline_pts = [
        (heel_radius, heel_radius), #right side of heel
        (0.5*heel_radius, 0.2*heel_radius),
        (0, 0),#base of heel
        # (-0.5*heel_radius, 0.3*heel_radius),
        (-heel_radius, 2*heel_radius), #left side
    ]
    
    heel_tangents = [
        (lateral_vector), #forces tangecy with right (lateral) edge of foot
        (None),
        (-1, 0),
        (0,1), #tangent with medial edge
    ]
    
    #Big toe part
    big_toe_pt = (-0.1 * ankle_radius, length)
    medial_toe_spline_pts = [
        (-ankle_radius, length - (toe_radius)), #
        (big_toe_pt),
    ]
    
    medial_toe_tangents = [
        (0, 1),
        (toe_vector),
    ]
    
    #little toes part
    lateral_toe_spline_pts = [
        (big_toe_pt),
        (0.6*foot_width, 0.66*length),
    ]
    
    lateral_toe_tangents = [
        (toe_vector),
        (lateral_vector),
    ]

    #foot
    result = (
        cq.Workplane("front")
        .spline(heel_spline_pts, heel_tangents)
        .lineTo(-ankle_radius, length - toe_radius)
        .spline(medial_toe_spline_pts, medial_toe_tangents)
        .spline(lateral_toe_spline_pts, lateral_toe_tangents)
        .close()
        .extrude(foot_height)
        .faces(">Z")
        .fillet(1)
    )
    
    #pylon
    result = (
        result.center(0, pylon_radius)
        .ellipse(pylon_radius, pylon_radius*1.2)
        .extrude(pylon_height)
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


