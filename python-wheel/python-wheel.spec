## START: Set by rpmautospec
## (rpmautospec version 0.7.3)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 6;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

# The function of bootstrap is that it builds the package with flit_core.wheel
# and installs it by unzipping it.
# A real build uses %%pyproject_wheel and %%pyproject_install.
%bcond bootstrap 0
# Default: when bootstrapping -> disable tests
%bcond tests %{without bootstrap}

# Similar to what we have in pythonX.Y.spec files.
# If enabled, provides unversioned executables and other stuff.
# Disable it if you build this package in an alternative stack.
%bcond main_python 1

%global pypi_name wheel
%global python_wheel_name %{pypi_name}-%{version}-py3-none-any.whl

Name:           python-%{pypi_name}
Version:        0.45.1
Release:        %autorelease
Epoch:          1
Summary:        Built-package format for Python

# packaging is Apache-2.0 OR BSD-2-Clause
License:        MIT AND (Apache-2.0 OR BSD-2-Clause)
URL:            https://github.com/pypa/wheel
Source0: %{url}/archive/refs/tags/%{version}.tar.gz#/%{pypi_name}-%{version}.tar.gz
# This is used in bootstrap mode where we manually install the wheel and
# entrypoints
# Compatibility with the setuptools 75+
# https://github.com/pypa/wheel/issues/650
Patch:          https://github.com/pypa/wheel/commit/3028d3.patch
# Compatibility with the setuptools 78+ (PEP 639)
# Upstream has removed this code entirely instead
# https://github.com/pypa/wheel/pull/655
Patch:          adjusts-tests-for-setuptools-78.patch
BuildArch:      noarch

BuildRequires:  python%{python3_pkgversion}-devel
# python3 bootstrap: this is rebuilt before the final build of python3, which
# adds the dependency on python3-rpm-generators, so we require it manually
BuildRequires:  python3-rpm-generators

# Needed to manually build and unpack the wheel
%if %{with bootstrap}
BuildRequires:  python%{python3_pkgversion}-flit-core
BuildRequires:  unzip
%endif

%if %{with tests}
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  python%{python3_pkgversion}-setuptools
# several tests compile extensions
# those tests are skipped if gcc is not found
BuildRequires:  gcc
%endif

%global _description %{expand:
This is a command line tool for manipulating Python wheel files,
as defined in PEP 427. It contains the following functionality:

- Convert .egg archives into .whl.
- Unpack wheel archives.
- Repack wheel archives.
- Add or remove tags in existing wheel archives.}

%description %{_description}

# Virtual provides for the packages bundled by wheel.
# %%{_rpmconfigdir}/pythonbundles.py src/wheel/vendored/vendor.txt --namespace 'python%%{python3_pkgversion}dist'
%global bundled %{expand:
Provides: bundled(python%{python3_pkgversion}dist(packaging)) = 24
}


%package -n     python%{python3_pkgversion}-%{pypi_name}
Summary:        %{summary}
%{bundled}

%description -n python%{python3_pkgversion}-%{pypi_name} %{_description}


%package -n     %{python_wheel_pkg_prefix}-%{pypi_name}-wheel
Summary:        The Python wheel module packaged as a wheel
%{bundled}

%description -n %{python_wheel_pkg_prefix}-%{pypi_name}-wheel
A Python wheel of wheel to use with virtualenv.


%prep
%autosetup -n %{pypi_name}-%{version} -p1


%if %{without bootstrap}
%generate_buildrequires
%pyproject_buildrequires
%endif


%build
%if %{with bootstrap}
%global _pyproject_wheeldir dist
%python3 -m flit_core.wheel
%else
%pyproject_wheel
%endif


%install
# pip is not available when bootstrapping, so we need to unpack the wheel and
# create the entrypoints manually.
%if %{with bootstrap}
mkdir -p %{buildroot}%{python3_sitelib}
unzip %{_pyproject_wheeldir}/%{python_wheel_name} \
    -d %{buildroot}%{python3_sitelib} -x wheel-%{version}.dist-info/RECORD
install -Dpm 0755 %{SOURCE1} %{buildroot}%{_bindir}/wheel
%py3_shebang_fix %{buildroot}%{_bindir}/wheel
%else
%pyproject_install
%endif

mv %{buildroot}%{_bindir}/%{pypi_name}{,-%{python3_version}}
%if %{with main_python}
ln -s %{pypi_name}-%{python3_version} %{buildroot}%{_bindir}/%{pypi_name}-3
ln -s %{pypi_name}-3 %{buildroot}%{_bindir}/%{pypi_name}
%endif

mkdir -p %{buildroot}%{python_wheel_dir}
install -p %{_pyproject_wheeldir}/%{python_wheel_name} -t %{buildroot}%{python_wheel_dir}


%check
%{_rpmconfigdir}/pythonbundles.py src/wheel/vendored/vendor.txt --namespace 'python%{python3_pkgversion}dist' --compare-with '%{bundled}'

# Smoke test
%{py3_test_envvars} wheel-%{python3_version} version
%py3_check_import wheel

%if %{with tests}
%pytest -v --ignore build
%endif

%files -n python%{python3_pkgversion}-%{pypi_name}
%license LICENSE.txt
%doc README.rst
%{_bindir}/%{pypi_name}-%{python3_version}
%if %{with main_python}
%{_bindir}/%{pypi_name}
%{_bindir}/%{pypi_name}-3
%endif
%{python3_sitelib}/%{pypi_name}*/

%files -n %{python_wheel_pkg_prefix}-%{pypi_name}-wheel
%license LICENSE.txt
# we own the dir for simplicity
%dir %{python_wheel_dir}/
%{python_wheel_dir}/%{python_wheel_name}

%changelog
## START: Generated by rpmautospec
* Wed Apr 16 2025 Miro Hrončok <miro@hroncok.cz> - 1:0.45.1-5
- Fix tests compatibility with setuptools 78+ (PEP 639)

* Sun Mar 16 2025 Lumir Balhar <lbalhar@redhat.com> - 1:0.45.1-4
- Fix tests compatibility with setuptools 75+

* Sat Jan 18 2025 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.45.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Wed Dec 11 2024 Tomáš Hrnčiar <thrnciar@redhat.com> - 1:0.45.1-1
- Update to 0.45.1

* Thu Nov 07 2024 Miro Hrončok <miro@hroncok.cz> - 1:0.44.0-2
- CI: Update the list of tests
- Remove retired Pythons
- Add Python 3.14
- Remove virtualenv test for 3.6 as virtualenv in F42+ no longer supports
  3.6

* Mon Aug 26 2024 Miro Hrončok <miro@hroncok.cz> - 1:0.44.0-1
- Update to 0.44.0
- Fixes: rhbz#2302718

* Fri Jul 19 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.43.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Fri Jun 07 2024 Python Maint <python-maint@redhat.com> - 1:0.43.0-3
- Rebuilt for Python 3.13

* Thu Jun 06 2024 Python Maint <python-maint@redhat.com> - 1:0.43.0-2
- Bootstrap for Python 3.13

* Tue Apr 09 2024 Charalampos Stratakis <cstratak@redhat.com> - 1:0.43.0-1
- Rebase to 0.43.0
- Resolves: rhbz#2247012

* Fri Jan 26 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.41.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Mon Jan 22 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.41.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Tue Aug 15 2023 Tomáš Hrnčiar <thrnciar@redhat.com> - 1:0.41.2-1
- Update to 0.41.2
- Fixes: rhbz#2224712
- Fixes: rhbz#2233485

* Fri Jul 21 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.40.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Fri Jun 16 2023 Python Maint <python-maint@redhat.com> - 1:0.40.0-3
- Rebuilt for Python 3.12

* Tue Jun 13 2023 Python Maint <python-maint@redhat.com> - 1:0.40.0-2
- Bootstrap for Python 3.12

* Tue Mar 14 2023 Maxwell G <maxwell@gtmx.me> - 1:0.40.0-1
- Update to 0.40.0. Fixes rhbz#2178246.

* Fri Jan 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.38.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Wed Dec 07 2022 Lumír Balhar <lbalhar@redhat.com> - 1:0.38.4-1
- Update to 0.38.4 (rhbz#2136627)

* Fri Jul 22 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.37.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Mon Jun 13 2022 Python Maint <python-maint@redhat.com> - 1:0.37.1-3
- Rebuilt for Python 3.11

* Mon Jun 13 2022 Python Maint <python-maint@redhat.com> - 1:0.37.1-2
- Bootstrap for Python 3.11

* Wed Mar 09 2022 Tomas Orsava <torsava@redhat.com> - 1:0.37.1-1
- Update to 0.37.1
- Fixes: rhbz#2034895

* Fri Jan 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.37.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Tue Aug 17 2021 Karolina Surma <ksurma@redhat.com> - 1:0.37.0-1
- Update to 0.37.0
- Fixes: rhbz#1991740

* Tue Jul 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.36.2-5
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Wed Jun 02 2021 Python Maint <python-maint@redhat.com> - 1:0.36.2-4
- Rebuilt for Python 3.10

* Tue Jun 01 2021 Python Maint <python-maint@redhat.com> - 1:0.36.2-3
- Bootstrap for Python 3.10

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.36.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jan 04 2021 Miro Hrončok <mhroncok@redhat.com> - 1:0.36.2-1
- Update to 0.36.2
- Fixes: rhbz#1907227
- Fixes: rhbz#1899553

* Thu Sep 10 2020 Tomas Hrnciar <thrnciar@redhat.com> - 1:0.35.1-1
- Update to 0.35.1
- Fixes: rhbz#1868821

* Mon Aug 10 2020 Miro Hrončok <mhroncok@redhat.com> - 1:0.34.2-1
- Update to 0.34.2
- Drops Python 3.4 support
- Fixes: rhbz#1795134

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.33.6-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri May 22 2020 Miro Hrončok <mhroncok@redhat.com> - 1:0.33.6-5
- Rebuilt for Python 3.9

* Thu May 21 2020 Miro Hrončok <mhroncok@redhat.com> - 1:0.33.6-4
- Bootstrap for Python 3.9

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.33.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Sep 09 2019 Miro Hrončok <mhroncok@redhat.com> - 1:0.33.6-2
- Drop python2-wheel

* Tue Aug 27 2019 Miro Hrončok <mhroncok@redhat.com> - 1:0.33.6-1
- Update to 0.33.6 (#1708194)
- Don't add the m ABI flag to wheel names on Python 3.8

* Thu Aug 15 2019 Miro Hrončok <mhroncok@redhat.com> - 1:0.33.1-5
- Rebuilt for Python 3.8

* Wed Aug 14 2019 Miro Hrončok <mhroncok@redhat.com> - 1:0.33.1-4
- Bootstrap for Python 3.8

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.33.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Jul 16 2019 Miro Hrončok <mhroncok@redhat.com> - 1:0.33.1-2
- Make /usr/bin/wheel Python 3

* Mon Feb 25 2019 Charalampos Stratakis <cstratak@redhat.com> - 1:0.33.1-1
- Update to 0.33.1

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.32.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sun Sep 30 2018 Miro Hrončok <mhroncok@redhat.com> - 1:0.32.0-1
- Update to 0.32.0

* Wed Aug 15 2018 Miro Hrončok <mhroncok@redhat.com> - 1:0.31.1-3
- Create python-wheel-wheel package with the wheel of wheel

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.31.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Sat Jul 07 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1:0.31.1-1
- Update to 0.31.1

* Mon Jun 18 2018 Miro Hrončok <mhroncok@redhat.com> - 1:0.30.0-3
- Rebuilt for Python 3.7

* Wed Jun 13 2018 Miro Hrončok <mhroncok@redhat.com> - 1:0.30.0-2
- Bootstrap for Python 3.7

* Fri Feb 23 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1:0.30.0-1
- Update to 0.30.0

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.30.0a0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Aug 29 2017 Tomas Orsava <torsava@redhat.com> - 0.30.0a0-8
- Switch macros to bcond's and make Python 2 optional to facilitate building
  the Python 2 and Python 3 modules

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.30.0a0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.30.0a0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 03 2017 Charalampos Stratakis <cstratak@redhat.com> - 0.30.0a0-5
- Enable tests

* Fri Dec 09 2016 Charalampos Stratakis <cstratak@redhat.com> - 0.30.0a0-4
- Rebuild for Python 3.6 without tests

* Tue Dec 06 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.30.0a0-3
- Add bootstrap method

* Mon Sep 19 2016 Charalampos Stratakis <cstratak@redhat.com> - 0.30.0a0-2
- Use the python_provide macro

* Mon Sep 19 2016 Charalampos Stratakis <cstratak@redhat.com> - 0.30.0a0-1
- Update to 0.30.0a0
- Added patch to remove keyrings.alt dependency

* Wed Aug 10 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.29.0-1
- Update to 0.29.0
- Cleanups and fixes

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.26.0-3
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.26.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Oct 13 2015 Robert Kuska <rkuska@redhat.com> - 0.26.0-1
- Update to 0.26.0
- Rebuilt for Python3.5 rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.24.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jan 13 2015 Slavek Kabrda <bkabrda@redhat.com> - 0.24.0-3
- Make spec buildable in EPEL 6, too.
- Remove additional sources added to upstream tarball.

* Sat Jan 03 2015 Matej Cepl <mcepl@redhat.com> - 0.24.0-2
- Make python3 conditional (switched off for RHEL-7; fixes #1131111).

* Mon Nov 10 2014 Slavek Kabrda <bkabrda@redhat.com> - 0.24.0-1
- Update to 0.24.0
- Remove patches merged upstream

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.22.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Apr 25 2014 Matej Stuchlik <mstuchli@redhat.com> - 0.22.0-3
- Another rebuild with python 3.4

* Fri Apr 18 2014 Matej Stuchlik <mstuchli@redhat.com> - 0.22.0-2
- Rebuild with python 3.4

* Thu Nov 28 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 0.22.0-1
- Initial package.

## END: Generated by rpmautospec
