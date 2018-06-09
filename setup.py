########################################################################################################################
# |||||||||||||||||||||||||||||||||||||||||||||||||| AQUITANIA ||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
# |||| To be a thinker means to go by the factual evidence of a case, not by the judgment of others |||||||||||||||||| #
# |||| As there is no group stomach to digest collectively, there is no group mind to think collectively. |||||||||||| #
# |||| Each man must accept responsibility for his own life, each must be sovereign by his own judgment. ||||||||||||| #
# |||| If a man believes a claim to be true, then he must hold to this belief even though society opposes him. ||||||| #
# |||| Not only know what you want, but be willing to break all established conventions to accomplish it. |||||||||||| #
# |||| The merit of a design is the only credential that you require. |||||||||||||||||||||||||||||||||||||||||||||||| #
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
########################################################################################################################

"""
.. moduleauthor:: H Roark
"""

import os
import re

from Cython.Build import cythonize
from setuptools import setup, find_packages, Extension


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath for dirpath, _, __ in os.walk(package) if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename) for filename in filenames])
    return {package: filepaths}


def get_cython_extensions():
    extension_list = []
    for x, y, z in os.walk('aquitania'):
        for filename in z:
            if '.pyx' == filename[-4:]:
                ext_name = '{}.{}'.format(x.replace('/', '.'), filename[:-4])
                include_dir = '{}/'.format(x)
                source = include_dir + filename
                extension_list.append(Extension(ext_name, [source], include_dirs=[include_dir]))
                print(ext_name,source,include_dir)

    return extension_list


version = get_version('aquitania')

try:
    import pypandoc

    readme = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    readme = ''

setup(
    name='aquitania',
    version=version,
    url='https://github.com/hroark-architect/aquitania',
    ext_modules=cythonize(get_cython_extensions()),
    zip_safe=False,  # Necessary to work with SetupTools
    license='MIT',
    long_description=readme,
    description='Algorithmic Trading with Artificial Intelligence',
    keywords='finance algorithmic trading ai artificial intelligence',
    author='Howard Roark',
    author_email='hroark.aquitania@gmail.com',
    packages=find_packages(),
    install_requires=['scikit-learn', 'numpy', 'pandas', 'oandapyV20', 'fxcmpy', 'requests', 'scipy', 'tables',
                      'matplotlib', 'jupyter', 'jupyterlab', 'memory_profiler', 'pytz', 'statsmodels'],
    python_requires='>=3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
)
