import streamlit as st
import yt_dlp
import os
import glob

# Dọn dẹp tệp cũ để tránh đầy bộ nhớ máy chủ
for f in glob.glob("*.mp4") + glob.glob("*.webm") + glob.glob("*.mkv") + glob.glob("*.jpg") + glob.glob("*.png"):
    try:
        os.remove(f)
    except Exception:
        pass

st.set_page_config(page_title="Công cụ tải đa nền tảng", page_icon="⬇️")
st.title("⬇️ Công cụ tải Video/Ảnh đa nền tảng")
st.write("Hỗ trợ tải nội dung từ Facebook, TikTok, Instagram (Không hỗ trợ YouTube).")

url = st.text_input("Dán đường dẫn vào đây:")

@st.cache_data(show_spinner=False)
def phan_tich_thong_tin(link):
    ydl_opts_info = {'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            return ydl.extract_info(link, download=False), None
    except Exception as e:
        return None, str(e)

if url:
    if "youtube.com" in url or "youtu.be" in url:
        st.warning("Theo cấu hình hiện tại, tính năng tải từ YouTube đã được vô hiệu hóa để tránh các vấn đề liên quan đến cookie và chặn IP.")
    else:
        with st.spinner("Đang phân tích đường dẫn, vui lòng chờ trong giây lát..."):
            thong_tin, loi = phan_tich_thong_tin(url)

        if loi:
            st.error("Không thể lấy thông tin. Có thể đường dẫn không hợp lệ, nội dung ở chế độ riêng tư hoặc nền tảng đã thay đổi thuật toán.")
        elif thong_tin:
            loai_noi_dung = "Video"
            if thong_tin.get('_type') == 'playlist' or 'images' in thong_tin.get('title', '').lower():
                loai_noi_dung = "Hình ảnh / Slide"

            st.success(f"Đã nhận diện: {loai_noi_dung}")
            st.write(f"**Tiêu đề:** {thong_tin.get('title', 'Không có tiêu đề')}")

            danh_sach_chat_luong = []
            if 'formats' in thong_tin:
                for f in thong_tin['formats']:
                    chieu_cao = f.get('height')
                    if chieu_cao and f.get('vcodec') != 'none':
                        do_phan_giai = f"{chieu_cao}p"
                        if do_phan_giai not in danh_sach_chat_luong:
                            danh_sach_chat_luong.append(do_phan_giai)

            danh_sach_chat_luong.sort(key=lambda x: int(x.replace('p', '')), reverse=True)

            if not danh_sach_chat_luong:
                danh_sach_chat_luong = ["Mặc định (Tốt nhất có thể)"]

            chat_luong_chon = st.selectbox("Lựa chọn chất lượng tải xuống:", danh_sach_chat_luong)

            if st.button("Tiến hành tải xuống"):
                with st.spinner("Hệ thống đang xử lý tệp tin..."):
                    if chat_luong_chon == "Mặc định (Tốt nhất có thể)":
                        lenh_chat_luong = 'best'
                    else:
                        h = chat_luong_chon.replace('p', '')
                        lenh_chat_luong = f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best"

                    ydl_opts_tai = {
                        'format': lenh_chat_luong,
                        'outtmpl': 'noidung_tai_ve_%(id)s.%(ext)s',
                        'quiet': True,
                        'merge_output_format': 'mp4'
                    }

                    try:
                        with yt_dlp.YoutubeDL(ydl_opts_tai) as ydl_tai:
                            thong_tin_tai = ydl_tai.extract_info(url, download=True)
                            ten_tep = ydl_tai.prepare_filename(thong_tin_tai)
                            
                            if ten_tep.endswith('.webm') or ten_tep.endswith('.mkv'):
                                ten_tep = ten_tep.rsplit('.', 1)[0] + '.mp4'

                        if os.path.exists(ten_tep):
                            with open(ten_tep, "rb") as tep_tin:
                                st.download_button(
                                    label="✅ Bấm vào đây để lưu tệp về máy",
                                    data=tep_tin,
                                    file_name=ten_tep,
                                    mime="video/mp4" if loai_noi_dung == "Video" else "application/octet-stream"
                                )
                    except Exception as e:
                        st.error(f"Đã xảy ra lỗi trong quá trình tải dữ liệu: {e}")
