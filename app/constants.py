import os

ROOT_DIR = os.path.abspath(os.curdir)
CONFIGMAP_PATH = os.getenv("configmap_path", f"{ROOT_DIR}/app/config/.env")
