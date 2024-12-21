import json
import os
import sys
from tqdm import tqdm

def process_json_file(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def generate_xaml_from_template(template, replacements):
    for key, value in replacements.items():
        template = template.replace(f"[{key}]", value)
    return template

def write_xaml_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def process_packages(packages_data, template_1, template_2, output_dir):
    # First filtering
    filtered = [
        package for package in packages_data['result']
        if package['directly_downloadable'] and package['free_use_in_production'] and package['major_version'] != 6
    ]
    
    for package in tqdm(filtered):
        distribution = package['distribution']
        base_path = os.path.join(output_dir, distribution)
        
        # Step 1: Generate /[distribution]/[distribution].xaml
        distribution_xaml_path = os.path.join(base_path, f"{distribution}.xaml")
        replacements = {
            'title': "选择系统类型和系统架构",
            'page-number': "1/6",
            'page': f"{output_dir2}/{distribution}/{distribution}",
            'xaml': "json",
            'choose': generate_choose_lines(filtered, 'operating_system', 'architecture'),
            'next_page-url': f"https://zkitefly.github.io/PCL2-java_download_page/{output_dir2}/{distribution}/{{0}}/{{0}}.json"
        }
        write_xaml_file(distribution_xaml_path, generate_xaml_from_template(template_1, replacements))

        # Step 2: Generate /[distribution]/[operating_system]-[architecture]/[operating_system]-[architecture].xaml
        for os_arch in get_unique_pairs(filtered, 'operating_system', 'architecture'):
            os_arch_path = os.path.join(base_path, f"{os_arch[0]}-{os_arch[1]}")
            os_arch_xaml_path = os.path.join(os_arch_path, f"{os_arch[0]}-{os_arch[1]}.xaml")
            replacements = {
                'title': "选择 Java 大版本",
                'page-number': "2/6",
                'page': f"{output_dir2}/{distribution}/{os_arch[0]}-{os_arch[1]}/{os_arch[0]}-{os_arch[1]}",
                'choose': generate_choose_lines_for_major_version(filtered, os_arch),
                'next_page-url': f"https://zkitefly.github.io/PCL2-java_download_page/{output_dir2}/{distribution}/{os_arch[0]}-{os_arch[1]}/{{0}}/{{0}}.json"
            }
            write_xaml_file(os_arch_xaml_path, generate_xaml_from_template(template_1, replacements))

            # Step 3: Generate /[distribution]/[operating_system]-[architecture]/[major_version]/[major_version].xaml
            for major_version in get_unique_values(filtered, 'major_version'):
                major_version_path = os.path.join(os_arch_path, str(major_version))
                major_version_xaml_path = os.path.join(major_version_path, f"{major_version}.xaml")
                pkg = f"{package['package_type']}{'fx' if package['javafx_bundled'] else ''}"
                replacements = {
                    'title': "选择包类型",
                    'page-number': "3/6",
                    'page': f"{output_dir2}/{distribution}/{os_arch[0]}-{os_arch[1]}/{major_version}/{major_version}",
                    'choose': generate_choose_lines_for_package_type(filtered, pkg),
                    'next_page-url': f"https://zkitefly.github.io/PCL2-java_download_page/{output_dir2}/{distribution}/{os_arch[0]}-{os_arch[1]}/{major_version}/{{0}}/{{0}}.json"
                }
                write_xaml_file(major_version_xaml_path, generate_xaml_from_template(template_1, replacements))

                # Step 4: Generate /[distribution]/[operating_system]-[architecture]/[major_version]/[pkg]/[pkg].xaml
                for pkg in get_unique_values(filtered, 'package_type'):
                    pkg_path = os.path.join(major_version_path, pkg)
                    pkg_xaml_path = os.path.join(pkg_path, f"{pkg}.xaml")
                    replacements = {
                        'title': "选择 Java 版本",
                        'page-number': "4/6",
                        'page': f"{output_dir2}/{distribution}/{os_arch[0]}-{os_arch[1]}/{major_version}/{pkg}/{pkg}",
                        'choose': generate_choose_lines_for_java_version(filtered),
                        'next_page-url': f"https://zkitefly.github.io/PCL2-java_download_page/{output_dir2}/{distribution}/{os_arch[0]}-{os_arch[1]}/{major_version}/{pkg}/{{0}}/{{0}}.json"
                    }
                    write_xaml_file(pkg_xaml_path, generate_xaml_from_template(template_1, replacements))

                    # Step 5: Generate /[distribution]/[operating_system]-[architecture]/[major_version]/[pkg]/[java_version]/[java_version].xaml
                    for java_version in get_unique_values(filtered, 'java_version'):
                        java_version_path = os.path.join(pkg_path, java_version)
                        java_version_xaml_path = os.path.join(java_version_path, f"{java_version}.xaml")
                        replacements = {
                            'title': "选择文件类型",
                            'page-number': "5/6",
                            'page': f"{output_dir2}/{distribution}/{os_arch[0]}-{os_arch[1]}/{major_version}/{pkg}/{java_version}/{java_version}",
                            'choose': generate_choose_lines_for_archive_type(filtered),
                            'next_page-url': f"https://zkitefly.github.io/PCL2-java_download_page/{output_dir2}/{distribution}/{os_arch[0]}-{os_arch[1]}/{major_version}/{pkg}/{java_version}/{{0}}/{{0}}.json"
                        }
                        write_xaml_file(java_version_xaml_path, generate_xaml_from_template(template_1, replacements))

                        # Step 6: Generate /[distribution]/[operating_system]-[architecture]/[major_version]/[pkg]/[java_version]/[archive_type]/[archive_type].xaml
                        for archive_type in get_unique_values(filtered, 'archive_type'):
                            archive_type_path = os.path.join(java_version_path, archive_type)
                            archive_type_xaml_path = os.path.join(archive_type_path, f"{archive_type}.xaml")
                            replacements = {
                                'title': "下载！",
                                'page-number': "6/6",
                                'page': f"{output_dir2}/{distribution}/{os_arch[0]}-{os_arch[1]}/{major_version}/{pkg}/{java_version}/{archive_type}/{archive_type}",
                                'file_name': package['filename'],
                                'download-url': package['links']['pkg_download_redirect'],
                                'info': f"https://api.foojay.io/disco/v3.0/packages/{package['id']}",
                                'raw-download-url': package['links']['pkg_info_uri']
                            }
                            write_xaml_file(archive_type_xaml_path, generate_xaml_from_template(template_2, replacements))

    # Generate JSON file for each XAML file
    generate_json_for_xaml_files(output_dir)

def generate_choose_lines(filtered, os_key, arch_key):
    lines = []
    for os_arch in get_unique_pairs(filtered, os_key, arch_key):
        lines.append(f'<local:MyComboBoxItem Content="{os_arch[0]}-{os_arch[1]}"/>')
    return "\n".join(lines)

def generate_choose_lines_for_major_version(filtered, os_arch):
    lines = [f'<local:MyComboBoxItem Content="{major_version}"/>'
             for major_version in get_unique_values(filtered, 'major_version')]
    return "\n".join(lines)

def generate_choose_lines_for_package_type(filtered, pkg):
    lines = [f'<local:MyComboBoxItem Content="{pkg}"/>']
    return "\n".join(lines)

def generate_choose_lines_for_java_version(filtered):
    lines = [f'<local:MyComboBoxItem Content="{java_version}"/>'
             for java_version in get_unique_values(filtered, 'java_version')]
    return "\n".join(lines)

def generate_choose_lines_for_archive_type(filtered):
    lines = [f'<local:MyComboBoxItem Content="{archive_type}"/>'
             for archive_type in get_unique_values(filtered, 'archive_type')]
    return "\n".join(lines)

def get_unique_pairs(filtered, key1, key2):
    pairs = []
    for package in filtered:
        if key1 in package and key2 in package:
            pairs.append((package[key1], package[key2]))
    return list(set(pairs))

def get_unique_values(filtered, key):
    return list(set(item[key] for item in filtered if key in item))

def generate_json_for_xaml_files(output_dir):
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".xaml"):
                json_file_path = os.path.splitext(os.path.join(root, file))[0] + ".json"
                if not os.path.exists(json_file_path):
                    json_content = {"Title": "Java 下载"}
                    with open(json_file_path, 'w') as json_file:
                        json.dump(json_content, json_file)

if __name__ == "__main__":
    json_file = sys.argv[1]
    packages_data = process_json_file(json_file)
    
    with open("1.txt", 'r') as f:
        template_1 = f.read()
    
    with open("2.txt", 'r') as f:
        template_2 = f.read()
    
    output_dir = './choose'
    output_dir2 = 'choose'
    process_packages(packages_data, template_1, template_2, output_dir)
