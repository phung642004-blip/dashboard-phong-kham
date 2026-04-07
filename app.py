import streamlit as st
import pandas as pd
import os

# Cấu hình trang web
st.set_page_config(layout="wide", page_title="Hệ Thống Bấm Số Khoa Sản Pro")

# Căn chỉnh phông chữ
st.markdown("""
    <style>
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Times New Roman', Times, serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =======================================================
# HÀM BẢO MẬT & LƯU TRỮ DỮ LIỆU
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
    
    col_letan, col_bacsi, col_trakq = st.columns([1, 2, 1])
    df = st.session_state.danh_sach
    
    # [CỘT 1] LỄ TÂN
    with col_letan:
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
                st.rerun()

    # [CỘT 2] BÁC SĨ TỰ GỌI KHÁM TRỰC TIẾP TẠI PHÒNG
    with col_bacsi:
        st.subheader("2. Bác Sĩ Các Phòng Gọi Khám")
        c_p1, c_p2 = st.columns(2)
        
        def render_room_control(ten_phong, col_container):
            with col_container:
                st.markdown(f"📍 **{ten_phong}**")
                
                # Phân đoạn 1: Thông tin người đang khám & Nút xử lý
                bn_dang_kham = df[(df['Trang_thai'] == 'Đang phục vụ') & (df['Phong'] == ten_phong)]
                if not bn_dang_kham.empty:
                    info = bn_dang_kham.iloc[0]
                    st.success(f"Đang siêu âm:\n\n**{info['STT']} - {info['PID']} ({info['Loai_sieu_am']})**")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("⏩ Qua lượt", key=f"q_{ten_phong}"):
                            df.loc[df['STT'] == info['STT'], 'Trang_thai'] = 'Qua lượt'
                            save_data(df); st.rerun()
                    with c2:
                        if st.button("✅ Trả KQ", key=f"k_{ten_phong}"):
                            df.loc[df['STT'] == info['STT'], 'Trang_thai'] = 'Chờ trả kết quả'
                            save_data(df); st.rerun()
                else: 
                    st.info("Phòng đang trống")
                
                st.write("---")
                
                # Phân đoạn 2: Danh sách chờ để gọi người mới
                ds_cho = df[df['Trang_thai'].isin(['Chờ khám', 'Qua lượt'])].copy()
                if not ds_cho.empty:
                    # Rút gọn nhãn: Xóa chữ [Chờ khám], chỉ hiện thị STT - PID. Nếu qua lượt thì thêm cái cờ cảnh báo nhỏ.
                    ds_cho['Nhan_hien_thi'] = ds_cho['STT'] + " - " + ds_cho['PID'] + " (" + ds_cho['Loai_sieu_am'] + ")"
                    ds_cho.loc[ds_cho['Trang_thai'] == 'Qua lượt', 'Nhan_hien_thi'] = "⚠️ " + ds_cho['Nhan_hien_thi']
                    
                    bn_chon = st.selectbox("Chọn người tiếp theo:", ds_cho['Nhan_hien_thi'], key=f"sel_{ten_phong}")
                    
                    if st.button(f"📢 Gọi vào {ten_phong}", key=f"call_{ten_phong}"):
                        # Trích xuất số thứ tự an toàn (cắt bỏ icon cảnh báo nếu có)
                        stt_chon = bn_chon.replace("⚠️ ", "").split(" - ")[0]
                        
                        df.loc[(df['Trang_thai'] == 'Đang phục vụ') & (df['Phong'] == ten_phong), 'Trang_thai'] = 'Chờ trả kết quả'
                        df.loc[df['STT'] == stt_chon, 'Trang_thai'] = 'Đang phục vụ'
                        df.loc[df['STT'] == stt_chon, 'Phong'] = ten_phong
                        
                        st.session_state.danh_sach = df
                        save_data(df)
                        st.rerun()
                else:
                    st.write("*Không có bệnh nhân chờ*")
                
                st.markdown("<div style='border-right: 2px solid #E5E7EB; height: 100%;'></div>", unsafe_allow_html=True)

        render_room_control("Phòng B1040", c_p1)
        render_room_control("Phòng B1041", c_p2)

    # [CỘT 3] HOÀN TẤT
    with col_trakq:
        st.subheader("3. Quầy Trả KQ")
        ds_kq = df[df['Trang_thai'] == 'Chờ trả kết quả']
        if not ds_kq.empty:
            bn_done = st.selectbox("BN nhận kết quả:", ds_kq['STT'] + " - " + ds_kq['PID'])
            if st.button("🏁 Đã Nhận KQ"):
                df.loc[df['STT'] == bn_done.split(" - ")[0], 'Trang_thai'] = 'Hoàn thành'
                save_data(df); st.rerun()
        else:
            st.info("Chưa có KQ.")

    st.divider()
    if st.button("🗑️ Reset Dữ Liệu Ngày Mới"):
        if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
        st.session_state.clear(); st.rerun()

    st.write("📊 DỮ LIỆU HIS TỔNG HỢP:")
    st.dataframe(st.session_state.danh_sach, use_container_width=True)

# ----------------- TẤT CẢ CODE CHO TAB HIỂN THỊ (BẢO MẬT) -----------------
with tab_hien_thi:
    df_view = st.session_state.danh_sach.copy()
    df_view = df_view[df_view['Trang_thai'] != 'Hoàn thành']
    
    st.markdown("<h2 style='text-align: center; color: #1E3A8A; background-color: #E0F2FE; padding: 10px;'>PHÒNG KHÁM SẢN - DANH SÁCH CHỜ</h2>", unsafe_allow_html=True)
    
    if not df_view.empty:
        df_view['PID_An'] = df_view['PID'].apply(mask_pid)
        df_view['Hien_thi'] = df_view['STT'] + ' - ' + df_view['PID_An']
        
        col_L, col_R = st.columns([7, 3])
        with col_L:
            st.markdown("<h3 style='background-color: #1E40AF; color: white; padding: 10px;'>ĐANG PHỤC VỤ >>> </h3>", unsafe_allow_html=True)
            p1, p2 = st.columns(2)
            for p, name in zip([p1, p2], ["Phòng B1040", "Phòng B1041"]):
                with p:
                    st.markdown(f"<div style='text-align: center; font-weight: bold; color: #1E3A8A;'>{name}</div>", unsafe_allow_html=True)
                    row = df_view[(df_view['Trang_thai'] == 'Đang phục vụ') & (df_view['Phong'] == name)]
                    if not row.empty:
                        st.markdown(f"<div style='border: 3px solid #1E40AF; padding: 15px; text-align: center;'><h2 style='color: #B91C1C; margin: 0;'>{row.iloc[0]['Hien_thi']}</h2></div>", unsafe_allow_html=True)
                    else: st.markdown("<div style='border: 1px dashed gray; padding: 25px; text-align: center; color: gray;'>TRỐNG</div>", unsafe_allow_html=True)
            
            # Khách hàng chờ
            cho = df_view[df_view['Trang_thai'] == 'Chờ khám']['Hien_thi'].tolist()
            st.markdown(f"<h4 style='background-color: #E5E7EB; padding: 5px; margin-top: 15px;'>KHÁCH HÀNG CHỜ ({len(cho)})</h4>", unsafe_allow_html=True)
            c_cho = st.columns(3)
            for i, bn in enumerate(cho):
                with c_cho[i%3]: st.markdown(f"🔸 **{bn}**")

        with col_R:
            # Chờ kết quả
            tkq = df_view[df_view['Trang_thai'] == 'Chờ trả kết quả']['Hien_thi'].tolist()
            st.markdown(f"<h4 style='background-color: #D1FAE5; padding: 5px;'>CHỜ TRẢ KQ ({len(tkq)})</h4>", unsafe_allow_html=True)
            for bn in tkq: st.write(f"✔️ {bn}")
            
            # Qua lượt
            ql = df_view[df_view['Trang_thai'] == 'Qua lượt']['Hien_thi'].tolist()
            st.markdown(f"<h4 style='background-color: #FEE2E2; padding: 5px; margin-top: 15px;'>QUA LƯỢT ({len(ql)})</h4>", unsafe_allow_html=True)
            for bn in ql: st.write(f"⚠️ **{bn}**")
