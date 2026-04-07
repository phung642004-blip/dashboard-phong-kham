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
    
    # [CỘT 1] LỄ TÂN
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

    # [CỘT 2] BÁC SĨ GỌI KHÁM
    with col2:
        st.subheader("2. Gọi Khám")
        ds_cho = df[df['Trang_thai'] == 'Chờ khám']
        if not ds_cho.empty:
            lua_chon_bn = st.selectbox("Chọn bệnh nhân đang chờ:", ds_cho['STT'] + " - " + ds_cho['PID'] + " (" + ds_cho['Loai_sieu_am'] + ")")
            phong_kham = st.selectbox("Chọn phòng siêu âm:", ["Phòng B1040", "Phòng B1041"])
            
            if st.button("📢 Gọi Vào Phòng"):
                stt_duoc_goi = lua_chon_bn.split(" - ")[0]
                df.loc[(df['Trang_thai'] == 'Đang phục vụ') & (df['Phong'] == phong_kham), 'Trang_thai'] = 'Chờ trả kết quả'
                df.loc[df['STT'] == stt_duoc_goi, 'Trang_thai'] = 'Đang phục vụ'
                df.loc[df['STT'] == stt_duoc_goi, 'Phong'] = phong_kham
                
                st.session_state.danh_sach = df
                save_data(df) 
                st.rerun()
        else:
            st.info("Sảnh đang trống.")

    # [CỘT 3] XỬ LÝ TRONG PHÒNG KHÁM
    with col3:
        st.subheader("3. Đang Khám")
        
        def admin_phong_kham(ten_phong):
            st.markdown(f"**{ten_phong}**")
            bn_trong_phong = df[(df['Trang_thai'] == 'Đang phục vụ') & (df['Phong'] == ten_phong)]
            
            if not bn_trong_phong.empty:
                stt_dang_kham = bn_trong_phong.iloc[0]['STT']
                pid_dang_kham = bn_trong_phong.iloc[0]['PID']
                loai_sa_dang_kham = bn_trong_phong.iloc[0]['Loai_sieu_am']
                st.success(f"{stt_dang_kham} - {pid_dang_kham} ({loai_sa_dang_kham})")
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("⏩ Qua lượt", key=f"ql_{ten_phong}"):
                        df.loc[df['STT'] == stt_dang_kham, 'Trang_thai'] = 'Qua lượt'
                        st.session_state.danh_sach = df
                        save_data(df)
                        st.rerun()
                with c_btn2:
                    if st.button("✅ Trả KQ", key=f"tkq_{ten_phong}"):
                        df.loc[df['STT'] == stt_dang_kham, 'Trang_thai'] = 'Chờ trả kết quả'
                        st.session_state.danh_sach = df
                        save_data(df)
                        st.rerun()
            else:
                st.write("Phòng trống")
            st.divider()

        admin_phong_kham("Phòng B1040")
        admin_phong_kham("Phòng B1041")

    # [CỘT 4] KẾT THÚC QUY TRÌNH
    with col4:
        st.subheader("4. Quầy Trả KQ")
        ds_cho_kq = df[df['Trang_thai'] == 'Chờ trả kết quả']
        
        if not ds_cho_kq.empty:
            bn_hoan_thanh = st.selectbox("Chọn bệnh nhân phát kết quả:", ds_cho_kq['STT'] + " - " + ds_cho_kq['PID'])
            if st.button("🏁 Đã Nhận Kết Quả"):
                stt_ht = bn_hoan_thanh.split(" - ")[0]
                df.loc[df['STT'] == stt_ht, 'Trang_thai'] = 'Hoàn thành' 
                
                st.session_state.danh_sach = df
                save_data(df)
                st.rerun()
        else:
            st.info("Chưa có KQ.")

    st.divider()
    st.write("📊 DỮ LIỆU HIS TỔNG HỢP:")
    st.dataframe(st.session_state.danh_sach, use_container_width=True)
    
    # NÚT RESET DỮ LIỆU ĐƯỢC THÊM VÀO ĐÂY
    st.markdown("---")
    if st.button("🗑️ Xóa Toàn Bộ Dữ Liệu (Reset Ngày Mới)"):
        # Reset lại bộ nhớ
        st.session_state.danh_sach = pd.DataFrame(columns=['STT', 'PID', 'Loai_sieu_am', 'Trang_thai', 'Phong'])
        st.session_state.so_tiep_theo = 1
        # Xóa file lưu trữ
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        # Tải lại trang web
        st.rerun()

# ----------------- TẤT CẢ CODE CHO TAB HIỂN THỊ -----------------
with tab_hien_thi:
    df_hien_thi = st.session_state.danh_sach.copy() 
    
    st.markdown("<h2 style='text-align: center; color: #1E3A8A; background-color: #E0F2FE; padding: 10px; margin-bottom: 20px;'>PHÒNG KHÁM SẢN - DANH SÁCH CHỜ</h2>", unsafe_allow_html=True)
    
    df_hien_thi = df_hien_thi[df_hien_thi['Trang_thai'] != 'Hoàn thành']
    
    if df_hien_thi.empty:
        st.markdown("<h4 style='text-align: center; color: gray; margin-top: 50px;'>Hệ thống đã sẵn sàng. Vui lòng cấp số tại quầy Lễ tân.</h4>", unsafe_allow_html=True)
    else:
        df_hien_thi['PID_An'] = df_hien_thi['PID'].apply(mask_pid)
        df_hien_thi['Hien_thi'] = df_hien_thi['STT'] + ' - ' + df_hien_thi['PID_An'] + ' (' + df_hien_thi['Loai_sieu_am'] + ')'
        
        cho_kham = df_hien_thi[df_hien_thi['Trang_thai'] == 'Chờ khám']['Hien_thi'].tolist()
        cho_ket_qua = df_hien_thi[df_hien_thi['Trang_thai'] == 'Chờ trả kết quả']['Hien_thi'].tolist()
        qua_luot = df_hien_thi[df_hien_thi['Trang_thai'] == 'Qua lượt']['Hien_thi'].tolist()

        col_trai, col_phai = st.columns([7, 3])

        with col_trai:
            st.markdown("<h3 style='background-color: #1E40AF; color: white; padding: 10px; margin-bottom: 0px;'>ĐANG PHỤC VỤ >>> </h3>", unsafe_allow_html=True)
            
            c_p1, c_p2 = st.columns(2)
            
            def render_phong(ten_phong, col):
                with col:
                    st.markdown(f"<div style='background-color: #DBEAFE; padding: 8px; text-align: center; font-weight: bold; color: #1E3A8A; border: 1px solid #93C5FD;'>{ten_phong.upper()}</div>", unsafe_allow_html=True)
                    bn_phong = df_hien_thi[(df_hien_thi['Trang_thai'] == 'Đang phục vụ') & (df_hien_thi['Phong'] == ten_phong)]
                    if not bn_phong.empty:
                        for _, row in bn_phong.iterrows():
                            st.markdown(f"<div style='border: 3px solid #1E40AF; padding: 20px; text-align: center; background-color: white;'><h2 style='color: #B91C1C; margin: 0; font-size: 38px;'>{row['Hien_thi']}</h2></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='border: 2px dashed #9CA3AF; padding: 30px; text-align: center; background-color: #F9FAFB;'><h3 style='color: #9CA3AF; margin: 0;'>TRỐNG</h3></div>", unsafe_allow_html=True)
            
            render_phong("Phòng B1040", c_p1)
            render_phong("Phòng B1041", c_p2)
            
            st.markdown(f"<h4 style='background-color: #E5E7EB; padding: 5px; margin-top: 20px;'>KHÁCH HÀNG CHỜ ({len(cho_kham)})</h4>", unsafe_allow_html=True)
            if len(cho_kham) > 0:
                cols_cho = st.columns(3)
                for i, bn in enumerate(cho_kham):
                    with cols_cho[i % 3]: 
                        st.markdown(f"🔸 <span style='font-size: 22px; color: #4B5563; font-weight: bold;'>{bn}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='color: gray;'>Chưa có khách hàng chờ...</span>", unsafe_allow_html=True)

        with col_phai:
            st.markdown(f"<h4 style='background-color: #D1FAE5; color: #065F46; padding: 5px;'>CHỜ TRẢ KẾT QUẢ ({len(cho_ket_qua)})</h4>", unsafe_allow_html=True)
            for bn in cho_ket_qua:
                st.markdown(f"✔️ <span style='font-size: 20px; color: #047857;'>{bn}</span>", unsafe_allow_html=True)
                st.divider()
                
            st.markdown(f"<h4 style='background-color: #FEE2E2; color: #991B1B; padding: 5px; margin-top: 20px;'>QUA LƯỢT ({len(qua_luot)})</h4>", unsafe_allow_html=True)
            for bn in qua_luot:
                st.markdown(f"⚠️ <span style='font-size: 20px; color: #B91C1C; font-weight: bold;'>{bn}</span>", unsafe_allow_html=True)
                st.divider()
