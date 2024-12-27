import json
import requests
from flask import Flask, request, jsonify, redirect
from functools import lru_cache

app = Flask(__name__)

DATA_API = "https://api.foojay.io/disco/v3.0/packages"
TEMPLATE1_PATH = "1.txt"
TEMPLATE2_PATH = "2.txt"

def get_template(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

@lru_cache(maxsize=128)
def get_data_api():
    response = requests.get(DATA_API)
    return response.json()['result']

def filter_packages(data, distribution=None, operating_system=None, architecture=None, major_version=None, package_type=None, javafx_bundled=None, java_version=None, archive_type=None):
    filtered = []
    for item in data:
        if distribution and item['distribution'] != distribution:
            continue
        if operating_system and item['operating_system'] != operating_system:
            continue
        if architecture and item['architecture'] != architecture:
            continue
        if major_version and item['major_version'] != major_version:
            continue
        if package_type and item['package_type'] != package_type:
            continue
        if javafx_bundled is not None and item['javafx_bundled'] != javafx_bundled:
            continue
        if java_version and item['java_version'] != java_version:
            continue
        if archive_type and item['archive_type'] != archive_type:
            continue
        if not item['directly_downloadable'] or not item['free_use_in_production']:
            continue
        if item['major_version'] == 6:
            continue
        filtered.append(item)
    return filtered

@app.route('/', methods=['GET'])
def handle_root_request():
    return redirect(request.host_url.rstrip('/') + "/Custom.xaml", code=301)

@app.route('/<path:params>', methods=['GET'])
def handle_request(params):
    server_address = request.host_url.rstrip('/')
    data = get_data_api()

    if ".xaml" in params:
        path_parts = params.replace('.xaml', '').split('/')
    elif ".json" in params:
        return jsonify({"Title": "Java 下载"})
    else:
        return "Invalid request path"
    
    template1 = get_template(TEMPLATE1_PATH)
    template2 = get_template(TEMPLATE2_PATH)
    
    if len(path_parts) == 1:
        if path_parts in ['Custom', 'download', 'goto']:
            return redirect(f"https://vip.123pan.cn/1821946486/PCL2-java_download_page/{distribution}.xaml", code=301)

        distribution = path_parts[0]
        filtered_data = filter_packages(data, distribution=distribution)
        os_arch_list = []
        for item in filtered_data:
            comb = f"{item['operating_system']}-{item['architecture']}"
            if comb not in os_arch_list:
                os_arch_list.append(comb)
        choose_content = "\n".join([f'<local:MyComboBoxItem Content="{comb}"/>' for comb in os_arch_list])
        content = template1.replace('[choose]', choose_content)
        content = content.replace('[title]', '选择系统类型和系统架构')
        content = content.replace('[page]', f'{distribution}')
        content = content.replace('[next_page-url]', f'{server_address}/{distribution}/{{0}}.json')
        content = content.replace('[page-number]', '1/6')
        return content
    
    elif len(path_parts) == 2:
        distribution, os_arch = path_parts
        os, arch = os_arch.split('-')
        filtered_data = filter_packages(data, distribution=distribution, operating_system=os, architecture=arch)
        major_versions = set([item['major_version'] for item in filtered_data])
        choose_content = "\n".join([f'<local:MyComboBoxItem Content="{mv}"/>' for mv in major_versions])
        content = template1.replace('[choose]', choose_content)
        content = content.replace('[title]', '选择 Java 大版本')
        content = content.replace('[page]', f'{distribution}/{os_arch}')
        content = content.replace('[next_page-url]', f'{server_address}/{distribution}/{os_arch}/{{0}}.json')
        content = content.replace('[page-number]', '2/6')
        return content
    
    elif len(path_parts) == 3:
        distribution, os_arch, major_version = path_parts
        os, arch = os_arch.split('-')
        filtered_data = filter_packages(data, distribution=distribution, operating_system=os, architecture=arch, major_version=int(major_version))
        package_types = []
        for item in filtered_data:
            pkg = f"{item['package_type']}fx" if item['javafx_bundled'] else item['package_type']
            if pkg not in package_types:
                package_types.append(pkg)
        choose_content = "\n".join([f'<local:MyComboBoxItem Content="{pkg}"/>' for pkg in package_types])
        content = template1.replace('[choose]', choose_content)
        content = content.replace('[title]', '选择包类型')
        content = content.replace('[page]', f'{distribution}/{os_arch}/{major_version}')
        content = content.replace('[next_page-url]', f'{server_address}/{distribution}/{os_arch}/{major_version}/{{0}}.json')
        content = content.replace('[page-number]', '3/6')
        return content
    
    elif len(path_parts) == 4:
        distribution, os_arch, major_version, pkg = path_parts
        os, arch = os_arch.split('-')
        javafx_bundled = 'fx' in pkg
        pkg = pkg.replace('fx', '')
        filtered_data = filter_packages(data, distribution=distribution, operating_system=os, architecture=arch, major_version=int(major_version), package_type=pkg, javafx_bundled=javafx_bundled)
        java_versions = set([item['java_version'] for item in filtered_data])
        choose_content = "\n".join([f'<local:MyComboBoxItem Content="{jv}"/>' for jv in java_versions])
        content = template1.replace('[choose]', choose_content)
        content = content.replace('[title]', '选择 Java 版本')
        content = content.replace('[page]', f'{distribution}/{os_arch}/{major_version}/{pkg}')
        content = content.replace('[next_page-url]', f'{server_address}/{distribution}/{os_arch}/{major_version}/{pkg}/{{0}}.json')
        content = content.replace('[page-number]', '4/6')
        return content
    
    elif len(path_parts) == 5:
        distribution, os_arch, major_version, pkg, java_version = path_parts
        os, arch = os_arch.split('-')
        javafx_bundled = 'fx' in pkg
        pkg = pkg.replace('fx', '')
        filtered_data = filter_packages(data, distribution=distribution, operating_system=os, architecture=arch, major_version=int(major_version), package_type=pkg, javafx_bundled=javafx_bundled, java_version=java_version)
        archive_types = set([item['archive_type'] for item in filtered_data])
        choose_content = "\n".join([f'<local:MyComboBoxItem Content="{at}"/>' for at in archive_types])
        content = template1.replace('[choose]', choose_content)
        content = content.replace('[title]', '选择文件类型')
        content = content.replace('[page]', f'{distribution}/{os_arch}/{major_version}/{pkg}/{java_version}')
        content = content.replace('[next_page-url]', f'{server_address}/{distribution}/{os_arch}/{major_version}/{pkg}/{java_version}/{{0}}.json')
        content = content.replace('[page-number]', '5/6')
        return content
    
    elif len(path_parts) == 6:
        distribution, os_arch, major_version, pkg, java_version, archive_type = path_parts
        os, arch = os_arch.split('-')
        javafx_bundled = 'fx' in pkg
        pkg = pkg.replace('fx', '')
        filtered_data = filter_packages(data, distribution=distribution, operating_system=os, architecture=arch, major_version=int(major_version), package_type=pkg, javafx_bundled=javafx_bundled, java_version=java_version, archive_type=archive_type)
        if filtered_data:
            item = filtered_data[0]
            content = template2.replace('[title]', '下载！')
            content = content.replace('[page-number]', '6/6')
            content = content.replace('[page]', f'{distribution}/{os_arch}/{major_version}/{pkg}/{java_version}/{archive_type}')
            content = content.replace('[file_name]', item['filename'])
            content = content.replace('[download-url]', item['links']['pkg_download_redirect'])
            content = content.replace('[raw-download-url]', f"https://api.foojay.io/disco/v3.0/ids/{item['id']}")
            content = content.replace('[info]', f"https://api.foojay.io/disco/v3.0/packages/{item['id']}")
            return content
    
    return "Invalid request path"

if __name__ == '__main__':
    app.run(debug=True)