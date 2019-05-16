# shp2osmnx
# See full license in LICENSE.md

from setuptools import setup
from setuptools import find_packages


def readme():
    with open('README.md') as f:
        return f.read()


# list of classifiers
classifiers = ['Development Status :: 2 - Pre-Alpha',
               'License :: OSI Approved :: MIT License',
               'Operating System :: OS Independent',
               'Topic :: Scientific/Engineering :: GIS',
               'Topic :: Software Development :: Libraries',
               'Topic :: Scientific/Engineering :: Physics',
               'Topic :: Scientific/Engineering :: Visualization']

# now call setup
setup(name='shp2osmnx',
      version='0.2',
      description='Covert .shp files to OSM JSON to use in OSMnx',
      long_description=open('README.md').read(),
      url='https://github.com/jugrajsingh/shp2osmnx',
      classifiers=classifiers,
      license='MIT',
      author='Jugraj Singh',
      author_email='jugrajskhalsa@gmail.com',
      packages=find_packages(exclude=['tests']),
      test_suite='nose.collector',
      tests_require=['nose'],
      install_requires=['pyshp',
                        'osmnx',
                        'geopandas>=0.2.1',
                        'progressbar2'])
