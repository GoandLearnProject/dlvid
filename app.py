import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Trình Tải Video Public", page_icon="📥", layout="centered")

# --- HÀM NHẬN DIỆN NỀN TẢNG ---
def nhan_dien_nen_tang(url):
    if "facebook.com" in url or "fb.watch" in url: return "Facebook"
    if "tiktok.com" in url: return "TikTok"
    if "instagram.com" in url: return "Instagram"
    if "youtube.com" in url or "youtu.be" in url: return "YouTube"
    return "Nền tảng khác"

# --- GIAO DIỆN CHÍNH ---
st.title("📥 Trình Tải Video Đa Nền Tảng")
st.markdown("Hỗ trợ tải: **YouTube, TikTok, Facebook, Instagram**")

url = st.text_input("Dán link video vào đây:")

if url:
    nen_tang = nhan_dien_nen_tang(url)
    st.info(f"🔍 Hệ thống nhận diện: **{nen_tang}**")

    # Sử dụng Session State để không phải tải lại thông tin mỗi khi chọn chất lượng
    if "current_url" not in st.session_state or st.session_state.current_url != url:
        st.session_state.current_url = url
        st.session_state.info = None
        
        with st.spinner("Đang phân tích link và lấy các độ phân giải..."):
            try:
                ydl_opts_info = {'quiet': True, 'no_warnings': True, 'extractor_args': {'youtube': ['player_client=android,ios,web']}}
                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                    st.session_state.info = ydl.extract_info(url, download=False)
            except Exception as e:
                st.error(f"❌ Lỗi khi phân tích link: {e}")

    # Nếu đã lấy được thông tin
    if st.session_state.info:
        info = st.session_state.info
        formats = info.get('formats', [])
        title = info.get('title', 'video_tai_ve')

        # Lọc danh sách độ phân giải
        danh_sach_res = []
        for f in formats:
            if f.get('height') and f.get('vcodec') != 'none':
                res = f"{f['height']}p"
                if res not in danh_sach_res:
                    danh_sach_res.append(res)
        
        # Sắp xếp từ cao xuống thấp
        danh_sach_res.sort(key=lambda x: int(x.replace('p', '')), reverse=True)

        if danh_sach_res:
            selected_res = st.selectbox("Tùy chọn chất lượng video:", danh_sach_res)
            
            # Nút xử lý
            if st.button("🚀 Bắt đầu xử lý (Ghép hình & tiếng)"):
                h = selected_res.replace('p', '')
                out_filename = "temp_video.mp4"
                
                # Cấu hình tải
                ydl_opts_dl = {
                    'format': f'bestvideo[height<={h}]+bestaudio/best[height<={h}]',
                    'outtmpl': out_filename,
                    'merge_output_format': 'mp4',
                    'quiet': False,
                    'extractor_args': {'youtube': ['player_client=android,ios,web']},
                    'nocheckcertificate': True
                }
                
                with st.spinner(f"Đang tải và ghép nối video ở chất lượng {selected_res}. Vui lòng không đóng trang..."):
                    try:
                        # Tải video về máy chủ
                        with yt_dlp.YoutubeDL(ydl_opts_dl) as ydl:
                            ydl.download([url])
                        
                        # Đọc file lên RAM và hiển thị nút tải về máy tính/điện thoại
                        if os.path.exists(out_filename):
                            with open(out_filename, "rb") as file:
                                video_bytes = file.read()
                            
                            st.success("✅ Xử lý hoàn tất!")
                            st.download_button(
                                label="⬇️ NHẤN VÀO ĐÂY ĐỂ LƯU VỀ MÁY ⬇️",
                                data=video_bytes,
                                file_name=f"{title}_{selected_res}.mp4",
                                mime="video/mp4"
                            )
                            # Xóa file rác trên máy chủ để tránh đầy bộ nhớ
                            os.remove(out_filename)
                            
                    except Exception as e:
                        st.error(f"❌ Lỗi tải video: {e}")
        else:
            st.warning("Không tìm thấy lựa chọn độ phân giải cụ thể. Sẽ tải bản mặc định tốt nhất.")
            if st.button("🚀 Tải bản mặc định"):
                with st.spinner("Đang xử lý tải video..."):
                    ydl_opts_dl = {'format': 'best', 'outtmpl': 'temp_video_default.mp4'}
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts_dl) as ydl:
                            ydl.download([url])
                        
                        if os.path.exists('temp_video_default.mp4'):
                            with open('temp_video_default.mp4', "rb") as file:
                                video_bytes = file.read()
                            st.success("✅ Xử lý hoàn tất!")
                            st.download_button(
                                label="⬇️ LƯU VIDEO VỀ MÁY ⬇️",
                                data=video_bytes,
                                file_name=f"{title}.mp4",
                                mime="video/mp4"
                            )
                            os.remove('temp_video_default.mp4')
                    except Exception as e:
                        st.error(f"❌ Lỗi tải video: {e}")
