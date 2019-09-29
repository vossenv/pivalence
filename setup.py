from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup_deps = [
          'pyinstaller',
          'wheel',
          'twine'
      ],

setup(name='piveilance',
      version='1.0.2',
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
      ],
      extras_require={
          ':sys_platform=="win32"': [
              'pyqt5',
              'pyqt5-sip'
          ],
          'setup': setup_deps,
      },
      setup_requires=setup_deps,
      entry_points={
          'console_scripts': [
              'piveilance = piveilance.app:main',
          ]
      },
      )

# python setup.py sdist bdist_wheel
# twine upload --repository testpypi dist/*.tar.gz dist/*.whl
#

