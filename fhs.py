#!/usr/bin/env python3
import os, argparse, json, random, sys
from pathlib import Path
from subprocess import run

VERSION = "0.02" 
CONF = Path.home() / ".feh_saved_wallpapers.json"
DIR_CONF = Path.home() / ".feh_wallpaper_dir.json"
FEHBG = Path.home() / ".fehbg"

def get_dir():
    if DIR_CONF.exists():
        try:
            with open(DIR_CONF, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and "dir" in data:
                    d = Path(data["dir"])
                    if d.exists() and d.is_dir():
                        return d
        except json.JSONDecodeError:
            pass
    print("Ошибка: некорректный путь для обоев")
    sys.exit(1)

def set_dir(d):
    d = Path(d).expanduser().resolve()
    if not d.exists() or not d.is_dir():
        print(f"Ошибка: директория {d} не найдена")
        sys.exit(1)
    with open(DIR_CONF, 'w') as f:
        json.dump({"dir": str(d)}, f)
    print(f"Директория обоев установлена: {d}")

def get_wall():
    if FEHBG.exists():
        with open(FEHBG, 'r') as f:
            for line in f:
                if '--bg-scale' in line:
                    return line.split()[-1].strip("'")
    return None

def load_conf():
    if CONF.exists():
        try:
            with open(CONF, 'r') as f:
                c = json.load(f)
                if isinstance(c, dict):
                    c.setdefault("fav", [])
                    c.setdefault("hist", [])
                    return c
        except json.JSONDecodeError:
            pass
    return {"fav": [], "hist": []}

def save_conf(c):
    with open(CONF, 'w') as f:
        json.dump(c, f, indent=2)

def set_wall(p, undo=False):
    cur = get_wall()
    c = load_conf()
    if not undo and cur:
        c['hist'].append(cur)
        c['hist'] = c['hist'][-10:]
        save_conf(c)
    run(['feh', '--bg-scale', str(p)])

def get_files(sub=False):
    d = get_dir()
    return [p for p in (d.rglob('*') if sub else d.glob('*')) if p.suffix.lower() in ('.jpeg', '.jpg', '.png') and p.is_file()]

def rand_wall(sub=False):
    f = get_files(sub)
    if f:
        set_wall(random.choice(f))

def save_wall(p):
    c = load_conf()
    p = Path(p).expanduser().resolve()
    if not p.exists():
        print(f"Файл {p} не найден")
        return
    ps = str(p)
    if any(f['path'] == ps for f in c['fav']):
        print(f"Обои {ps} уже в избранном")
        return
    c['fav'].append({"id": len(c['fav']) + 1, "path": ps})
    save_conf(c)
    print(f"Сохранены обои: {ps}, ID: {len(c['fav'])}")

def list_favs():
    for i in sorted(load_conf()['fav'], key=lambda x: x['id']):
        print(f"{i['id']} : {i['path']}")

def set_fav(i):
    for x in load_conf()['fav']:
        if x['id'] == i:
            set_wall(Path(x['path']))
            return
    print(f"Обои с ID {i} не найдены")

def rm_fav(i):
    c = load_conf()
    new_fav = [x for x in c['fav'] if x['id'] != i]
    if len(new_fav) == len(c['fav']):
        print(f"Обои с ID {i} не найдены")
        return
    c['fav'] = new_fav
    save_conf(c)
    print(f"Удалены обои с ID {i}")

def un_wall():
    c = load_conf()
    if c['hist']:
        set_wall(Path(c['hist'].pop()), undo=True)
        save_conf(c)
    else:
        print("История пуста")

def rand_fav():
    f = load_conf()['fav']
    if f:
        set_wall(Path(random.choice(f)['path']))
    else:
        print("Нет сохраненных обоев")

def acto_fav():
    cur_wall = get_wall()
    if cur_wall:
        save_wall(cur_wall)
    else:
        print("Текущие обои не найдены")

def rm_invalid_favs():
    c = load_conf()
    removed = []
    valid_favs = []
    for fav in c['fav']:
        if Path(fav['path']).exists():
            valid_favs.append(fav)
        else:
            removed.append(fav)
    if removed:
        c['fav'] = valid_favs
        save_conf(c)
        print("Удалены обои с некорректными путями:")
        for r in removed:
            print(f"ID: {r['id']}, Путь: {r['path']}")
    else:
        print("Все обои в избранном имеют корректные пути")

def reindex_favs():
    c = load_conf()
    for i, fav in enumerate(c['fav'], start=1):
        fav['id'] = i
    save_conf(c)
    print("ID обоев переиндексированы")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('-p', action='store_true')
    p.add_argument('-c', action='store_true')
    p.add_argument('-f', metavar='PATH')
    p.add_argument('-fl', action='store_true')
    p.add_argument('-fs', type=int, metavar='ID')
    p.add_argument('-fsw', metavar='PATH')
    p.add_argument('-frm', type=int, metavar='ID')
    p.add_argument('-d', action='store_true')
    p.add_argument('-w', action='store_true')
    p.add_argument('-v', action='store_true')
    p.add_argument('-D', metavar='PATH')
    p.add_argument('-lc', action='store_true')
    p.add_argument('-R', action='store_true') 
    p.add_argument('-I', action='store_true')  

    a = p.parse_args()

    if a.v:
        print(f"FehManager v{VERSION}")
    elif a.D:
        set_dir(a.D)
    elif a.c:
        print(get_wall() or "Нет установленных обоев")
    elif a.fl:
        list_favs()
    elif a.fs:
        set_fav(a.fs)
    elif a.fsw:
        set_wall(Path(a.fsw))
    elif a.frm:
        rm_fav(a.frm)
    elif a.d:
        un_wall()
    elif a.f:
        save_wall(a.f)
    elif a.w:
        rand_fav()
    elif a.lc:
        acto_fav()
    elif a.R:
        rm_invalid_favs()
    elif a.I:
        reindex_favs()
    else:
        rand_wall(a.p)

if __name__ == "__main__":
    main()
