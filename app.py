import streamlit as st
import math
from datetime import date

# -----------------------------
# PASSWORD PROTECTION
# -----------------------------
def check_password():
    def password_entered():
        if st.session_state["password"] == "Vijay@2026":   # 🔑 change if needed
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Password", type="password", key="password", on_change=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Password", type="password", key="password", on_change=password_entered)
        st.error("Incorrect Password")
        return False
    else:
        return True

if not check_password():
    st.stop()

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

col1, col2 = st.columns(2)

with col1:
    project = st.text_input("Project Name")

with col2:
    location = st.text_input("Location")

st.write(f"Date: {date.today()}")

# -----------------------------
# DESIGN BASIS
# -----------------------------
st.markdown("## Design Basis")

st.info("""
Tensile Stress: 0.14 MPa  
Shear Stress (Long term): 7 kPa  
Minimum Bite: 6 mm  
""")

# -----------------------------
# TABS
# -----------------------------
tabs = st.tabs([
    "Structural Bite",
    "Dead Load",
    "Thermal"
])

# -----------------------------
# STRUCTURAL BITE
# -----------------------------
with tabs[0]:

    st.subheader("Structural Bite Calculation")

    shape = st.selectbox("Panel Shape", ["Rectangular", "Circular", "Triangular"], key="shape")

    # RECTANGULAR / CIRCULAR
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

    # TRIANGLE
    elif shape == "Triangular":

        st.subheader("Triangular Panel Calculation")

        wind_kpa = st.number_input("Wind Load (kPa)", value=1.5, key="wind_tri")
        side_A = st.number_input("Hypotenuse A (mm)", value=2500, key="sideA")
        angle_a = st.number_input("Angle a (°)", value=60, key="angleA")
        angle_b = st.number_input("Angle b (°)", value=30, key="angleB")

        if st.button("Calculate Triangle Bite", key="btn_tri"):

            # Convert kPa → kg/m²
            wind = wind_kpa * 100  

            # Convert mm → m
            A = side_A / 1000  

            term1 = (wind * A) / 28

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

    st.subheader("Dead Load Calculation")

    length = st.number_input("Window Length (mm)", value=1500, key="len_dl")
    width = st.number_input("Window Width (mm)", value=1500, key="wid_dl")
    glass_weight = st.number_input("Glass Weight (kg/m²)", value=25, key="gw_dl")
    bite = st.number_input("Bite (mm)", value=15, key="bite_dl")

    if st.button("Calculate Dead Load", key="btn_dl"):

        # Convert mm → m
        L = length / 1000
        W = width / 1000

        # Area
        area = L * W

        # Weight in kg
        weight_kg = glass_weight * area

        # Convert to Newton
        weight_N = weight_kg * 9.81

        # Perimeter
        perimeter = 2 * (L + W)

        # Stress (Pa)
        stress = weight_N / (perimeter * (bite / 1000))

        # Convert to kPa
        stress_kpa = stress / 1000

        st.metric("Sealant Stress (kPa)", f"{stress_kpa:.2f}")

        if stress_kpa < 7:
            st.success("PASS")
        else:
            st.error("FAIL")

# -----------------------------
# THERMAL
# -----------------------------
with tabs[2]:

    st.subheader("Thermal Movement")

    length = st.number_input("Panel Length (mm)", value=1500, key="length")
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