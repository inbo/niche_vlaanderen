from setuptools import setup

setup(name='niche_vlaanderen',
      version="0.0.1",
      description='NICHE Vlaanderen',
      url='https://github.com/INBO/niche_vlaanderen',
      author='Johan Van de Wauw',
      author_email='johan.vandewauw@inbo.be',
      license='MIT',
      install_requires=[
          'pandas',
          'numpy'
      ],
      classifiers=[
          'Development Status :: 1 - Planning',
          'Inteded Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5'
      ],
      include_package_data=True
)
