#!/usr/bin/env python3

from setuptools import setup, Extension

setup(name='TelemXnet',
      version='0.1.0',
      description='Reliable networks for Unmanned Vehicles',
      author='Stephen Dade',
      author_email='stephen_dade@hotmail.com',
      url='http://www.TelemXnet.com',
      install_requires=['cobs', 'netifaces', 'construct'],
      test_suite="tests",
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3.0',
                   'Topic :: Scientific/Engineering'
                  ],
      license='GPLv3',
      py_modules=['TelemXnet.clienthub', 'TelemXnet.devicedict', 'TelemXnet.serverhub', 
                  'TelemXnet.udpxciever', 'TelemXnet.unipacket', 'TelemXnet.util'],
      scripts=['TelemXnet-Client.py', 'TelemXnet-Server.py']
     )
