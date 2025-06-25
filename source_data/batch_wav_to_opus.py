import os
import subprocess
import shutil
import concurrent.futures

input_root = "output"

wav_files = []
for root, dirs, files in os.walk(input_root):
    for file in files:
        if file.lower().endswith(".wav"):
            wav_files.append(os.path.join(root, file))

output_root = "output_opus"


def convert_wav_to_ogg(wav_file):
    rel_path = wav_file.replace(".wav", ".ogg")
    rel_path = os.path.relpath(rel_path, input_root)
    expect_ogg_file = os.path.join(output_root, rel_path)
    if os.path.exists(expect_ogg_file):
        print(f"已存在: {expect_ogg_file}")
        return
    print(f"正在转换: {wav_file}")
    os.makedirs(os.path.dirname(expect_ogg_file), exist_ok=True)
    result = subprocess.run(
        [
            "ffmpeg",
            "-i",
            wav_file,
            "-c:a",
            "libopus",
            "-b:a",
            "96k",
            "-y",
            expect_ogg_file,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        print(f"转换失败: {wav_file}")


if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        executor.map(convert_wav_to_ogg, wav_files)
