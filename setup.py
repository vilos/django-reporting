from setuptools import setup, find_packages

setup(
    name='django-reporting',
    version=__import__('reporting').__version__,
    description='django-reporting',
    long_description=open('README.TXT').read(),
    author='Vitaliy Kucheraviy, Rinat Shigapov',
    author_email='ppr.vitaly@gmail.com, rinatshigapov@gmail.com',
    url='https://github.com/DXist/django-reporting',
    download_url='git://github.com/DXist/django-reporting.git',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    tests_require=[
        'django==1.4',
    ],
    #test_suite='debug_toolbar.runtests.runtests',
    include_package_data=True,
    zip_safe=False, # because we're including media that Django needs
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
