%global python3_pkgversion 3.12

# when bootstrapping, we cannot yet use sphinx and pytest
%bcond_with docs
%bcond_with tests

Name:           python-pygments
Version:        2.19.1
Release:        2%{?dist}
Summary:        Syntax highlighting engine written in Python

License:        BSD-2-Clause
URL:            https://pygments.org/
Source0:        %{pypi_source pygments}
Source1:        setup.cfg
Source2:        setup.py

BuildArch:      noarch

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-rpm-macros
BuildRequires:  python%{python3_pkgversion}-setuptools
%if %{with tests}
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  python%{python3_pkgversion}-lxml
%endif
%if %{with docs}
BuildRequires:  python%{python3_pkgversion}-sphinx
%endif
%if %{with docs} || %{with tests}
BuildRequires:  python%{python3_pkgversion}-wcag-contrast-ratio
BuildRequires:  make
%endif


%global _description %{expand:
Pygments is a generic syntax highlighter suitable for use in code hosting,
forums, wikis or other applications that need to prettify source code.

Highlights are:

 * a wide range of over 500 languages and other text formats is supported
 * special attention is paid to details that increase highlighting quality
 * support for new languages and formats are added easily;
   most languages use a simple regex-based lexing mechanism
 * a number of output formats is available, among them HTML, RTF, LaTeX
   and ANSI sequences
 * it is usable as a command-line tool and as a library}

%description %_description


%package -n python%{python3_pkgversion}-pygments
Summary:        %{summary}
Provides:       pygmentize = %{?epoch:%{epoch}:}%{version}-%{release}

%description -n python%{python3_pkgversion}-pygments %_description


%prep
%autosetup -p1 -n pygments-%{version}


#%%generate_buildrequires
#%%pyproject_buildrequires


%build
cp %{SOURCE1} %{SOURCE2} .
%py3_build


%install
%py3_install
mv %{buildroot}%{_bindir}/pygmentize %{buildroot}%{_bindir}/pygmentize-%{python3_pkgversion}
#%%pyproject_save_files pygments

%if %{with docs}
%make_build -C doc html
rm doc/_build/html/.buildinfo
rm -rf doc/_build/html/_sources
install doc/pygmentize.1 -Dt %{buildroot}%{_mandir}/man1/
chmod -x %{buildroot}%{_mandir}/man1/*.1
%endif


%if %{with tests}
%check
make test PYTHON=%{python3}
%endif


%files -n python%{python3_pkgversion}-pygments
%doc AUTHORS CHANGES
%license LICENSE
%{_bindir}/pygmentize-%{python3_pkgversion}
%{python3_sitelib}/pygments/
%{python3_sitelib}/Pygments-*.egg-info/
%if %{with docs}
%lang(en) %{_mandir}/man1/pygmentize.1*
%doc doc/_build/html
%endif


%changelog
* Sat May 24 2025 Michael Lampe - 2.19.1-2
- Rebuilt for Python 3.12

* Tue Jan  7 2025 Michael Lampe - 2.19.1-1
- Update to 2.19.1

* Fri Dec  6 2024 Michael Lampe - 2.18.0-1
- Update to 2.18.0

* Sun Mar 17 2024 Charalampos Stratakis <cstratak@redhat.com> - 2.14.0-2
- Security fix for CVE-2022-40896
- Fixes: rhbz#2259082

* Mon Jan 30 2023 Parag Nemade <pnemade AT redhat DOT com> - 2.14.0-1
- Update to 2.14.0 (#2157264)
- Update license tag to SPDX expression

* Fri Jan 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 2.13.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Wed Sep 07 2022 Karolina Surma <ksurma@redhat.com> - 2.13.0-1
- Update to 2.13.0
- Fixes: rhbz#2118377

* Fri Jul 22 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.12.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Mon Jun 13 2022 Python Maint <python-maint@redhat.com> - 2.12.0-3
- Rebuilt for Python 3.11

* Mon Jun 13 2022 Python Maint <python-maint@redhat.com> - 2.12.0-2
- Bootstrap for Python 3.11

* Mon May 02 2022 Charalampos Stratakis <cstratak@redhat.com> - 2.12.0-1
- Update to 2.12.0
- Fixes: rhbz#2078223

* Fri Feb 11 2022 Karolina Surma <ksurma@redhat.com> - 2.11.2-1
- Update to 2.11.2
- Fixes: rhbz#2036218

* Fri Jan 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.10.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Aug 16 2021 Miro Hrončok <mhroncok@redhat.com> - 2.10.0-1
- Update to 2.10.0
- Fixes: rhbz#1993673

* Fri Jul 23 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Fri Jun 11 2021 Karolina Surma <ksurma@redhat.com> - 2.9.0-1
- Update to 2.9.0 (rhbz#1956417)

* Thu Jun 03 2021 Petr Viktorin <pviktori@redhat.com> - 2.8.1-4
- Remove test files with a no-nuclear license from the sources

* Wed Jun 02 2021 Python Maint <python-maint@redhat.com> - 2.8.1-3
- Rebuilt for Python 3.10

* Wed Jun 02 2021 Python Maint <python-maint@redhat.com> - 2.8.1-2
- Bootstrap for Python 3.10

* Wed Mar 10 2021 Charalampos Stratakis <cstratak@redhat.com> - 2.8.1-1
- Update to 2.8.1 (rhbz#1928510)

* Fri Jan 29 2021 Tomas Hrnciar <thrnciar@redhat.com> - 2.7.4-1
- Update to 2.7.4

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Nov 25 2020 Petr Viktorin <pviktori@redhat.com> - 2.7.2-1
- Update to 2.7.2

* Mon Oct 12 2020 Tomas Hrnciar <thrnciar@redhat.com> - 2.7.1-1
- Update to 2.7.1

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri May 22 2020 Miro Hrončok <mhroncok@redhat.com> - 2.6.1-3
- Rebuilt for Python 3.9

* Fri May 22 2020 Miro Hrončok <mhroncok@redhat.com> - 2.6.1-2
- Bootstrap for Python 3.9

* Tue May 19 2020 Miro Hrončok <mhroncok@redhat.com> - 2.6.1-1
- Update to 2.6.1 (#1776922)

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Nov 15 2019 Miro Hrončok <mhroncok@redhat.com> - 2.4.2-6
- Subpackage python2-pygments has been removed
  See https://fedoraproject.org/wiki/Changes/RetirePython2

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 2.4.2-5
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Thu Aug 15 2019 Miro Hrončok <mhroncok@redhat.com> - 2.4.2-4
- Rebuilt for Python 3.8

* Thu Aug 15 2019 Miro Hrončok <mhroncok@redhat.com> - 2.4.2-3
- Bootstrap for Python 3.8

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jul 10 2019 Kevin Fenzi <kevin@scrye.com> - 2.4.2-1
- Update to 2.4.2. Fixes bug #1707945

* Tue Mar 12 2019 Miro Hrončok <mhroncok@redhat.com> - 2.3.1-1
- Update to 2.3.1

* Mon Mar 11 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.2.0-17
- Use python3-sphinx to build docs

* Tue Feb 26 2019 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.2.0-16
- Add missing setuptools Requires

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.0-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.0-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jul 04 2018 Miro Hrončok <mhroncok@redhat.com> - 2.2.0-13
- Run tests
- Add fix for 3.7

* Thu Jun 14 2018 Miro Hrončok <mhroncok@redhat.com> - 2.2.0-12
- Rebuilt for Python 3.7

* Mon Mar 19 2018 Steve Milner <smilner@redhat.com> - 2.2.0-11
- Added import-directive.patch to work around a change in sphinx.

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Sep 29 2017 Troy Dawson <tdawson@redhat.com> - 2.2.0-9
- Cleanup spec file conditionals

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Mar 23 2017 Steve Milner <smilner@redhat.com> - 2.2.0-7
- Fixed python2 sitelib in files section.

* Wed Mar 22 2017 Steve Milner <smilner@redhat.com> - 2.2.0-6
- Dropped python26 support.
- Spec clean up

* Mon Mar 20 2017 Steve Milner <smilner@redhat.com> - 2.2.0-5
- Updated for standards per BZ#1433650

* Mon Mar  6 2017 Steve Milner <smilner@redhat.com> - 2.2.0-4
- Added conflict per BZ#1429075

* Mon Mar  6 2017 Steve Milner <smilner@redhat.com> - 2.2.0-3
- Python3 package now houses the pygmentize binary
- Fixed Source0 url to point to pypi.org
- Made python3-nose a hard BuildRequirement for python3

* Thu Mar  2 2017 Steve Milner <smilner@redhat.com> - 2.2.0-2
- Update bin to come back into line with Fedora standards

* Thu Mar  2 2017 Steve Milner <smilner@redhat.com> - 2.2.0-1
- Update for upstream release.

* Thu Mar  2 2017 Steve Milner <smilner@redhat.com> - 2.1.3-5
- Split bin between versions.

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Dec 12 2016 Charalampos Stratakis <cstratak@redhat.com> - 2.1.3-3
- Rebuild for Python 3.6
- Don't make rpmbuild fail on failed tests for now

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.3-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Fri Mar  4 2016 Steve Milner <smilner@redhat.com> - 2.1.3-1
- Update for upstream release.

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Nov 12 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Thu Oct 29 2015 Steve Milner <smilner@redhat.com> - 2.0.2-3
- Backport patch to fix font manager shell injection for BZ#1276321

* Mon Oct 12 2015 Robert Kuska <rkuska@redhat.com> - 2.0.2-2
- Rebuilt for Python3.5 rebuild
- Also remove python3-sphinx from BR as docs are built only with python2-sphinx

* Mon Aug 24 2015 Steve Milner <smilner@redhat.com> - 2.0.2-1
- update for upstream release.
- Added python-pygments/python3-pygments to BuildRequires.

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat May 10 2014 Orion Poplawski <orion@cora.nwra.com> - 1.6-2
- Rebuild for Python 3.4

* Tue Nov 26 2013 Steve Milner <smilner@fedoraproject.org> - 1.6-1
- update for upstream release.

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Aug 04 2012 David Malcolm <dmalcolm@redhat.com> - 1.4-7
- rebuild for https://fedoraproject.org/wiki/Features/Python_3.3

* Fri Aug  3 2012 David Malcolm <dmalcolm@redhat.com> - 1.4-6
- remove rhel logic from with_python3 conditional

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Sep 13 2011 Toshio Kuratomi <toshio@fedoraproject.org> - 1.4-3
- Really enable the python3 unittests.
- Fix python26 byte compilation (thanks to Jeffrey Ness)

* Sat Sep 10 2011 Toshio Kuratomi <toshio@fedoraproject.org> - 1.4-2
- Fix python main package having dependencies for the python2.6 subpackage
- Fix places that used the default python instead of python26
- Attempt to make byte compilation more robust in case we add python3 to EPEL5
- Run unittests on python3 in F15+

* Fri Jun 24 2011 Steve Milner <smilner@fedoraproject.org> - 1.4-1
- update for upstream release
- Add python2.6 support done by Steve Traylen <steve.traylen@cern.ch>. BZ#662755.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Aug 25 2010 Thomas Spura <tomspur@fedoraproject.org> - 1.3.1-7
- update to most recent python guidelines
- rebuild with python3.2
  http://lists.fedoraproject.org/pipermail/devel/2010-August/141368.html

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 1.3.1-6
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Thu May  6 2010 Gareth Armstrong <gareth.armstrong@hp.com> - 1.3.1-5
- Enforce that Pygments requires Python 2.4 or later via an explicit BR
- Minor tweaks to spec file
- Deliver html and reST doc files to specifically named directories
- Align description with that of http://pygments.org/
- Add %%check section for Python2 and add BR on python-nose

* Fri Apr 23 2010 Steve 'Ashcrow' Milner <me@stevemilner.org> - 1.3.1-4
- switched with_python3 back to 1

* Fri Apr 23 2010 David Malcolm <dmalcolm@redhat.com> - 1.3.1-3
- add python3 subpackage (BZ#537244), ignoring soft-dep on imaging for now

* Tue Apr 13 2010 Steve 'Ashcrow' Milner <me@stevemilner.org> - 1.3.1-2
- added python-imaging as a dependency per BZ#581663.

* Sat Mar  6 2010 Steve 'Ashcrow' Milner <me@stevemilner.org> - 1.3.1-1
- Updated for release.

* Tue Sep 29 2009 Steve 'Ashcrow' Milner <me@stevemilner.org> - 1.1.1-1
- Updated for release.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Dec 21 2008 Steve 'Ashcrow' Milner <me@stevemilner.org> - 1.0-3
- Updated for release.

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.0-2
- Rebuild for Python 2.6

* Thu Nov 27 2008 Steve 'Ashcrow' Milner <me@stevemilner.org> - 1.0-1
- Updated for upstream 1.0.

* Sun Sep 14 2008 Steve 'Ashcrow' Milner <me@stevemilner.org> - 0.11.1-1
- Updated for upstream 0.11.

* Mon Jul 21 2008 Steve 'Ashcrow' Milner <me@stevemilner.org> - 0.10-1
- Updated for upstream 0.10.

* Thu Nov 29 2007 Steve 'Ashcrow' Milner <me@stevemilner.org> - 0.9-2
- Added python-setuptools as a Requires per bz#403601.

* Mon Nov 12 2007 Steve 'Ashcrow' Milner <me@stevemilner.org> - 0.9-1
- Updated for upstream 0.9.

* Fri Aug 17 2007 Steve 'Ashcrow' Milner <me@stevemilner.org> - 0.8.1-2
- Removed the dos2unix build dependency.

* Thu Jun 28 2007 Steve 'Ashcrow' Milner <me@stevemilner.org> - 0.8.1-1
- Initial packaging for Fedora.
