from distutils.core import setup

setup(
    name='neo_backend',
    version='1.0.0',
    packages=['neo_backend', 'neo_backend.components', 'neo_backend.components.commands'],
    url='',
    license='BSD',
    author='Robert Robinson',
    author_email='rerobins@meerkatlabs.org',
    description='Neo4j Connector for the Rho infrastructure',
    install_requires=['py2neo==2.0.7', 'rhobot==1.0.0']
)
