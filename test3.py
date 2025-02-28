import json
import itertools
import random


def generate_versions(template, count=2):
    generated = []
    allowed_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    for _ in range(count):
        parts = template.split('.')
        for i, part in enumerate(parts):
            if part == '*':
                j = random.choice(allowed_numbers)
                parts[i] = str(j)
                allowed_numbers.remove(j)
        version = '.'.join(parts)
        generated.append(version)
    return generated

def main(version, config_file):
    all_versions = []
    with open(config_file, 'r') as f:
        config = json.load(f)
    for key, template in config.items():
        while True:
            versions = generate_versions(template)
            if any(v in all_versions for v in versions):
                continue
            else:
                all_versions.extend(versions)
                break


    sorted_versions = sorted(all_versions, key=lambda x: tuple(map(int, x.split('.'))))
    print("Отсортированный список всех версий:")
    for v in sorted_versions:
        print(v)
    older_versions = [v for v in sorted_versions if tuple(map(int, v.split('.'))) < tuple(map(int, version.split('.')))]
    print("\nСписок версий старше", version)
    for v in older_versions:
        print(v)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Использование: python test3.py <версия> <конфигурационный файл>")
        print("Пример: python test3.py 3.7.5 config.json")
    else:
        version = sys.argv[1]
        config_file = sys.argv[2]
        main(version, config_file)