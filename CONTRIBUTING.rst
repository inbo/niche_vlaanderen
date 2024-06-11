.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/inbo/niche_vlaanderen/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
and "help wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

niche_vlaanderen could always use more documentation, whether as part of the
official niche_vlaanderen docs, in docstrings, or even on the web in blog posts,
articles, and such. Note that on every documentation page there is a small "edit on Github" link in the top right - if you catch small errors, please suggest improvements.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/inbo/niche_vlaanderen/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `niche_vlaanderen` for local development.

1. Fork the `niche_vlaanderen` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/niche_vlaanderen.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv niche_vlaanderen
    $ cd niche_vlaanderen/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox::

    $ flake8 niche_vlaanderen tests
    $ python setup.py test or py.test
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for the supported versions listed in `setup.py <https://github.com/inbo/niche_vlaanderen/blob/master/setup.py>`_).
   Results of the automated tests can be found at: https://github.com/inbo/niche_vlaanderen/actions

.. note::
    Note that this are guidelines. If you are stuck while adding functionality
    - consider doing a pull request anyway, others may be able to help.

Tips
----

Releasing a new version
~~~~~~~~~~~~~~~~~~~~~~~
1. The version numbers of ``niche_vlaanderen`` are based on semver_: MAJOR.MINOR version. MAJOR versions can have incompatible API changes,
MINOR versions are backwards-compatible. Alpha and beta releases are made by appending a1/b1 to the version number, eg 1.0a10 for the 10th alpha release.

2. Before updating a version, make sure you run all notebooks (clear kernel and run all steps).

3. Finally, to update the version, edit the file `niche_vlaanderen/version.py <https://github.com/inbo/niche_vlaanderen/blob/master/setup.py>`_.

Building the documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~
The documentation for the project can be found under the ``docs/`` folder, and is written using
`reStructuredText`_.

To build the documentation locally, you need to install the doc requirements, which are based on sphinx_.

.. code-block:: bash

  $ pip install -r doc-requirements.txt

After which you should be able to generate HTML output by typing ``make html`` from the `docs` directory.

Publishing on the documentation website (https://inbo.github.io/niche_vlaanderen/ ) will happen when changes
to master build correctly (under github actions). Note that this may mean that the documentation is actually a bit more recent than the last released version.

.. _reStructuredText: https://docutils.sourceforge.net/rst.html
.. _sphinx: https://www.sphinx-doc.org/en/master/
.. _semver: https://semver.org/

