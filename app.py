import streamlit as st
import yt_dlp
import os
import glob
import tempfile
from PIL import Image

# Dọn dẹp tất cả rác từ các lần tải trước để không trào bộ nhớ máy chủ
for f in glob.glob("*.mp4") + glob.glob("*.webm") + glob.glob("*.mkv") + glob.glob("*.jpg") + glob.glob("*.png") + glob.glob("*.webp") + glob.glob("*.txt"):
    try:
        # Giữ lại file requirements và packages
        if "requirements" not in f and "packages" not in f:
            os.remove(f)
    except Exception:
        pass

st.set_page_config(page_title="Công cụ tải đa nền tảng", page_icon="⬇️")
st.title("⬇️ Trình Tải Đa Nền Tảng (Bản Full & Bảo Mật)")

url = st.text_input("Dán đường dẫn vào đây (Hỗ trợ YouTube, Facebook, TikTok, Instagram...):")

# Hàm khởi tạo cookie ẩn để dùng chung cho cả lúc check thông tin và lúc tải
def lay_cookie_tam_thoi():
    if "YOUTUBE_COOKIES" in st.secrets:
        try:
            tep_tam = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8")
            tep_tam.write(st.secrets["YOUTUBE_COOKIES"])
            tep_tam.close()
            return tep_tam.name
        except Exception:
            return None
    return None

if url:
    duong_dan_cookie = lay_cookie_tam_thoi()
    
    with st.spinner("Đang phân tích dữ liệu, vui lòng chờ..."):
        ydl_opts_info = {'quiet': True, 'no_warnings': True}
        if duong_dan_cookie:
            ydl_opts_info['cookiefile'] = duong_dan_cookie
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                thong_tin = ydl.extract_info(url, download=False)
                loi = None
        except Exception as e:
            thong_tin = None
            loi = str(e)

    if loi:
        st.error("Không thể lấy thông tin. Hãy kiểm tra lại link hoặc cookie.")
    elif thong_tin:
        # Nhận diện loại nội dung
        loai_noi_dung = "Video"
        if thong_tin.get('_type') == 'playlist' or 'images' in thong_tin.get('title', '').lower():
            loai_noi_dung = "Hình ảnh / Slide"

        st.success(f"Đã nhận diện: {loai_noi_dung}")
        st.write(f"**Tiêu đề:** {thong_tin.get('title', 'Không có tiêu đề')}")

        # Lọc danh sách chất lượng
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
            with st.spinner("Hệ thống đang kéo tệp về và xử lý..."):
                if chat_luong_chon == "Mặc định (Tốt nhất có thể)":
                    lenh_chat_luong = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    h = chat_luong_chon.replace('p', '')
                    lenh_chat_luong = f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/best[height<={h}][ext=mp4]/best"

                ydl_opts_tai = {
                    'format': lenh_chat_luong,
                    'outtmpl': 'noidung_tai_ve_%(id)s.%(ext)s',
                    'quiet': True,
                    'merge_output_format': 'mp4'
                }
                
                if duong_dan_cookie:
                    ydl_opts_tai['cookiefile'] = duong_dan_cookie

                try:
                    with yt_dlp.YoutubeDL(ydl_opts_tai) as ydl_tai:
                        thong_tin_tai = ydl_tai.extract_info(url, download=True)
                        ten_tep = ydl_tai.prepare_filename(thong_tin_tai)
                        
                        if ten_tep.endswith('.webm') or ten_tep.endswith('.mkv'):
                            ten_tep = ten_tep.rsplit('.', 1)[0] + '.mp4'

                    loai_mime = "video/mp4"
                    
                    # Tự động ép ảnh sang định dạng WebP
                    if ten_tep.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        try:
                            anh = Image.open(ten_tep)
                            ten_tep_webp = ten_tep.rsplit('.', 1)[0] + '.webp'
                            anh.save(ten_tep_webp, 'webp')
                            os.remove(ten_tep)
                            ten_tep = ten_tep_webp
                            loai_mime = "image/webp"
                        except Exception:
                            loai_mime = "image/jpeg"

                    if os.path.exists(ten_tep):
                        with open(ten_tep, "rb") as tep_tin:
                            st.download_button(
                                label="✅ Bấm vào đây để lưu tệp về máy",
                                data=tep_tin,
                                file_name=ten_tep,
                                mime=loai_mime
                            )
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi tải dữ liệu: {e}")
                    
    # Tiêu hủy cookie ngay lập tức sau khi xong việc
    if duong_dan_cookie and os.path.exists(duong_dan_cookie):
        os.remove(duong_dan_cookie)
