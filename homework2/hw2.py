import subprocess
import configparser
import os

def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return {
        'visualizer_path': config['DEFAULT']['visualizer_path'],
        'repo_path': config['DEFAULT']['repo_path'],
        'output_path': config['DEFAULT']['output_path']
    }

def get_commit_tree(repo_path):
    result = subprocess.run(
        ['git', '-C', repo_path, 'log', '--pretty=format:%H %s', '--reverse'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    if result.returncode != 0:
        print("Ошибка при получении коммитов:", result.stderr)
        return {}

    commits = result.stdout.splitlines()
    commit_info = {}
    
    for line in commits:
        parts = line.split(' ', 1)
        if len(parts) == 2:
            commit_hash = parts[0]
            commit_message = parts[1]
            commit_info[commit_hash] = {
                'message': commit_message,
                'files': [],
                'actions': []
            }

    # Получаем действия с файлами для каждого коммита
    for commit_hash in commit_info.keys():
        diff_result = subprocess.run(
            ['git', '-C', repo_path, 'diff-tree', '--no-commit-id', '--name-status', '-r', commit_hash],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        if diff_result.returncode != 0:
            print(f"Ошибка при получении изменений для коммита {commit_hash}:", diff_result.stderr)
            continue

        for line in diff_result.stdout.splitlines():
            status, filename = line.split('\t')
            if status == 'A':
                action = f"{filename} (C)"
            elif status == 'M':
                action = f"{filename} (R)"
            elif status == 'D':
                action = f"{filename} (D)"
            else:
                continue
            
            commit_info[commit_hash]['files'].append(filename)
            commit_info[commit_hash]['actions'].append(action)

    return commit_info

def generate_plantuml_code(commit_info):
    lines = ["@startuml", "!define RECTANGLE class", "package \"Commits\" {"]
    
    previous_commit_hash = None
    
    for commit_hash, info in commit_info.items():
        short_commit_hash = commit_hash[:7]
        files_list = "\n        + ".join(info['files'])
        
        # Добавляем действия с файлами
        actions_text = "\n        + ".join(info['actions'])
        
        commit_node = f'    RECTANGLE "{info["message"]}" as {short_commit_hash}{{\n        + {commit_hash}\n        + {files_list}\n        + {actions_text}\n    }}'
        lines.append(commit_node)

        if previous_commit_hash:
            lines.append(f'    {previous_commit_hash} --> {short_commit_hash}')

        previous_commit_hash = short_commit_hash

    lines.append("}")  
    lines.append("@enduml")
    
    return "\n".join(lines)

def write_output(output_path, content):
    with open(output_path, 'w') as f:
        f.write(content)

def main(config_path):
    config = read_config(config_path)
    commit_info = get_commit_tree(config['repo_path'])
    plantuml_code = generate_plantuml_code(commit_info)
    
    write_output(config['output_path'], plantuml_code)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Использование: python script.py <config.ini>")
        sys.exit(1)
    main(sys.argv[1])
