import json
import os
import sys
from collections import defaultdict

def load_json(file_path):
    """加载 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_file(file_path, content):
    """写入文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def process_xaml_template(template, replacements):
    """处理 XAML 模板，替换相关内容"""
    for key, value in replacements.items():
        template = template.replace(f"[{key}]", value)
    return template

def process_data(packages_data, template_1, template_2, output_dir):
    """根据数据生成 xaml 文件并替换内容"""
    distributions = defaultdict(list)

    # 筛选符合条件的数据
    filtered_data = [
        item for item in packages_data
        if item.get("directly_downloadable") and item.get("free_use_in_production")
        and item.get("major_version") != 6
    ]

    # 遍历数据生成 xaml 文件
    for item in filtered_data:
        distribution = item["distribution"]
        operating_system = item["operating_system"]
        architecture = item["architecture"]
        major_version = item["major_version"]
        package_type = item["package_type"]
        javafx_bundled = item["javafx_bundled"]
        java_version = item["java_version"]
        archive_type = item["archive_type"]
        filename = item["filename"]
        pkg_download_url = item["links"]["pkg_download_redirect"]
        pkg_info_url = item["links"]["pkg_info_uri"]

        # 创建分发路径
        dist_path = os.path.join(output_dir, distribution)
        os.makedirs(dist_path, exist_ok=True)

        # 生成模板替换内容
        template = template_1
        replacements = {
            "title": "选择系统类型和系统架构",
            "page-number": "1/6",
            "page": f"{distribution}/{distribution}.xaml",
            "xaml": "json",
            "choose": generate_system_arch_content(filtered_data),
            "next_page-url": f"https://baidu.com/{distribution}/{distribution}.json"
        }

        # 生成系统架构的选择
        xaml_content = process_xaml_template(template, replacements)
        write_file(os.path.join(dist_path, f"{distribution}.xaml"), xaml_content)

        # 为系统架构-版本进一步生成 XAML 文件
        os_arch = f"{operating_system}-{architecture}"
        os_arch_path = os.path.join(dist_path, os_arch)
        os.makedirs(os_arch_path, exist_ok=True)
        
        template = template_1
        replacements.update({
            "title": "选择 Java 大版本",
            "page-number": "2/6",
            "page": f"{distribution}/{os_arch}/{os_arch}.xaml",
            "choose": generate_version_content(filtered_data),
            "next_page-url": f"https://baidu.com/{distribution}/{os_arch}/{os_arch}.json"
        })
        xaml_content = process_xaml_template(template, replacements)
        write_file(os.path.join(os_arch_path, f"{os_arch}.xaml"), xaml_content)

        # 为版本生成 XAML 文件
        pkg = package_type + ("fx" if javafx_bundled else "")
        pkg_path = os.path.join(os_arch_path, pkg)
        os.makedirs(pkg_path, exist_ok=True)
        
        template = template_1
        replacements.update({
            "title": "选择包类型",
            "page-number": "3/6",
            "page": f"{distribution}/{os_arch}/{pkg}/{pkg}.xaml",
            "choose": generate_pkg_content(filtered_data, javafx_bundled),
            "next_page-url": f"https://baidu.com/{distribution}/{os_arch}/{pkg}/{pkg}.json"
        })
        xaml_content = process_xaml_template(template, replacements)
        write_file(os.path.join(pkg_path, f"{pkg}.xaml"), xaml_content)

        # 为包生成 XAML 文件
        java_version_content = generate_java_version_content(filtered_data)
        java_version_path = os.path.join(pkg_path, java_version)
        os.makedirs(java_version_path, exist_ok=True)

        template = template_1
        replacements.update({
            "title": "选择 Java 版本",
            "page-number": "4/6",
            "page": f"{distribution}/{os_arch}/{pkg}/{java_version}/{java_version}.xaml",
            "choose": java_version_content,
            "next_page-url": f"https://baidu.com/{distribution}/{os_arch}/{pkg}/{java_version}.json"
        })
        xaml_content = process_xaml_template(template, replacements)
        write_file(os.path.join(java_version_path, f"{java_version}.xaml"), xaml_content)

        # 生成文件类型 XAML 文件
        archive_type_content = generate_archive_type_content(filtered_data)
        archive_path = os.path.join(java_version_path, archive_type)
        os.makedirs(archive_path, exist_ok=True)

        template = template_2
        replacements.update({
            "title": "下载！",
            "page-number": "6/6",
            "page": f"{distribution}/{os_arch}/{pkg}/{java_version}/{archive_type}/{archive_type}.xaml",
            "file_name": filename,
            "download-url": pkg_download_url,
            "info": pkg_info_url
        })
        xaml_content = process_xaml_template(template, replacements)
        write_file(os.path.join(archive_path, f"{archive_type}.xaml"), xaml_content)

    # 最后生成对应的 JSON 文件
    generate_json_files(output_dir)

def generate_system_arch_content(filtered_data):
    """生成系统架构选择项"""
    unique_system_arch = set((item["operating_system"], item["architecture"]) for item in filtered_data)
    return "\n".join(f'<local:MyComboBoxItem Content="{os}-{arch}"/>' for os, arch in unique_system_arch)

def generate_version_content(filtered_data):
    """生成 Java 版本选择项"""
    unique_versions = set(item["major_version"] for item in filtered_data)
    return "\n".join(f'<local:MyComboBoxItem Content="{version}"/>' for version in unique_versions)

def generate_pkg_content(filtered_data, javafx_bundled):
    """生成包类型选择项"""
    unique_pkg_types = set(item["package_type"] + ("fx" if javafx_bundled else "") for item in filtered_data)
    return "\n".join(f'<local:MyComboBoxItem Content="{pkg}"/>' for pkg in unique_pkg_types)

def generate_java_version_content(filtered_data):
    """生成 Java 版本选择项"""
    unique_java_versions = set(item["java_version"] for item in filtered_data)
    return "\n".join(f'<local:MyComboBoxItem Content="{java_version}"/>' for java_version in unique_java_versions)

def generate_archive_type_content(filtered_data):
    """生成档案类型选择项"""
    unique_archive_types = set(item["archive_type"] for item in filtered_data)
    return "\n".join(f'<local:MyComboBoxItem Content="{archive_type}"/>' for archive_type in unique_archive_types)

def generate_json_files(output_dir):
    """扫描并生成与 xaml 文件对应的 json 文件"""
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".xaml"):
                json_file = os.path.splitext(file)[0] + ".json"
                json_content = {"Title": "Java 下载"}
                write_file(os.path.join(root, json_file), json.dumps(json_content, indent=4))

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("请提供 JSON 文件名作为参数")
        return

    json_file = sys.argv[1]
    packages_data = load_json(json_file)

    # 读取模板文件
    with open('1.txt', 'r', encoding='utf-8') as f:
        template_1 = f.read()
    
    with open('2.txt', 'r', encoding='utf-8') as f:
        template_2 = f.read()

    # 处理数据并生成 XAML 文件
    output_dir = "output"
    process_data(packages_data["result"], template_1, template_2, output_dir)

if __name__ == "__main__":
    main()
