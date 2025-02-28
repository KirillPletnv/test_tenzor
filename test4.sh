#!/bin/bash

units=$(systemctl list-unit-files --type=service | grep -o 'foobar-[^ ]*\.service')

for unit in $units; do
    echo "Остановка systemd-unit $unit..."
    sudo systemctl stop "$unit"    
    
    working_dir=$(systemctl show -p WorkingDirectory "$unit" | cut -d= -f2)      
    exec_start=$(systemctl show -p ExecStart "$unit" | grep -oP 'argv\[\]=\K[^;]+') 
    service_name=$(echo "$unit" | sed 's/foobar-\(.*\)\.service/\1/')    
    new_working_dir="/srv/data/$service_name"    
    new_exec_start=$(echo "$exec_start" | sed "s|/opt/misc/$service_name|$new_working_dir|")
    
    echo "Перемещение файлов из $working_dir в $new_working_dir..."
    sudo mkdir -p "$new_working_dir"
    sudo cp -r "$working_dir"/* "$new_working_dir"
    
    unit_file="/etc/systemd/system/$unit"
    echo "Обновление путей в файле $unit_file..."
    sudo sed -i "s|WorkingDirectory=$working_dir|WorkingDirectory=$new_working_dir|" "$unit_file"
    sudo sed -i "s|ExecStart=.*|ExecStart=$new_exec_start|" "$unit_file"
    
    sudo systemctl daemon-reload    
    echo "Перезапуск $unit..."

    sudo systemctl start "$unit"
    echo "Редактирование параметров $unit выполнено"
done

echo "Все systemd-unit отредактированы."
