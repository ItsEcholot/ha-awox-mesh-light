from setuptools import setup

setup(name='ha-awox-mesh-light',
	version='0.1.0',
	author='Marc Berchtold',
	author_email='me@echolot.io',
	license='MIT',
	packages=['ha-awox-mesh-light'],
	install_requires=['awoxmeshlight', 'paho-mqtt']
	)
