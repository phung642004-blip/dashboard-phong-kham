import streamlit as st
import pandas as pd
import os

# Cấu hình trang web
st.set_page_config(layout="wide", page_title="Hệ Thống Bấm Số Khoa Sản Pro")

# Căn chỉnh toàn bộ phông chữ hệ thống
st.markdown("""
    <style>
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Times New Roman', Times, serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =======================================================
# HÀM BẢO MẬT & LƯU TRỮ DỮ LIỆU (DATABASE DẠNG CSV)
# =======================================================
DATA_FILE = "dulieu_benhnhan.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype=str)
        # Tự động nâng cấp dữ liệu cũ (nếu chưa có cột Loai_sieu_am)
        if 'Loai_sieu_am' not in df.columns:
            df['Loai_sieu_am'] = "2D" 
        return df
    else:
        return pd.DataFrame(columns=['STT', 'PID', 'Loai_sieu_am', 'Trang_thai', 'Phong'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def mask_pid(pid):
    pid = str(pid)
    if len(pid) <= 5: return "*****"
    start = (len(pid) - 5) // 2
    return pid[:start] + "*****" + pid[start+5:]

# =======================================================
# 1. KHỞI TẠO BỘ NHỚ
# =======================================================
if 'danh_sach' not in st.session_state:
    st.session_state.danh_sach = load_data()

if 'so_tiep_theo' not in st.session_state:
    if not st.session_state.danh_sach.empty:
        try:
            max_stt = max([int(x) for x in st.session_state.danh_sach['STT']])
            st.session_state.so_tiep_theo = max_stt + 1
        except:
            st.session_state.so_tiep_theo = 1
    else:
        st.session_state.so_tiep_theo = 1

# =======================================================
# 2. CHIA 2 MÀN HÌNH (TABS)
# =======================================================
tab_admin, tab_hien_thi = st.tabs(["⚙️ MÀN HÌNH ĐIỀU KHIỂN (Nhân viên)", "📺 MÀN HÌNH CHỜ (Dashboard)"])

# ----------------- TẤT CẢ CODE CHO TAB ADMIN -----------------
with tab_admin:
    st.header("Hệ Thống Quản Lý Luồng Bệnh Nhân")
    
    col1, col2, col3, col4 = st.columns(4)
    df = st.session_state.danh_sach
    
    # [CỘT 1] LỄ TÂN QUÉT MÃ VÀ CHỌN LOẠI SIÊU ÂM
    with col1:
        st.subheader("1. Lễ Tân")
        with st.form("form_nhan_benh", clear_on_submit=True):
            pid_input = st.text_input("Mã Bệnh Nhân (PID):")
            loai_sa_input = st.selectbox("Loại hình siêu âm:", ["2D", "4D"])
            submit_btn = st.form_submit_button("🖨️ Cấp Số", type="primary")
            
            if submit_btn and pid_input:
                stt_moi = f"{st.session_state.so_tiep_theo:03d}"
                new_row = pd.DataFrame({
                    'STT': [stt_moi], 
                    'PID': [pid_input], 
                    'Loai_sieu_am': [loai_sa_input],
                    'Trang_thai': ['Chờ khám'], 
                    'Phong': ['Đang chờ']
                })
                df = pd.concat([df, new_row], ignore_index=True)
                
                st.session_state.danh_sach = df
                save_data(df)
                st.session_state.so_tiep_theo += 1
                st.success(f"✅ Cấp số {stt_moi} ({loai_sa_input})")
                st.rerun()

    # [CỘT 2] BÁC SĨ GỌI KHÁM (PHÒNG B1040, B1041)
    with col2:
        st.subheader("2. Gọi Khám")
        ds_cho = df[df['Trang_thai'] == 'Chờ khám']
        if not ds_cho.empty:
            # Hiển thị thêm loại siêu âm để bác sĩ dễ gọi đúng người
            lua_chon_bn = st.selectbox("Chọn bệnh nhân đang chờ:", ds_cho['STT'] + " - " + ds_cho['PID'] + " (" + ds_cho['Loai_sieu_am'] + ")")
            phong_kham = st.selectbox("Chọn phòng siêu âm:", ["Phòng B1040", "Phòng B1041"])
            
            if st.button("📢 Gọi Vào Phòng"):
                stt_duoc_goi = lua_
