import os, json, urllib.request, sys, time

LOCAL_VERSION_FILE = "version.txt"
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/MrRjczr/Murzik_Desktop/main/latest.json"

def get_local():
    try:
        return open(LOCAL_VERSION_FILE).read().strip()
    except:
        return "0.0.0"

def check_update():
    try:
        print(f"Мурзик v{get_local()} - проверка обновы...")
        req = urllib.request.Request(REMOTE_VERSION_URL, headers={'Cache-Control': 'no-cache'})
        data = json.loads(urllib.request.urlopen(req, timeout=5).read())
        remote = data['version']
        if remote != get_local():
            print(f"Новая версия {remote}! Скачиваю...")
            new_code = urllib.request.urlopen(data['url'], timeout=10).read()
            # бекап старой
            if os.path.exists("run_murzik.py"):
                os.rename("run_murzik.py", "run_murzik_backup.py")
            open("run_murzik.py","wb").write(new_code)
            open(LOCAL_VERSION_FILE,"w").write(remote)
            print(f"Обновлено до {remote}: {data.get('changelog','')}")
            return True
        print("Обновлений нет")
    except Exception as e:
        print(f"Обнова не проверена: {e}")
    return False