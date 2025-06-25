import os
import subprocess
import shutil

# vgmstream-cli.exe的相对路径
vgmstream_cli = os.path.join("vgmstream-win64", "vgmstream-cli.exe")

# 遍历当前目录下所有.wem文件
wem_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.lower().endswith(".wem"):
            wem_files.append(os.path.join(root, file))

for wem_file in wem_files:
    expect_wav_file = wem_file + ".wav"
    if os.path.exists(expect_wav_file):
        print(f"已存在: {expect_wav_file}")
        continue

    # 构造命令行参数
    cmd = [vgmstream_cli, wem_file]
    print(f"正在转换: {wem_file}")
    # 调用vgmstream-cli.exe，不显示子进程输出
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 将所有.wav文件移动到输出目录，重命名删除多余的.wem字符
output_root = "output"

for wem_file in wem_files:
    wav_file = wem_file + ".wav"
    if os.path.exists(wav_file):
        # 计算输出文件的新路径
        # 去掉前面的./
        rel_path = os.path.relpath(wem_file, ".")
        # 去掉.wem后缀
        rel_path = rel_path.replace(".wem", ".wav")

        output_wav_path = os.path.join(output_root, rel_path)
        output_dir = os.path.dirname(output_wav_path)
        os.makedirs(output_dir, exist_ok=True)
        # 复制并重命名
        if not os.path.exists(output_wav_path):
            shutil.copyfile(wav_file, output_wav_path)
        else:
            print(f"输出文件已存在: {output_wav_path}")
