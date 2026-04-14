import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="AirGuard AI", page_icon="🌫️", layout="wide")

st.title("🌫️ AirGuard AI")
st.subheader("Đo mức độ ô nhiễm không khí THỰC TẾ tại TP.HCM")
st.caption("Dữ liệu từ trạm Lãnh sự quán Mỹ • Cập nhật mỗi giờ")

token = "19555aceabb14118cafec4e2a60d1342f7aa0ce3"

if st.button("📡 Lấy dữ liệu thực tế ngay", type="primary", use_container_width=True):
    with st.spinner("Đang kết nối trạm đo thực tế..."):
        url = f"https://api.waqi.info/feed/@8767/?token={token}"
        try:
            response = requests.get(url, timeout=15)
            data = response.json()

            if data["status"] == "ok":
                # === FIX: Xử lý an toàn dữ liệu ===
                aqi_raw = data["data"].get("aqi")
                try:
                    aqi = int(aqi_raw) if aqi_raw is not None else -1
                except:
                    aqi = -1

                pm25_raw = data["data"].get("iaqi", {}).get("pm25", {}).get("v")
                try:
                    pm25 = float(pm25_raw) if pm25_raw is not None else None
                except:
                    pm25 = None

                city = data["data"]["city"]["name"]

                st.success(f"✅ Dữ liệu thực tế từ {city}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("**AQI**", aqi if aqi > 0 else "N/A")
                with col2:
                    st.metric("**PM2.5**", f"{pm25} µg/m³" if pm25 is not None else "N/A")
                with col3:
                    st.metric("Cập nhật lúc", datetime.now().strftime("%H:%M %d/%m"))

                # Phân loại thông minh
                if aqi <= 0:
                    st.warning("⚠️ Dữ liệu tạm thời không khả dụng. Vui lòng thử lại sau vài phút.")
                elif aqi <= 50:
                    st.success("🟢 Tốt - Có thể ra ngoài bình thường")
                elif aqi <= 100:
                    st.warning("🟡 Trung bình - Nên đeo khẩu trang nếu nhạy cảm")
                else:
                    st.error("🔴 Không tốt - Hạn chế ra ngoài, đeo khẩu trang N95")

                st.info("💡 AirGuard AI khuyên: Nếu AQI > 100, nên ở trong nhà hoặc đeo khẩu trang khi di chuyển.")

            else:
                st.error("❌ API trả về lỗi. Vui lòng thử lại sau.")
        except Exception as e:
            st.error(f"❌ Không kết nối được: {str(e)}")

st.markdown("---")
st.caption("AirGuard AI • Thử thách AI Driven Innovation 2026")