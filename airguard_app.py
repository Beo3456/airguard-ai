import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="AirGuard AI", page_icon="🌫️", layout="wide")

st.title("🌫️ AirGuard AI")
st.subheader("Đo mức độ ô nhiễm không khí THỰC TẾ tại TP.HCM")
st.caption("Dữ liệu từ trạm Lãnh sự quán Mỹ • Cập nhật mỗi giờ")

token = "19555aceabb14118cafec4e2a60d1342f7aa0ce3"

if st.button("📡 Lấy dữ liệu thực tế ngay", type="primary", use_container_width=True):
    with st.spinner("Đang kết nối trạm đo thực tế... (có thể mất 5-10 giây)"):
        url = f"https://api.waqi.info/feed/@8767/?token={token}"
        try:
            response = requests.get(url, timeout=15)
            data = response.json()

            if data["status"] == "ok":
                # FIX LỖI: Chuyển AQI và PM2.5 về số an toàn
                aqi_raw = data["data"]["aqi"]
                aqi = int(aqi_raw) if isinstance(aqi_raw, (int, str)) and str(aqi_raw).isdigit() else 0
                
                pm25_raw = data["data"]["iaqi"].get("pm25", {}).get("v", "N/A")
                pm25 = float(pm25_raw) if isinstance(pm25_raw, (int, float, str)) and str(pm25_raw).replace('.','').isdigit() else "N/A"
                
                city = data["data"]["city"]["name"]
                
                st.success(f"✅ Dữ liệu thực tế từ {city}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("**AQI**", aqi)
                with col2:
                    st.metric("**PM2.5**", f"{pm25} µg/m³" if pm25 != "N/A" else "N/A")
                with col3:
                    st.metric("Cập nhật lúc", datetime.now().strftime("%H:%M %d/%m"))

                # Phân loại màu (đã fix type)
                if aqi <= 50:
                    st.success("🟢 Tốt - Có thể ra ngoài bình thường")
                elif aqi <= 100:
                    st.warning("🟡 Trung bình - Nên đeo khẩu trang nếu nhạy cảm")
                else:
                    st.error("🔴 Không tốt - Hạn chế ra ngoài, đeo khẩu trang N95")
                
                st.info("💡 AirGuard AI khuyên: Nếu AQI > 100, nên ở trong nhà hoặc đeo khẩu trang khi di chuyển.")
                
            else:
                st.error("❌ Token không hợp lệ hoặc API trả về lỗi.")
        except Exception as e:
            st.error(f"❌ Không kết nối được: {str(e)}")
            st.info("💡 Thử refresh trang hoặc chờ 10 giây rồi nhấn nút lại.")

st.markdown("---")
st.caption("AirGuard AI • Thử thách AI Driven Innovation 2026")
st.caption("Token đã được tích hợp sẵn")