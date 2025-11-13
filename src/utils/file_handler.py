"""
文件处理工具
"""
import json
import os
from typing import Any, Dict


def save_json(data: Any, file_path: str):
    """保存JSON文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(file_path: str) -> Any:
    """加载JSON文件"""
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_text(text: str, file_path: str):
    """保存文本文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


def load_text(file_path: str) -> str:
    """加载文本文件"""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def ensure_dir(dir_path: str):
    """确保目录存在"""
    os.makedirs(dir_path, exist_ok=True)
