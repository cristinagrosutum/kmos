#!/usr/bin/python
"""kMC modeling on steroids"""

from distutils.core import setup

maintainer = 'Max J. Hoffmann'
maintainer_email = 'mjhoffmann@gmail.com'
author = 'Max J. Hoffmann'
author_email = 'mjhoffmann@gmail.com'
description =  __doc__
classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Fortran',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
              ]
requires = [
                    'ase',
                    'cairo',
                    'gobject',
                    'goocanvas',
                    'gtk',
                    'kiwi',
                    'lxml',
                    'matplotlib',
                    'pygtk',
                   ]
license = 'COPYING'
long_description = file('README.rst').read()
name='python-kmos'
packages = [
           'kmos',
           'kmos.pygtkcanvas',
           ]
package_dir = {'kmos':'kmos'}
package_data = {'kmos':['fortran_src/*f90',
                        'kmc_editor.glade',
                        'fortran_src/assert.ppc',
                        'kmc_project_v0.2.dtd']}
platforms = ['linux']
scripts = [
        'tools/kmos-editor',
        'tools/kmos-export-program',
        'tools/kmos-build',
        'tools/kmos-view',
        'tools/kmos-build-standalone',
        'tools/kmos',
        'tools/kmos-install-dependencies-ubuntu',
        ]
url = 'https://github.com/mhoffman/kmos'
version = '0.1'

setup(
      author=author,
      author_email=author_email,
      description=description,
      #requires=requires,
      license=license,
      long_description=long_description,
      maintainer=maintainer,
      maintainer_email=maintainer_email,
      name=name,
      package_data=package_data,
      package_dir=package_dir,
      packages=packages,
      platforms=platforms,
      #requires=requires,
      scripts=scripts,
      url=url,
      version=version,
      )