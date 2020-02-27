import setuptools


with open("README.md", "r") as fh:
        long_description = fh.read()

setuptools.setup ( name = 'dbwidgets',
                   version = '0.0.1',
                   description = 'Database aware widgets for PySide2',
                   author = 'Ilker Manap',
                   author_email='ilkermanap@gmail.com',
                   long_description = long_description,
                   long_description_content_type="text/markdown",
                   url="https://github.com/ilkermanap/dbwidgets",
                   packages=setuptools.find_packages(),
                   install_requires=[
                           'PySide2','psycopg2-binary',
                   ],
                   classifiers=[
                           "Programming Language :: Python :: 3",
                           "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3)",
                           "Operating System :: OS Independent",
                   ],
                   
)

