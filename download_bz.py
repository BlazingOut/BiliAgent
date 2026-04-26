import yt_dlp
import os
import sys

from faster_whisper import WhisperModel

# 自动定位当前 Conda 环境中的 library/bin 路径
if sys.platform == 'win32':
    # 假设你的环境路径里包含 library/bin
    conda_env_path = os.environ.get('CONDA_PREFIX')
    if conda_env_path:
        cuda_bin_path = os.path.join(conda_env_path, 'Library', 'bin')
        if os.path.exists(cuda_bin_path):
            os.add_dll_directory(cuda_bin_path)
            print(f"✅ 已成功加载 CUDA DLL 路径: {cuda_bin_path}")


def get_meta(info):
    # 提取我们关心的核心字段
    metadata = {
        "title": info.get('title'),  # 视频标题
        "author": info.get('uploader'),  # UP 主名字
        "author_id": info.get('uploader_id'),  # UP 主的 UID
        "description": info.get('description'),  # 视频简介
        "tags": info.get('tags', []),  # UP 主打的关键词标签 (List)
        "category": info.get('categories', []),  # B站的分区 (List，如 ['知识'])
        "view_count": info.get('view_count'),  # 播放量
        "duration": info.get('duration'),  # 视频时长（秒）
        "upload_date": info.get('upload_date'),  # 上传日期 (YYYYMMDD)
    }

    return metadata


def download_bilibili_audio(bvid: str, output_dir: str = "./audio"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    url = f"https://www.bilibili.com/video/{bvid}"

    # 核心修改在这里 👇
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'quiet': False,

        # 🌟 破局关键：让 yt-dlp 自动读取本地浏览器的 Cookie
        # 假设你平时用 Chrome 登录 B 站，就写 'chrome'。
        # 如果是 Edge，就改成 ('edge',)；如果是 Safari，就改成 ('safari',)
        # 'cookiesfrombrowser': ('chrome',),
        'cookiefile': 'cookies/www.bilibili.com_cookies.txt',
        # 1. 忽略 SSL 证书校验（专治各种梯子/代理导致的网络劫持报错）
        'nocheckcertificate': True,

        # 2. 补全防盗链请求头（告诉 B 站 CDN：我是在你的官网上看视频的，别掐我线）
        'http_headers': {
            'Referer': 'https://www.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
    }

    print(f"正在抓取音频: {url} ...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        meta_data = get_meta(info)
        audio_path = f"{output_dir}/{info['id']}.mp3"
        print(f"音频下载完成: {audio_path}")
    # 保存对应的meta信息

    return meta_data, audio_path

def audio_to_text(audio_path: str,context_prompt: str, language: str='zh') -> str:
    print("正在加载 Whisper 模型...")

    # 🌟 修复 1：将模型从 base 升级为 small
    # 注意：首次运行 small 会自动下载大概 400MB 的模型文件
    model_size = "small"

    model = WhisperModel(model_size, device="cuda", compute_type="float16")

    print(f"开始转录音频: {audio_path} ...")

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        language=language,
        initial_prompt=context_prompt,  # 塞小抄
        condition_on_previous_text=False  # 防止模型陷入复读机死循环
    )

    full_text = ""
    for segment in segments:
        full_text += segment.text + " "

    print("✅ 转录完成！")
    return full_text

# 测试运行
# 请确保你在代码里指定的浏览器（如 Chrome）中，已经打开并登录了 Bilibili！
if __name__ == "__main__":
    import json
    meta_data, audio_file = download_bilibili_audio("BV1P9oYByEy8")
    print(json.dumps(meta_data, indent=4))


    # audio_text = audio_to_text("audio/.mp3")
    # output_dir = "./text/BV1zFouBYEZR.txt"
    # with open(output_dir, "w") as f:
    #     f.write(audio_text)
    # print(audio_text[:400])
