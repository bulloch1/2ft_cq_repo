import streamlit as st
import cadquery as cq
from cadquery import exporters
import tempfile
import os

def PageContents():
    st.title("2ft Custom Prosthesis")
    length = st.slider("Leg length (cm)", 20, 400)
    circumference = st.slider("Residual Limb Circumference", 10, 30)
    return length, circumference

def GetShape():
    l, c = PageContents()
    result = cq.Workplane("XY").box(l, c/4, c/4).edges("|Z").fillet(0.125)
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