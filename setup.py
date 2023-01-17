from setuptools import setup

setup(
    name='historicalFinancialData',
    version='0.1.0',
    description="A package for public companies' historical financial data",
    url='https://github.com/DanielMistrik/HistoricFinancialData',
    author='Daniel Mistrik',
    author_email='danielkomist@gmail.com',
    license='Apache 2.0 License',
    packages=['historicalFinancialData'],
    install_requires=['ratelimit', 'numpy', 'requests'],
    classifiers=[
        'Intended Audience :: Finance/Research/Academic',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
)