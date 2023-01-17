from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='historicalFinancialData',
    version='0.1.2',
    description="A package for public companies' historical financial data",
    url='https://github.com/DanielMistrik/HistoricFinancialData',
    author='Daniel Mistrik',
    author_email='danielkomist@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache 2.0 License',
    packages=['historicalFinancialData'],
    install_requires=['ratelimit', 'numpy', 'requests', 'pypandoc'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: Apache Software License',
        "Operating System :: OS Independent",
    ],
)
