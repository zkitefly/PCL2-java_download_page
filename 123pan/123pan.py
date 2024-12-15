import os

def replace_in_file(file_path, old_text, new_text):
    with open(file_path, 'r') as file:
        file_data = file.read()
    
    file_data = file_data.replace(old_text, new_text)
    
    with open(file_path, 'w') as file:
        file.write(file_data)

def process_files(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            process_files(item_path)
        elif item.endswith('.xaml') or item.endswith('.py') or item.endswith('.txt'):
            replace_in_file(item_path, 'https://zkitefly.github.io/PCL2-java_download_page/', 'https://vip.123pan.cn/1821946486/PCL2-java_download_page/')

if __name__ == '__main__':
    current_directory = os.getcwd()
    process_files(current_directory)