from glob import glob
from setuptools import find_packages, setup

package_name = 'crisis_response'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'mock_scan = crisis_response.mock_scan:main',
        'scan_observer = crisis_response.scan_observer:main',
        'response_manager = crisis_response.response_manager:main',
        'experiment_logger = crisis_response.experiment_logger:main',
    ],
    },
)
