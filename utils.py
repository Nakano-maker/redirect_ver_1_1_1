# utils.py

import uuid

def generate_session_id():
    return str(uuid.uuid4())

def generate_device_id(ip_address):
    return f"device-{ip_address}"

def redirect_batch(batch_size):
    # 任意のロジック（例：バッチ処理のトリガー）
    return batch_size
