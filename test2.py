import os
import stat
import sys
import shutil
import json
import logging
import time
from functools import wraps
from datetime import datetime
from git import Repo


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Выполняется функция {func.__name__}")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed_time = end - start
        print(f"'{func.__name__}' выполнено за {elapsed_time:.4f} секунд")
        print('---------------------------------------------')
        return result
    return wrapper

@timer
def clone_git_repository(repo_url, clone_dir):
    logging.info(f"Клонирование репозитория {repo_url} в {clone_dir}...")
    Repo.clone_from(repo_url, clone_dir)
    logging.info("Клонирование завершено.")

def del_readonly(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)
    logging.warning(f"У директории был доступ только для чтения: {name}")

def replace_slash(input_string):
    if os.name == 'nt':
        print("Скрипт запущен в Windows.")
        return input_string.replace('/', '\\')
    elif os.name == 'posix':
        print("Скрипт запущен в Linux.")
        return input_string.replace('\\', '/')
    else:
        print("Неизвестная операционная система.")
        return input_string

@timer
def remove_unused_dirs(clone_dir, source_dir):
    ends = source_dir.split('\\')
    source_full_path = os.path.join(clone_dir, source_dir)
    logging.info(f"Удаление лишних директорий в {clone_dir}...")

    for item in os.listdir(clone_dir):
        item_path = os.path.join(clone_dir, item)
        #if item == ".git" or item in ends:
        if item in ends:
            logging.info(f"Директория/файл {item} пропущен.")
            continue
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path, onerror=del_readonly)
                logging.info(f"Удалена директория: {item}")
            else:
                os.remove(item_path)  # Удаляем файл
                logging.info(f"Удалён файл: {item}")
        except PermissionError as e:
            logging.error(f"Ошибка доступа: {e}")
        except FileNotFoundError as e:
            logging.error(f"Файл/директория не найдена: {e}")
        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
    logging.info("Очистка завершена.")


@timer
def create_file_with_version(source_dir, version):
    logging.info(f"Создание файла version.json в {source_dir}...")
    files = [f for f in os.listdir(source_dir) if f.endswith(('.py', '.js', '.sh'))]
    version_data = {
        "name": "hello world",
        "version": version,
        "files": files
    }
    version_file_path = os.path.join(source_dir, "version.json")
    with open(version_file_path, 'w') as f:
        json.dump(version_data, f, indent=4)
    logging.info(f"Файл version.json создан: {version_data}")


@timer
def create_archive(source_dir, output_dir):
    logging.info(f"Создание архива из {source_dir}...")
    dir_name = os.path.basename(source_dir)
    current_date = datetime.now().strftime("%d%m%Y")
    archive_name = f"{dir_name}{current_date}"
    archive_path = os.path.join(output_dir, archive_name)
    shutil.make_archive(archive_path, 'zip', source_dir)
    logging.info(f"Архив создан: {archive_path}")

@timer
def project_clone_and_delete(repo_url, source_path, version):
    clone_dir = os.path.join(os.getcwd(), "repository")
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir, onerror=del_readonly)
    os.makedirs(clone_dir)
    clone_git_repository(repo_url, clone_dir)
    source_dir = os.path.join(clone_dir, source_path)
    if not os.path.exists(source_dir):
        logging.error(f"Директория исходного кода не найдена: {source_dir}")
        return
    create_file_with_version(source_dir, version)
    output_dir = os.getcwd()
    create_archive(source_dir, output_dir)
    remove_unused_dirs(clone_dir, source_path)
    logging.info("Временная директория удалена.")

#if __name__ == "__main__":
#    repo_url = "https://github.com/paulbouwer/hello-kubernetes"
#    #my_repo_url = "https://github.com/KirillPletnv/project_taskier"
#    source_path = "src\\app"
#    #my_source_path = "taskier-env"
#    version = "25.3000"#
#    main(repo_url, source_path, version)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python test2.py <репозиторий> <путь к коду> <версия>")
        print("Пример: python test2.py https://github.com/paulbouwer/hello-kubernetes src/app 25.3000")
    else:
        repo_url = sys.argv[1]
        source_path = sys.argv[2]
        version = sys.argv[3]
        source_path = replace_slash(source_path)
        project_clone_and_delete(repo_url, source_path, version)
