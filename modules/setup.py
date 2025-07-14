from setuptools import setup, find_packages

setup(
    name="data_driven_generator",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'your-tool = your_module.cli:main'  # 用户安装后可通过 `your-tool` 命令调用
        ]
    }
)