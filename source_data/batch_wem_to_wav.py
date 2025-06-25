import os
import subprocess
import shutil
import concurrent.futures

# vgmstream-cli.exe的相对路径
vgmstream_cli = os.path.join("vgmstream-win64", "vgmstream-cli.exe")

input_root = "raw"
output_root = "output"


def convert_wem_to_wav(wem_file):
    expect_wav_file = wem_file + ".wav"
    if not os.path.exists(expect_wav_file):
        # 如果文件不存在，则转换
        # 构造命令行参数
        cmd = [vgmstream_cli, wem_file]
        print(f"正在转换: {wem_file}")
        # 调用vgmstream-cli.exe，不显示子进程输出
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(expect_wav_file):
        # 计算输出文件的新路径
        # 去掉前面的./
        rel_path = os.path.relpath(wem_file, input_root)
        # 去掉.wem后缀
        rel_path = rel_path.replace(".wem", ".wav")

        output_wav_path = os.path.join(output_root, rel_path)
        output_dir = os.path.dirname(output_wav_path)
        os.makedirs(output_dir, exist_ok=True)
        # 复制并重命名
        if not os.path.exists(output_wav_path):
            shutil.copyfile(expect_wav_file, output_wav_path)
        else:
            print(f"输出文件已存在: {output_wav_path}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # 遍历当前目录下所有.wem文件
    wem_files = []
    for root, dirs, files in os.walk(input_root):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(".wem"):
                wem_files.append(file_path)

    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        executor.map(convert_wem_to_wav, wem_files)


if __name__ == "__main__":
    main()
