import setuptools


setuptools.setup(
    name="colmap2deeparc",
    version="0.0.1",
    author="Pakkapon Phongthawee",
    author_email="pakkapon.p_s19@vistec.ac.th",
    description="create deeparc file from colmap db",
    url="https://github.com/pureexe/colmap2deeparc",
    packages=['tests','deeparc','colmap'],
    py_modules=['colmap2deeparc'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
     'console_scripts': ['colmap2deeparc=colmap2deeparc:entry_point'],
    },
    install_requires=[
        'numpy',
        'scipy'
    ],
    python_requires='>=3.6'
)