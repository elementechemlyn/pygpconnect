from setuptools import setup

setup(name='pygpconnect',
      version='0.1',
      description='Python Module for GPConnect',
      license='MIT',
      packages=['pygpconnect'],
      zip_safe=False,
      install_requires = [
          'asn1crypto',
          'attrs',
          'certifi',
          'cffi',
          'chardet',
          'idna',
          'pluggy',
          'py',
          'pyasn1',
          'pycparser',
          'pygpconnect',
          'PyJWT',
          'pytest',
          'requests',
          'six',
          'urllib3',
      ]
)
