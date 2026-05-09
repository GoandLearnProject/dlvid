import streamlit as st
import yt_dlp
import os
import re
import shutil

# Cấu hình bảo mật đơn giản
PASSWORD = "admin"

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        pwd = st.text_input("Nhập mật khẩu truy cập:", type="password")
        if pwd == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        elif pwd:
            st.error("Sai mật khẩu!")
        return False
    return True

def get_info(url):
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def main():
    st.set_page_config(page_title="Multi-Downloader Pro", layout="wide")
    
    if not check_password():
        return

    st.title("🚀 Universal Video Downloader")
    url = st.text_input("Dán đường dẫn (YouTube, TikTok, FB, Insta...):")

    if url:
        try:
            with st.spinner("Đang phân tích dữ liệu..."):
                info = get_info(url)
                formats = info.get('formats', [])
                title = info.get('title', 'video')
                
                # Phân loại nền tảng để hiển thị
                host = re.search(r"//(?:www\.)?([^/]+)", url).group(1)
                st.info(f"Nguồn: {host} | Tiêu đề: {title}")

                # Lọc độ phân giải
                res_list = sorted(list(set(
                    f"{f['height']}p" for f in formats if f.get('height') and f.get('vcodec') != 'none'
                )), key=lambda x: int(x.replace('p', '')), reverse=True)

                if res_list:
                    selected_res = st.selectbox("Chọn chất lượng video:", res_list)
                    h = selected_res.replace('p', '')
                    
                    if st.button("Bắt đầu xử lý và Tải về"):
                        output_fn = f"{title}_{selected_res}.mp4"
                        ydl_final_opts = {
                            'format': f'bestvideo[height<={h}]+bestaudio/best[height<={h}]',
                            'outtmpl': output_fn,
                            'merge_output_format': 'mp4',
                            'quiet': False
                        }
                        
                        with st.spinner("Máy chủ đang tải và ghép tệp (có thể mất vài phút)..."):
                            with yt_dlp.YoutubeDL(ydl_final_opts) as ydl:
                                ydl.download([url])
                            
                            if os.path.exists(output_fn):
                                with open(output_fn, "rb") as f:
                                    st.download_button(
                                        label="📥 Nhấn vào đây để lưu về máy",
                                        data=f,
                                        file_name=output_fn,
                                        mime="video/mp4"
                                    )
                                os.remove(output_fn)
                else:
                    if st.button("Tải bản mặc định (Best)"):
                        with st.spinner("Đang xử lý..."):
                            with yt_dlp.YoutubeDL({'outtmpl': 'video.mp4', 'format': 'best'}) as ydl:
                                ydl.download([url])
                            with open("video.mp4", "rb") as f:
                                st.download_button("📥 Tải về máy", f, "video.mp4")
                            os.remove("video.mp4")

        except Exception as e:
            st.error(f"Lỗi: {str(e)}")

if __name__ == "__main__":
    main()
