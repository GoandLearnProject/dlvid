import streamlit as st
import yt_dlp
import os
import re

# Lấy mật khẩu từ Secrets của Streamlit hoặc mặc định là '123'
PASSWORD = st.secrets.get("APP_PASSWORD", "123")

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        col1, col2 = st.columns([3, 1])
        with col1:
            pwd = st.text_input("Nhập mã truy cập:", type="password")
        if pwd == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        elif pwd:
            st.error("Mã không đúng!")
        return False
    return True

def main():
    st.set_page_config(page_title="Video Downloader", icon="📥")
    if not check_password(): return

    st.title("📥 Multi-Platform Downloader")
    url = st.text_input("Dán link vào đây:")

    if url:
        try:
            with st.spinner("Đang kiểm tra link..."):
                ydl_opts = {'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    formats = info.get('formats', [])
                    title = info.get('title', 'video_file')

                res_list = sorted(list(set(
                    f"{f['height']}p" for f in formats if f.get('height') and f.get('vcodec') != 'none'
                )), key=lambda x: int(x.replace('p', '')), reverse=True)

                if res_list:
                    selected_res = st.selectbox("Chọn chất lượng:", res_list)
                    if st.button("Xử lý và Tải xuống"):
                        h = selected_res.replace('p', '')
                        out_file = f"downloaded_video.mp4"
                        
                        final_opts = {
                            'format': f'bestvideo[height<={h}]+bestaudio/best[height<={h}]',
                            'outtmpl': out_file,
                            'merge_output_format': 'mp4',
                        }
                        
                        with st.spinner("Đang tải và ghép nhạc (vui lòng đợi)..."):
                            with yt_dlp.YoutubeDL(final_opts) as ydl:
                                ydl.download([url])
                            
                            with open(out_file, "rb") as f:
                                st.download_button(f"📥 Lưu {selected_res} về máy", f, f"{title}.mp4")
                            os.remove(out_file)
        except Exception as e:
            st.error(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
