import os
import json
import csv


script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def main():
    input_root = "output_opus"
    output_root = "../public"

    # 加载名称匹配表
    name_match_table_name = "voice_bank_name.json"
    with open(name_match_table_name, "r", encoding="utf-8") as f:
        name_match_table = json.load(f)

    # 生成分类表
    categories = []
    for dir_name in os.listdir(input_root):
        if not os.path.isdir(os.path.join(input_root, dir_name)):
            continue

        label = name_match_table.get(dir_name, dir_name.replace("_VO", ""))
        categories.append(
            {
                "label": label,
                "value": dir_name,
            }
        )

    with open(os.path.join(output_root, "categories.json"), "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

    # 加载内容匹配表
    match_table_name = "voice_content_match_table.csv"
    match_table_path = match_table_name
    content_match_table = {}
    with open(match_table_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            content_match_table[str(row[0])] = row[1]

    # 生成每个分类的音效表
    for category in categories:
        category_path = os.path.join(input_root, category["value"])

        voice_list = []
        for file_name in os.listdir(category_path):
            if not file_name.endswith(".ogg"):
                continue

            id_str = file_name.replace(".ogg", "")
            voice_list.append(
                {
                    "id": id_str,
                    "content": content_match_table.get(id_str, ""),
                    "file": file_name,
                }
            )

        with open(
            os.path.join(output_root, f"{category["value"]}.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(voice_list, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
