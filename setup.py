from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pieveilance',
      version='1.0.1',
      description='PiCam Surveilance App',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[],
      url='https://github.com/vossenv/pieveilance',
      maintainer='Danimae Vossen',
      maintainer_email='vossen.dm@gmail.com',
      license='MIT',
      packages=find_packages(),
      package_data={
          'pieveilance': ['resources/*'],
      },
      install_requires=[
          'click',
          'requests',
      ],
      extras_require={
          ':sys_platform=="win32"': [
              'PyQt5'
          ]},
      entry_points={
          'console_scripts': [
              'pieveilance = pieveilance.app:main',
          ]
      },
      )

# python setup.py sdist bdist_wheel
# twine upload --repository testpypi dist/*.tar.gz dist/*.whl
# twine upload dist/*.tar.gz dist/*.whl

# test_deps = ['mock', 'pytest']
# extras_require = {
#     ':sys_platform=="win32"': [
#         'pywin32-ctypes',
#         'pywin32'
#     ],
#     'test': test_deps,
# },
# tests_require=test_deps,
