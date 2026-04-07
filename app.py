import streamlit as st
import pandas as pd

# Cấu hình trang web
st.set_page_config(layout="wide", page_title="Hệ Thống Bấm Số Khoa Sản Pro")

# =======================================================
# HÀM BẢO MẬT: CHE 5 SỐ GIỮA CỦA MÃ PID
# =======================================================
def mask_pid(pid):
    pid = str(pid)
    if len(pid) <= 5:
        return "*****"
    start = (len(pid) - 5) // 2
    return pid[:start] + "*****" + pid[start+5:]

# =======================================================
# 1. KHỞI TẠO BỘ NHỚ
# =======================================================
if 'danh_sach' not in st.session_state:
    st.session_state.danh_sach = pd.DataFrame(columns=['STT', 'PID', 'Trang_thai', 'Phong'])
if 'so_tiep_theo' not in st.session_state:
    st.session_state.so_tiep_theo = 1

# =======================================================
# 2. CHIA 2 MÀN HÌNH (TABS)
# =======================================================
tab_admin, tab_hien_thi = st.tabs(["⚙️ MÀN HÌNH ĐIỀU KHIỂN (Nhân viên)", "📺 MÀN HÌNH CHỜ (Dashboard)"])

# ----------------- TẤT CẢ CODE CHO TAB ADMIN -----------------
with tab_admin:
    st.header("Hệ Thống Quản Lý Luồng Bệnh Nhân")
    
    col_letan, col_bacsi, col_xuly = st.columns(3)
    df = st.session_state.danh_sach
    
    # [CỘT 1] LỄ TÂN QUÉT MÃ
    with col_letan:
        st.subheader("1. Lễ Tân: Quét Mã Vạch")
        with st.form("form_nhan_benh", clear_on_submit=True):
            pid_input = st.text_input("Mã Bệnh Nhân (PID):", placeholder="Click vào đây và quét mã...")
            submit_btn = st.form_submit_button("🖨️ Tự Động Cấp Số", type="primary")
            
            if submit_btn and pid_input:
                stt_moi = f"{st.session_state.so_tiep_theo:03d}"
                new_row = pd.DataFrame({'STT': [stt_moi], 'PID': [pid_input], 'Trang_thai': ['Chờ khám'], 'Phong': ['Đang chờ']})
                st.session_state.danh_sach = pd.concat([df, new_row], ignore_index=True)
                st.session_state.so_tiep_theo += 1
                st.success(f"✅ Đã cấp số {stt_moi}")
                st.rerun()

    # [CỘT 2] BÁC SĨ GỌI KHÁM
    with col_bacsi:
        st.subheader("2. Bác Sĩ: Gọi Khám")
        ds_cho = df[df['Trang_thai'] == 'Chờ khám']
        
        if not ds_cho.empty:
            lua_chon_bn = st.selectbox("Chọn bệnh nhân đang chờ:", ds_cho['STT'] + " - " + ds_cho['PID'])
            phong_kham = st.selectbox("Chọn phòng siêu âm:", ["Phòng Siêu Âm 1", "Phòng Siêu Âm 2"])
            
            if st.button("📢 Gọi Vào Phòng"):
                stt_duoc_goi = lua_chon_bn.split(" - ")[0]
                df.loc[(df['Trang_thai'] == 'Đang phục vụ') & (df['Phong'] == phong_kham), 'Trang_thai'] = 'Chờ trả kết quả'
                df.loc[df['STT'] == stt_duoc_goi, 'Trang_thai'] = 'Đang phục vụ'
                df.loc[df['STT'] == stt_duoc_goi, 'Phong'] = phong_kham
                st.session_state.danh_sach = df
                st.rerun()
        else:
            st.info("Không có bệnh nhân chờ.")

    # [CỘT 3] XỬ LÝ QUA LƯỢT / HOÀN THÀNH
    with col_xuly:
        st.subheader("3. Cập nhật Trạng thái")
        ds_dang_kham = df[df['Trang_thai'] == 'Đang phục vụ']
        
        if not ds_dang_kham.empty:
            lua_chon_xuly = st.selectbox("Chọn bệnh nhân trên màn hình:", ds_dang_kham['STT'] + " - " + ds_dang_kham['PID'] + " (" + ds_dang_kham['Phong'] + ")")
            stt_xuly = lua_chon_xuly.split(" - ")[0]
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("⏩ Báo Qua Lượt"):
                    df.loc[df['STT'] == stt_xuly, 'Trang_thai'] = 'Qua lượt'
                    st.session_state.danh_sach = df
                    st.rerun()
            with col_btn2:
                if st.button("✅ Trả Kết Quả"):
                    df.loc[df['STT'] == stt_xuly, 'Trang_thai'] = 'Chờ trả kết quả'
                    st.session_state.danh_sach = df
                    st.rerun()
        else:
            st.info("Các phòng siêu âm đang trống.")

    st.divider()
    st.write("📊 BẢNG DỮ LIỆU TỔNG HỢP (Nhân viên y tế xem bản gốc đầy đủ):")
    st.dataframe(st.session_state.danh_sach, use_container_width=True)

# ----------------- TẤT CẢ CODE CHO TAB HIỂN THỊ -----------------
with tab_hien_thi:
    df_hien_thi = st.session_state.danh_sach.copy() 
    
    st.markdown("<h2 style='text-align: center; color: #1E3A8A; background-color: #E0F2FE; padding: 10px; margin-bottom: 20px;'>PHÒNG KHÁM SẢN - DANH SÁCH CHỜ</h2>", unsafe_allow_html=True)
    
    if df_hien_thi.empty:
        st.markdown("<h4 style='text-align: center; color: gray; margin-top: 50px;'>Hệ thống đã sẵn sàng. Vui lòng cấp số tại quầy Lễ tân.</h4>", unsafe_allow_html=True)
    else:
        df_hien_thi['PID_An'] = df_hien_thi['PID'].apply(mask_pid)
        df_hien_thi['Hien_thi'] = df_hien_thi['STT'] + ' - ' + df_hien_thi['PID_An']
        
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
                            st.markdown(f"<div style='border: 3px solid #1E40AF; padding: 20px; text-align: center; background-color: white;'><h2 style='color: #B91C1C; margin: 0; font-size: 45px;'>{row['Hien_thi']}</h2></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='border: 2px dashed #9CA3AF; padding: 30px; text-align: center; background-color: #F9FAFB;'><h3 style='color: #9CA3AF; margin: 0;'>TRỐNG</h3></div>", unsafe_allow_html=True)
            
            render_phong("Phòng Siêu Âm 1", c_p1)
            render_phong("Phòng Siêu Âm 2", c_p2)
            
            # DANH SÁCH CHỜ
            st.markdown(f"<h4 style='background-color: #E5E7EB; padding: 5px; margin-top: 20px;'>KHÁCH HÀNG CHỜ ({len(cho_kham)})</h4>", unsafe_allow_html=True)
            if len(cho_kham) > 0:
                cols_cho = st.columns(3)
                for i, bn in enumerate(cho_kham):
                    with cols_cho[i % 3]: 
                        st.markdown(f"🔸 <span style='font-size: 22px; color: #4B5563; font-weight: bold;'>{bn}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='color: gray;'>Chưa có khách hàng chờ...</span>", unsafe_allow_html=True)

        with col_phai:
            # CHỜ TRẢ KẾT QUẢ
            st.markdown(f"<h4 style='background-color: #D1FAE5; color: #065F46; padding: 5px;'>CHỜ TRẢ KẾT QUẢ ({len(cho_ket_qua)})</h4>", unsafe_allow_html=True)
            for bn in cho_ket_qua:
                st.markdown(f"✔️ <span style='font-size: 20px; color: #047857;'>{bn}</span>", unsafe_allow_html=True)
                st.divider()
                
            # QUA LƯỢT (Đã bỏ gạch ngang chữ và đổi icon nhẹ nhàng hơn)
            st.markdown(f"<h4 style='background-color: #FEE2E2; color: #991B1B; padding: 5px; margin-top: 20px;'>QUA LƯỢT ({len(qua_luot)})</h4>", unsafe_allow_html=True)
            for bn in qua_luot:
                st.markdown(f"⚠️ <span style='font-size: 20px; color: #B91C1C; font-weight: bold;'>{bn}</span>", unsafe_allow_html=True)
                st.divider()
                