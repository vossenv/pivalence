from setuptools import setup, find_packages
from piveilance._version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup_deps = [
          'pyinstaller',
          'wheel',
          'twine'
      ],

test_deps = ['pytest']

setup(name='piveilance',
      version=__version__,
      description='PiCam Surveilance App',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[],
      url='https://github.com/vossenv/piveilance',
      maintainer='Danimae Vossen',
      maintainer_email='vossen.dm@gmail.com',
      license='MIT',
      packages=find_packages(),
      package_data={
          'piveilance': ['resources/*'],
      },
      install_requires=[
          'click',
          'requests',
          'python_dateutil',
          'click-default-group',
      ],
      extras_require={
          ':sys_platform=="win32"': [
              'pyqt5',
              'pyqt5-sip'
          ],
          'setup': setup_deps,
      },
      setup_requires=setup_deps,
      tests_require=test_deps,
      entry_points={
          'console_scripts': [
              'piveilance = piveilance.app:cli',
          ]
      },
      )
