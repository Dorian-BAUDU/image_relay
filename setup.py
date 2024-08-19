import os
from glob import glob
from setuptools import find_packages, setup

package_name = "image_relay"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/image_relay"],
        ),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Guilhem Saurel",
    maintainer_email="guilhem.saurel@laas.fr",
    description="Examples for m3t_tracker_ros package",
    license="BSD",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "image_relay = image_relay.image_relay:main",
        ],
    },
)
