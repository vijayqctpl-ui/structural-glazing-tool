import streamlit as st
import math
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Structural Glazing Tool", layout="wide")

# -----------------------------
# HEADER
# -----------------------------
st.title("Structural Glazing Design Tool")
st.caption("Professional Engineering Application")

# -----------------------------
# PROJECT DETAILS
# -----------------------------
st.markdown("## Project Information")

col1, col2, col3 = st.columns(3)

with col1:
    project = st.text_input("Project Name")

with col2:
    location = st.text_input("Location")

with col3:
    engineer = st.text_input("Engineer")

st.write(f"Date: {date.today()}")

# -----------------------------
# DESIGN BASIS
# -----------------------------
st.markdown("## Design Basis")

st.info("""
Tensile Stress: 0.14 MPa  
Shear Stress (Long term): 0.007 MPa  
Minimum Bite: 6 mm  
Minimum Thickness: 6 mm
""")

# -----------------------------
# TABS
# -----------------------------
tabs = st.tabs([
    "Structural Bite",
    "Dead Load",
    "Thermal",
    "Combined Check",
    "Material"
])

# -----------------------------
# STRUCTURAL BITE
# -----------------------------
with tabs[0]:

    st.subheader("Structural Bite Calculation")

    shape = st.selectbox("Panel Shape", ["Rectangular", "Circular", "Triangular"], key="shape")

    if shape in ["Rectangular", "Circular"]:

        col1, col2 = st.columns(2)

        with col1:
            wind = st.number_input("Wind Load (kPa)", value=2.5, key="wind_rect")

        with col2:
            span = st.number_input("Short Span / Diameter (mm)", value=1000, key="span_rect")

        if st.button("Calculate Bite", key="btn_bite"):

            bite = (wind * span) / (2 * 0.14 * 1000)

            st.metric("Required Bite (mm)", f"{bite:.2f}")

            if bite >= 6:
                st.success("SAFE")
            else:
                st.error("NOT SAFE")

    elif shape == "Triangular":

        st.subheader("Triangular Panel Calculation")

        col1, col2, col3 = st.columns(3)

        with col1:
            wind_kg = st.number_input("Wind Load (kg/m²)", value=150, key="wind_tri")

        with col2:
            side_A = st.number_input("Hypotenuse A (m)", value=2.5, key="sideA")

        with col3:
            angle_a = st.number_input("Angle a (°)", value=60, key="angleA")

        angle_b = st.number_input("Angle b (°)", value=30, key="angleB")

        if st.button("Calculate Triangle Bite", key="btn_tri"):

            term1 = (wind_kg * side_A) / 28

            tan_a = math.tan(math.radians(angle_a / 2))
            tan_b = math.tan(math.radians(angle_b / 2))

            geometry = 1 / ((1 / tan_a) + (1 / tan_b))

            scd = term1 * geometry

            st.metric("Required Bite (mm)", f"{scd:.2f}")

            if scd >= 6:
                st.success("SAFE")
            else:
                st.warning("Use minimum 6 mm")

# -----------------------------
# DEAD LOAD
# -----------------------------
with tabs[1]:

    st.subheader("Dead Load Shear Check")

    col1, col2, col3 = st.columns(3)

    with col1:
        thickness = st.number_input("Glass Thickness (mm)", value=10, key="thickness_dead")

    with col2:
        height = st.number_input("Height (mm)", value=1500, key="height_dead")

    with col3:
        width = st.number_input("Width (mm)", value=1000, key="width_dead")

    sealant = st.number_input("Sealant Thickness (mm)", value=6, key="sealant_dead")

    if st.button("Check Shear", key="btn_dead"):

        h = height / 1000
        w = width / 1000
        t = thickness / 1000

        density = 25

        weight = density * h * w * t
        perimeter = 2 * (h + w)

        shear = weight / (perimeter * (sealant / 1000))

        st.metric("Shear Stress (MPa)", f"{shear:.4f}")

        if shear < 0.007:
            st.success("SAFE")
        else:
            st.error("NOT SAFE")

# -----------------------------
# THERMAL
# -----------------------------
with tabs[2]:

    st.subheader("Thermal Movement")

    col1, col2 = st.columns(2)

    with col1:
        length = st.number_input("Panel Length (mm)", value=1500, key="length")

    with col2:
        deltaT = st.number_input("Temperature Change (°C)", value=60, key="temp")

    if st.button("Calculate Movement", key="btn_thermal"):

        cte_glass = 9e-6
        cte_al = 23e-6

        move_glass = length * cte_glass * deltaT
        move_al = length * cte_al * deltaT

        diff = abs(move_al - move_glass)

        st.metric("Differential Movement (mm)", f"{diff:.2f}")

        if diff < 6:
            st.success("OK")
        else:
            st.warning("Increase thickness")

# -----------------------------
# COMBINED CHECK
# -----------------------------
with tabs[3]:

    st.subheader("Combined Design Check")

    wind = st.number_input("Wind Load (kPa)", value=2.5, key="wind_comb")
    span = st.number_input("Short Span (mm)", value=1000, key="span_comb")
    thickness = st.number_input("Glass Thickness (mm)", value=10, key="thickness_comb")
    height = st.number_input("Height (mm)", value=1500, key="height_comb")
    width = st.number_input("Width (mm)", value=1000, key="width_comb")
    sealant = st.number_input("Sealant Thickness (mm)", value=6, key="sealant_comb")

    if st.button("Run Check", key="btn_comb"):

        bite = (wind * span) / (2 * 0.14 * 1000)

        h = height / 1000
        w = width / 1000
        t = thickness / 1000

        density = 25
        weight = density * h * w * t
        perimeter = 2 * (h + w)

        shear = weight / (perimeter * (sealant / 1000))

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Bite (mm)", f"{bite:.2f}")

        with col2:
            st.metric("Shear (MPa)", f"{shear:.4f}")

        if bite >= 6 and shear < 0.007:
            st.success("FINAL STATUS: SAFE")
        else:
            st.error("FINAL STATUS: NOT SAFE")

        # REPORT
        if st.button("Generate Report", key="btn_report"):

            doc = SimpleDocTemplate("report.pdf")
            styles = getSampleStyleSheet()
            content = []

            content.append(Paragraph("STRUCTURAL GLAZING REPORT", styles['Title']))
            content.append(Spacer(1, 12))

            content.append(Paragraph(f"Project: {project}", styles['Normal']))
            content.append(Paragraph(f"Location: {location}", styles['Normal']))
            content.append(Paragraph(f"Engineer: {engineer}", styles['Normal']))
            content.append(Spacer(1, 12))

            table_data = [
                ["Parameter", "Value"],
                ["Wind Load", wind],
                ["Span", span],
                ["Bite", f"{bite:.2f} mm"],
                ["Shear", f"{shear:.4f} MPa"]
            ]

            table = Table(table_data)
            table.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.5, colors.black)
            ]))

            content.append(table)
            doc.build(content)

            with open("report.pdf", "rb") as f:
                st.download_button("Download Report", f)

# -----------------------------
# MATERIAL
# -----------------------------
with tabs[4]:

    st.subheader("Material Estimation")

    bite = st.number_input("Bite (mm)", value=10, key="bite_mat")
    thickness = st.number_input("Thickness (mm)", value=6, key="thick_mat")
    length = st.number_input("Joint Length (m)", value=10, key="length_mat")

    if st.button("Estimate", key="btn_mat"):

        area = (bite * thickness) / 1e6
        volume = area * length

        liters = volume * 1000
        cartridges = liters / 0.6

        st.metric("Volume (L)", f"{liters:.2f}")
        st.metric("Cartridges", f"{cartridges:.0f}")