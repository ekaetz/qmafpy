from setuptools import setup, find_packages
import json
import os

# Read Version
version_file_name = 'build_version.json'
try:
    with open(version_file_name) as f:
        version_dict = json.load(f)
except:
    # Set to default value
    versionDict = {'major': 1, 'minor': 0, 'build': 1}

# Update Build
version_dict['build'] += 1

# Save Updated Version
try:
    with open(version_file_name, 'w') as f:
        json.dump(version_dict, f)
except:
    # Do nothing
    pass
build_ver_str = f"{version_dict['major']}.{version_dict['minor']}.{version_dict['build']}"

# Delete old Dist folders (prevent multiple .dist-info directories error)
try:
    os.rmdir("build")
    os.rmdir("dist")
except:
    pass  # Ignore errors

setup(
    name='qmafpy',
    version=build_ver_str,
    description='Queued Message Application Framework for Python',
    license='0BSD',
    packages=find_packages(),
    keywords='Application,Framework,Queue',
    author="Edward Kaetz",
    author_email='ekaetz@kwesteng.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
	    'License :: OBSD',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
	    'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    install_requires=[],
)

