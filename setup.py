import setuptools

setuptools.setup(
    name='forceAnalysis',
    version='0.1',
    author='Jojo',
    #py_modules=['lizardanalysis'],
    install_requires=[
        'Click', 'ipython', 'numpy', 'scipy', 'pandas', 'matplotlib', 'os', 'glob', 'tkinter',
        'tkFileDialog'
    ],
    packages=setuptools.find_packages(),
    data_files=[('forceAnalysis',['forceAnalysis/config.yaml'])],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        forceAnalysis=forceAnalysis:main
    ''',
)