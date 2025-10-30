# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/check_dependencies.py
import importlib

required_packages = [
    'django',
    'rest_framework',
    'corsheaders',
    'pandas',
    'numpy',
    'sklearn',
    'joblib',
    'sqlalchemy',
    'openai',
]

print("检查项目依赖包...")
missing_packages = []

for package in required_packages:
    try:
        importlib.import_module(package)
        print(f"✅ {package}")
    except ImportError as e:
        missing_packages.append(package)
        print(f"❌ {package} - 错误: {e}")

if missing_packages:
    print(f"\n缺少的包: {missing_packages}")
    print("请运行: pip install " + " ".join(missing_packages))
else:
    print("\n✅ 所有必需的包都已安装!")