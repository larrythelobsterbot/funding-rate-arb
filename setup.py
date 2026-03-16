from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

requirements.append('gmx_python_sdk @ git+https://github.com/50shadesofgwei/gmx_python_sdk_custom.git@main')

setup(
    name='FundingRateArbitrage',
    version='0.4.0',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'project-run = Main.run:run',
            'project-run-demo = Main.run:demo',
            'close-position-pair = TxExecution.Master.run:main',
            'is-position-open = TxExecution.Master.run:is_position_open'
        ],
    },
    description='Delta-neutral funding rate arbitrage searcher',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='lekker.design',
    url='https://github.com/larrythelobsterbot/funding-rate-arb',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ]
)
