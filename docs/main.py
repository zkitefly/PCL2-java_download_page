import json
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        uri = pkg_info.get("result", [])[0].get("direct_download_uri", "")
        log(f"获取 direct_download_uri 成功：{uri}")
        return uri
    except Exception as e:
        log(f"获取 direct_download_uri 失败：{e}")
        return ""

# 处理单个包的逻辑
def process_archive_type(archive_type, current_type_packages, major_version_dir, template_2):
    archive_type_dir = os.path.join(major_version_dir, archive_type)
    archive_type_xaml_path = os.path.join(archive_type_dir, f"{archive_type}.xaml")

    if not current_type_packages:
        log(f"未找到与 {archive_type} 匹配的包，跳过")
        return

    pkg_info_uri = current_type_packages[0]["links"]["pkg_info_uri"]
    direct_download_uri = fetch_direct_download_uri(pkg_info_uri)

    replacements = {
        "title": "下载！",
        "page-number": "6/6",
        "page": f"{dir}/{archive_type}/{archive_type}",
        "file_name": current_type_packages[0]["filename"],
        "download-url": direct_download_uri,
        "info": f"https://api.foojay.io/disco/v3.0/packages/{current_type_packages[0]['id']}"
    }
    write_file(archive_type_xaml_path, generate_xaml(template_2, replacements))
    write_json(archive_type_xaml_path.replace(".xaml", ".json"), {"Title": "Java 下载 - 下载！"})

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

    # 创建线程池
    with ThreadPoolExecutor() as executor:
        futures = []

        for distribution in SUPPORTED_DISTRIBUTIONS:
            log(f"处理 distribution：{distribution}")
            dist_packages = [pkg for pkg in filtered_packages if pkg["distribution"] == distribution]
            if not dist_packages:
                log(f"跳过 distribution：{distribution}（无有效包）")
                continue

            for os_arch in set(f"{pkg['operating_system']}-{pkg['architecture']}" for pkg in dist_packages):
                log(f"处理操作系统架构：{os_arch}")
                os_arch_packages = [pkg for pkg in dist_packages if f"{pkg['operating_system']}-{pkg['architecture']}" == os_arch]

                for major_version in set(pkg["major_version"] for pkg in os_arch_packages):
                    log(f"处理 Java 大版本：{major_version}")
                    major_version_packages = [pkg for pkg in os_arch_packages if pkg["major_version"] == major_version]

                    for package_type in set(f"{pkg['package_type']}{'fx' if pkg['javafx_bundled'] else ''}" for pkg in major_version_packages):
                        log(f"处理包类型：{package_type}")
                        pkg_packages = [pkg for pkg in major_version_packages if f"{pkg['package_type']}{'fx' if pkg['javafx_bundled'] else ''}" == package_type]

                        for archive_type in set(pkg["archive_type"] for pkg in pkg_packages):
                            futures.append(executor.submit(
                                process_archive_type,
                                archive_type,
                                [pkg for pkg in pkg_packages if pkg["archive_type"] == archive_type],
                                os.path.join(OUTPUT_DIR, distribution, os_arch, str(major_version), package_type),
                                template_2
                            ))

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                log(f"任务执行出错：{e}")

    log("程序结束")

if __name__ == "__main__":
    main()
