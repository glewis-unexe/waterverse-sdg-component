#
# pycharm: setup with bdist_wheel as argument
#

import setuptools
import shutil
import os

shutil.rmtree(os.getcwd()+'/build', ignore_errors=True)
shutil.rmtree(os.getcwd()+'/dist', ignore_errors=True)

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if '.png' in filename or '.geojson' in filename:
                pass
            else:
                paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('waterverse_sdg/data')



setuptools.setup(
    name='waterverse_sdg',
    version='1.0.0.1',
    author='Gareth Lewis',
    author_email='g.lewis2@exeter.ac.uk',
    description='SDG for WATERVERSE project',
    long_description='',
    long_description_content_type='text/markdown',
    url='https://github.com/pypa/sampleproject',
    # packages=setuptools.find_packages(),
    packages=['waterverse_sdg/.'],
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.13',
    package_data={'': extra_files },
)