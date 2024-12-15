import json
import os
import requests

# 支持的 distribution
SUPPORTED_DISTRIBUTIONS = {"temurin", "liberica", "zulu", "graalvm", "semeru", "corretto"}

# 输出路径
OUTPUT_DIR = "./choose"
dir = "choose"

# 日志打印函数
def log(message):
    print(f"[LOG] {message}")

# 读取文件内容
def read_file(path):
    log(f"读取文件：{path}")
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

# 写入文件内容
def write_file(path, content):
    log(f"写入文件：{path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

# 加载 JSON 文件
def load_json(path):
    log(f"加载 JSON 文件：{path}")
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 生成路径并写入 JSON
def write_json(path, content):
    log(f"生成 JSON 文件：{path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)

# 生成模板并替换内容
def generate_xaml(template, replacements):
    content = template
    for placeholder, value in replacements.items():
        content = content.replace(f"[{placeholder}]", value)
    return content

# 根据属性生成 <local:MyComboBoxItem> 内容
def generate_combobox_items(values):
    unique_values = sorted(set(values))  # 去重并排序
    log(f"生成下拉框内容，共 {len(unique_values)} 项")
    return "\n".join(f'<local:MyComboBoxItem Content="{value}"/>' for value in unique_values)

# 获取 direct_download_uri
def fetch_direct_download_uri(pkg_info_uri):
    log(f"获取 direct_download_uri，URL：{pkg_info_uri}")
    try:
        response = requests.get(pkg_info_uri, timeout=10)
        response.raise_for_status()  # 检查 HTTP 请求是否成功
        pkg_info = response.json()
        # 获取第一个 result 的 direct_download_uri
        uri = pkg_info.get("result", [])[0].get("direct_download_uri", "")
        log(f"获取 direct_download_uri 成功：{uri}")
        return uri
    except Exception as e:
        log(f"获取 direct_download_uri 失败：{e}")
        return ""

# 主逻辑
def main():
    log("程序启动")
    
    # 加载数据
    packages = load_json("packages.json")["result"]
    template_1 = read_file("1.txt")
    template_2 = read_file("2.txt")

    # 筛选数据
    filtered_packages = [
        pkg for pkg in packages
        if pkg.get("size", 0) > 1 and pkg.get("distribution") in SUPPORTED_DISTRIBUTIONS
    ]
    log(f"筛选完成，共 {len(filtered_packages)} 个有效包")

    for distribution in SUPPORTED_DISTRIBUTIONS:
        log(f"处理 distribution：{distribution}")
        dist_packages = [pkg for pkg in filtered_packages if pkg["distribution"] == distribution]
        if not dist_packages:
            log(f"跳过 distribution：{distribution}（无有效包）")
            continue

        # 生成 distribution 级别的文件
        distribution_dir = os.path.join(OUTPUT_DIR, distribution)
        distribution_xaml_path = os.path.join(distribution_dir, f"{distribution}.xaml")
        
        operating_systems = [f"{pkg['operating_system']}-{pkg['architecture']}" for pkg in dist_packages]
        replacements = {
            "title": "选择系统类型和系统架构",
            "page-number": "1/6",
            "page": f"{dir}/{distribution}/{distribution}",
            "choose": generate_combobox_items(operating_systems),
            "next_page-url": f"https://vip.123pan.cn/1821946486/PCL2-java_download_page/{dir}/{distribution}/{{0}}/{{0}}.json"
        }
        write_file(distribution_xaml_path, generate_xaml(template_1, replacements))
        write_json(distribution_xaml_path.replace(".xaml", ".json"), {"Title": "Java 下载 - 选择系统类型和系统架构"})

        for os_arch in operating_systems:
            log(f"处理操作系统架构：{os_arch}")
            os_arch_packages = [pkg for pkg in dist_packages if f"{pkg['operating_system']}-{pkg['architecture']}" == os_arch]
            os_arch_dir = os.path.join(distribution_dir, os_arch)
            os_arch_xaml_path = os.path.join(os_arch_dir, f"{os_arch}.xaml")
            
            major_versions = [pkg["major_version"] for pkg in os_arch_packages]
            replacements = {
                "title": "选择 Java 大版本",
                "page-number": "2/6",
                "page": f"{dir}/{distribution}/{os_arch}/{os_arch}",
                "choose": generate_combobox_items(major_versions),
                "next_page-url": f"https://vip.123pan.cn/1821946486/PCL2-java_download_page/{dir}/{distribution}/{os_arch}/{{0}}/{{0}}.json"
            }
            write_file(os_arch_xaml_path, generate_xaml(template_1, replacements))
            write_json(os_arch_xaml_path.replace(".xaml", ".json"), {"Title": "Java 下载 - 选择 Java 大版本"})

            for major_version in major_versions:
                log(f"处理 Java 大版本：{major_version}")
                major_version_packages = [pkg for pkg in os_arch_packages if pkg["major_version"] == major_version]
                major_version_dir = os.path.join(os_arch_dir, str(major_version))
                major_version_xaml_path = os.path.join(major_version_dir, f"{major_version}.xaml")

                package_types = [
                    f"{pkg['package_type']}{'fx' if pkg['javafx_bundled'] else ''}"
                    for pkg in major_version_packages
                ]
                replacements = {
                    "title": "选择包类型",
                    "page-number": "3/6",
                    "page": f"{dir}/{distribution}/{os_arch}/{major_version}/{major_version}",
                    "choose": generate_combobox_items(package_types),
                    "next_page-url": f"https://vip.123pan.cn/1821946486/PCL2-java_download_page/{dir}/{distribution}/{os_arch}/{major_version}/{{0}}/{{0}}.json"
                }
                write_file(major_version_xaml_path, generate_xaml(template_1, replacements))
                write_json(major_version_xaml_path.replace(".xaml", ".json"), {"Title": "Java 下载 - 选择包类型"})

                for package_type in package_types:
                    log(f"处理包类型：{package_type}")
                    pkg_packages = [
                        pkg for pkg in major_version_packages
                        if f"{pkg['package_type']}{'fx' if pkg['javafx_bundled'] else ''}" == package_type
                    ]
                    pkg_dir = os.path.join(major_version_dir, package_type)
                    pkg_xaml_path = os.path.join(pkg_dir, f"{package_type}.xaml")

                    java_versions = [pkg["java_version"] for pkg in pkg_packages]
                    replacements = {
                        "title": "选择 Java 版本",
                        "page-number": "4/6",
                        "page": f"{dir}/{distribution}/{os_arch}/{major_version}/{package_type}/{package_type}",
                        "choose": generate_combobox_items(java_versions),
                        "next_page-url": f"https://vip.123pan.cn/1821946486/PCL2-java_download_page/{dir}/{distribution}/{os_arch}/{major_version}/{package_type}/{{0}}/{{0}}.json"
                    }
                    write_file(pkg_xaml_path, generate_xaml(template_1, replacements))
                    write_json(pkg_xaml_path.replace(".xaml", ".json"), {"Title": "Java 下载 - 选择 Java 版本"})

                    for java_version in java_versions:
                        log(f"处理 Java 版本：{java_version}")
                        java_version_packages = [pkg for pkg in pkg_packages if pkg["java_version"] == java_version]
                        java_version_dir = os.path.join(pkg_dir, java_version)
                        java_version_xaml_path = os.path.join(java_version_dir, f"{java_version}.xaml")

                        archive_types = [pkg["archive_type"] for pkg in java_version_packages]
                        replacements = {
                            "title": "选择文件类型",
                            "page-number": "5/6",
                            "page": f"{dir}/{distribution}/{os_arch}/{major_version}/{package_type}/{java_version}/{java_version}",
                            "choose": generate_combobox_items(archive_types),
                            "next_page-url": f"https://vip.123pan.cn/1821946486/PCL2-java_download_page/{dir}/{distribution}/{os_arch}/{major_version}/{package_type}/{java_version}/{{0}}/{{0}}.json"
                        }
                        write_file(java_version_xaml_path, generate_xaml(template_1, replacements))
                        write_json(java_version_xaml_path.replace(".xaml", ".json"), {"Title": "Java 下载 - 选择文件类型"})

                        for archive_type in archive_types:
                            log(f"处理文件类型：{archive_type}")
                            archive_type_dir = os.path.join(java_version_dir, archive_type)
                            archive_type_xaml_path = os.path.join(archive_type_dir, f"{archive_type}.xaml")

                            # 根据 archive_type 筛选出对应的包
                            current_type_packages = [pkg for pkg in java_version_packages if pkg["archive_type"] == archive_type]
                            if not current_type_packages:
                                log(f"未找到与 {archive_type} 匹配的包，跳过")
                                continue

                            # 提取 direct_download_uri
                            pkg_info_uri = current_type_packages[0]["links"]["pkg_info_uri"]
                            direct_download_uri = fetch_direct_download_uri(pkg_info_uri)

                            replacements = {
                                "title": "下载！",
                                "page-number": "6/6",
                                "page": f"{dir}/{distribution}/{os_arch}/{major_version}/{package_type}/{java_version}/{archive_type}/{archive_type}",
                                "file_name": current_type_packages[0]["filename"],
                                "download-url": direct_download_uri,
                                "info": f"https://api.foojay.io/disco/v3.0/packages/{current_type_packages[0]['id']}"
                            }
                            write_file(archive_type_xaml_path, generate_xaml(template_2, replacements))
                            write_json(archive_type_xaml_path.replace(".xaml", ".json"), {"Title": "Java 下载 - 下载！"})

    log("程序结束")

if __name__ == "__main__":
    main()
