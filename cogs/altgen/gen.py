import os
import json
import random

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

ALTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'alts'))

def get_alt(type_name):
    path = os.path.join(ALTS_DIR, f'{type_name}.txt')
    if not os.path.exists(path):
        return ''
    alts = read_file(type_name)
    if not alts:
        return ''
    return random.choice(alts)

def add_alt(type_name, alt):
    path = os.path.join(ALTS_DIR, f'{type_name}.txt')
    with open(path, 'a', encoding='utf-8') as f:
        f.write(f'{alt}\n')

def remove_alt(type_name, alt):
    path = os.path.join(ALTS_DIR, f'{type_name}.txt')
    if not os.path.exists(path):
        return
    alts = read_file(type_name)
    alts = [a for a in alts if a != alt]
    alts = [a for a in alts if a != '']
    save_file(type_name, alts)

def read_file(type_name):
    path = os.path.join(ALTS_DIR, f'{type_name}.txt')
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return [line for line in f.read().split('\n') if line]

def save_file(type_name, alts):
    path = os.path.join(ALTS_DIR, f'{type_name}.txt')
    if not os.path.exists(path):
        return
    with open(path, 'w', encoding='utf-8') as f:
        for alt in alts:
            f.write(f'{alt}\n')

def get_allowed_roles():
    return config.get('allowedRoles', [])

def get_allowed_channels():
    return config.get('allowedChannels', [])

def get_allowed_free_channels():
    return config.get('allowedFreeChannels', [])

def has_access(member):
    access = False
    for role in member.roles:
        if role.id in get_allowed_roles():
            access = True
    return access

def allowed_channel(channel):
    return channel.id in get_allowed_channels()

def allowed_free_channel(channel):
    return channel.id in get_allowed_free_channels()

def calculate_stock():
    alts_dir = ALTS_DIR
    stock = []
    if os.path.isdir(alts_dir):
        for entry in os.listdir(alts_dir):
            full = os.path.join(alts_dir, entry)
            if not os.path.isdir(full):
                continue
            type_name = entry
            count = 0
            for root, dirs, files in os.walk(full):
                for f in files:
                    if os.path.isfile(os.path.join(root, f)):
                        count += 1
            stock.append([type_name, count])
    return stock
