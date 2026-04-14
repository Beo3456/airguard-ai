import requests
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Air Quality Monitor",
    page_icon="🌫️",
    layout="wide",
)

# =========================
# CONFIG
# =========================
BASE_URL = "https://api.waqi.info/feed/{}/"
TOKEN = "19555aceabb14118cafec4e2a60d1342f7aa0ce3"
DEFAULT_STATION = "ho-chi-minh-city"


# =========================
# HELPERS
# =========================
def get_aqi_status(aqi: int):
    if aqi <= 50:
        return "Good", "Không khí tốt, an toàn cho hầu hết mọi người.", "🟢"
    if aqi <= 100:
        return "Moderate", "Chấp nhận được, nhưng người nhạy cảm nên chú ý.", "🟡"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups", "Trẻ em, người già, người có bệnh hô hấp nên hạn chế ra ngoài lâu.", "🟠"
    if aqi <= 200:
        return "Unhealthy", "Mọi người nên giảm hoạt động ngoài trời.", "🔴"
    if aqi <= 300:
        return "Very Unhealthy", "Không khí rất xấu, nên hạn chế ra ngoài nếu không cần thiết.", "🟣"
    return "Hazardous", "Nguy hại cho sức khỏe, nên ở trong nhà và bảo vệ hô hấp.", "⚫"


def safe_iaqi_value(iaqi: dict, key: str):
    try:
        return iaqi.get(key, {}).get("v", "-")
    except Exception:
        return "-"


@st.cache_data(ttl=600)
def fetch_air_quality(station: str):
    response = requests.get(
        BASE_URL.format(station),
        params={"token": TOKEN},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "ok":
        raise ValueError(payload.get("data", "Không lấy được dữ liệu từ API"))

    return payload.get("data", {})


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("⚙️ Cài đặt")
    station = st.text_input(
        "Nhập station / địa điểm",
        value=DEFAULT_STATION,
        help="Ví dụ: ho-chi-minh-city, hanoi, beijing, here, @1251",
    )

    if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
        fetch_air_quality.clear()

    st.markdown("---")
    st.markdown("### Gợi ý station")
    st.code("ho-chi-minh-city")
    st.code("hanoi")
    st.code("beijing")
    st.code("here")


# =========================
# MAIN UI
# =========================
st.title("🌫️ Air Quality Monitor App")
st.caption("Ứng dụng theo dõi chất lượng không khí bằng WAQI API")

try:
    data = fetch_air_quality(station.strip())

    city = data.get("city", {})
    city_name = city.get("name", "Unknown location") if isinstance(city, dict) else str(city)

    aqi = data.get("aqi", 0)
    try:
        aqi = int(aqi)
    except Exception:
        aqi = 0

    dominentpol = str(data.get("dominentpol", "N/A")).upper()
    iaqi = data.get("iaqi", {}) if isinstance(data.get("iaqi"), dict) else {}
    time_data = data.get("time", {}) if isinstance(data.get("time"), dict) else {}
    updated_at = time_data.get("s", "N/A")
    timezone = time_data.get("tz", "")

    status_label, health_message, status_icon = get_aqi_status(aqi)

    st.subheader(f"📍 {city_name}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AQI", aqi)
    col2.metric("Mức độ", f"{status_icon} {status_label}")
    col3.metric("Chất ô nhiễm chính", dominentpol)
    col4.metric("Cập nhật", updated_at)

    st.info(health_message)

    st.markdown("### Chỉ số chi tiết")
    d1, d2, d3, d4, d5, d6 = st.columns(6)
    d1.metric("PM2.5", safe_iaqi_value(iaqi, "pm25"))
    d2.metric("PM10", safe_iaqi_value(iaqi, "pm10"))
    d3.metric("CO", safe_iaqi_value(iaqi, "co"))
    d4.metric("NO₂", safe_iaqi_value(iaqi, "no2"))
    d5.metric("SO₂", safe_iaqi_value(iaqi, "so2"))
    d6.metric("O₃", safe_iaqi_value(iaqi, "o3"))

    st.markdown("### Thông tin bổ sung")
    extra1, extra2 = st.columns(2)

    with extra1:
        st.write(f"**Thời gian cập nhật:** {updated_at}")
        st.write(f"**Múi giờ:** {timezone or 'N/A'}")

    with extra2:
        forecast = data.get("forecast", {})
        has_forecast = "Có" if forecast else "Không"
        st.write(f"**Có dữ liệu dự báo:** {has_forecast}")
        st.write(f"**Thời điểm xem app:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with st.expander("Xem dữ liệu JSON thô"):
        st.json(data)

except requests.RequestException as e:
    st.error(f"Lỗi kết nối API: {e}")
except ValueError as e:
    st.error(f"API trả về lỗi: {e}")
except Exception as e:
    st.error(f"Có lỗi xảy ra: {e}")

st.markdown("---")
st.caption("Made with Streamlit + WAQI API")

# =========================
# requirements.txt
# =========================
# streamlit
# requests

# =========================
# RUN LOCAL
# =========================
# streamlit run app.py

# =========================
# IMPORTANT
# =========================
# Code này chạy được ngay, nhưng vì token đang viết trực tiếp trong code,
# bạn KHÔNG nên public nguyên bản này lên GitHub.
# Trước khi public, hãy chuyển TOKEN sang st.secrets hoặc biến môi trường.
