#define prerelease rc1

# We need avoid oython byte compiler to not crash over template .py file which
# is not a valid python file, only for the IDE
%global _python_bytecompile_errors_terminate_build 0

Name:           qt-creator
Version:        8.0.2
Release:        9%{?dist}
Summary:        Cross-platform IDE for Qt

License:        GPLv3 with exceptions
URL:            https://www.qt.io/ide/
Source0:        https://download.qt.io/%{?prerelease:development}%{?!prerelease:official}_releases/qtcreator/8.0/%{version}%{?prerelease:-%prerelease}/qt-creator-opensource-src-%{version}%{?prerelease:-%prerelease}.tar.xz

Source1:        qt-creator-Fedora-privlibs

# In Fedora, the ninja command is called ninja-build
Patch0:         qt-creator_ninja-build.patch
# Fix leading whitespace in desktop file
Patch1:         qt-creator_desktop.patch
# Limit qmake names to avoid the rpm macro wrapper qmake-qt5.sh getting picked up (#1644989)
Patch2:         qt-creator_qmake-names.patch
# Don't depend on non-existing (?) target clangTooling for ClangFormat plugin
Patch3:         qt-creator_clang.patch
# Fix path to clang includes
Patch4:         qt-creator_clangtools.patch

BuildRequires:  chrpath
BuildRequires:  clang-devel
BuildRequires:  cmake
#BuildRequires:  cmake(KF5SyntaxHighlighting)
BuildRequires:  cmake(Qt5Concurrent)
BuildRequires:  cmake(Qt5Core)
BuildRequires:  cmake(Qt5Gui)
BuildRequires:  cmake(Qt5Designer)
BuildRequires:  cmake(Qt5Help)
BuildRequires:  cmake(Qt5LinguistTools)
BuildRequires:  cmake(Qt5Network)
BuildRequires:  cmake(Qt5PrintSupport)
BuildRequires:  cmake(Qt5Qml)
BuildRequires:  cmake(Qt5QmlModels)
BuildRequires:  cmake(Qt5Quick)
BuildRequires:  cmake(Qt5SerialPort)
BuildRequires:  cmake(Qt5Sql)
BuildRequires:  cmake(Qt5Svg)
BuildRequires:  cmake(Qt5UiPlugin)
BuildRequires:  cmake(Qt5Widgets)
BuildRequires:  cmake(Qt5Xml)
BuildRequires:  desktop-file-utils
BuildRequires:  diffutils
BuildRequires:  elfutils-devel
BuildRequires:  libappstream-glib
BuildRequires:  llvm-devel
#BuildRequires:  litehtml-devel
BuildRequires:  ninja-build
BuildRequires:  python3
# tight dep on qt5-qtbase used to build, uses some private apis
BuildRequires:  qt5-qtbase-private-devel
BuildRequires:  systemd-devel
BuildRequires:  yaml-cpp-devel

Requires:       hicolor-icon-theme
Requires:       xdg-utils
Requires:       qt5-qtquickcontrols%{?_isa}

# we need qt-devel and gcc-c++ to compile programs using qt-creator
Requires:       qt5-qtbase-devel
Requires:       gcc-c++
Requires:       %{name}-data = %{version}-%{release}
# The ClangTools plugin hard-codes the path to the clang headers, i.e.
# $ strings /usr/lib64/qtcreator/plugins/libClangTools.so | grep /usr/lib/clang/
# /usr/lib/clang/18/include
#Requires:       clang-libs%{?_isa} = %(rpm -q --qf '%%{version}' clang-libs)
Requires:       /usr/lib/clang/20/include/stddef.h
Requires:       clang-resource-filesystem

Provides:       qtcreator = %{version}-%{release}

# long list of private shared lib names to filter out
%include %{SOURCE1}
%global __provides_exclude ^(%{privlibs})\.so
%global __requires_exclude ^(%{privlibs})\.so



%description
Qt Creator is a cross-platform IDE (integrated development environment)
tailored to the needs of Qt developers.


%package data
Summary:        Application data for %{name}
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description data
Application data for %{name}.


%package translations
Summary:        Translations for %{name}
Requires:       %{name}-data = %{version}-%{release}
Requires:       qt5-qttranslations
BuildArch:      noarch

%description translations
Translations for %{name}.


%package doc
Summary:        User documentation for %{name}
Requires:       %{name} = %{version}-%{release}
Requires:       qt5-qtdoc
BuildArch:      noarch

%description doc
User documentation for %{name}.


%prep
%autosetup -p1 -n qt-creator-opensource-src-%{version}%{?prerelease:-%prerelease}

# Remove some bundled libraries to be sure
rm -rf src/shared/qbs
#rm -rf src/plugins/help/qlitehtml/litehtml
#rm -rf src/libs/3rdparty/syntax-highlighting/src
rm -rf src/libs/3rdparty/yaml-cpp


%build
%cmake -G Ninja \
    -DBUILD_PLUGIN_CLANGREFACTORING=ON \
    -DBUILD_PLUGIN_CLANGPCHMANAGER=ON \
    -DWITH_DOCS=ON \
    -Djournald=ON \
    -DBUILD_DEVELOPER_DOCS=ON \
    -DCMAKE_INSTALL_LIBDIR=%{_lib}

%cmake_build
%cmake_build -- qch_docs


%install
%cmake_install
%cmake_install --component qch_docs


%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/org.qt-project.qtcreator.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/org.qt-project.qtcreator.appdata.xml
chrpath -l %{buildroot}%{_bindir}/qtcreator

# Output an up-to-date list of Provides/Requires exclude statements.
outfile=__Fedora-privlibs
i=0
sofiles=$(find %{buildroot}%{_libdir}/qtcreator -name \*.so\*|sed 's!^.*/\(.*\).so.*!\1!g'|sort|uniq)
for so in ${sofiles} ; do
    if [ $i == 0 ]; then
        echo "%%global privlibs $so" > $outfile
        i=1
    else
        echo "%%global privlibs %%{privlibs}|$so" >> $outfile
    fi
done
cat $outfile
# If there are differences, abort the build
diff -u %{SOURCE1} $outfile


%files
%doc README.md
%license LICENSE.GPL3-EXCEPT
%{_bindir}/qtcreator
%{_bindir}/qtcreator.sh
%{_libdir}/qtcreator
%{_libexecdir}/qtcreator/
%{_datadir}/applications/org.qt-project.qtcreator.desktop
%{_metainfodir}/org.qt-project.qtcreator.appdata.xml
%{_datadir}/icons/hicolor/*/apps/QtProject-qtcreator.png

%files data
%{_datadir}/qtcreator/
%exclude %{_datadir}/qtcreator/translations

%files translations
%{_datadir}/qtcreator/translations/

%files doc
# Please don't change this, it is where qt-creator expects the documentation to be!
%dir %{_defaultdocdir}/qtcreator/
%doc %{_defaultdocdir}/qtcreator/qtcreator.qch
%doc %{_defaultdocdir}/qtcreator/qtcreator-dev.qch


%changelog
* Sat May 24 2025 Michael Lampe - 8.0.2-9
- Rebuild for llvm 20.1.5

* Wed Dec 18 2024 Michael Lampe - 8.0.2-8
- require clang-libs without refering to the minor release number

* Thu Dec  5 2024 Michael Lampe - 8.0.2-7
- Rebuild for llvm 19.1.5

* Mon Jun 24 2024 Michael Lampe - 8.0.2-6
- Rebuild for llvm 18.1.8

* Fri Jun 14 2024 Michael Lampe - 8.0.2-5
- Rebuild for llvm 18.1.7

* Fri May 24 2024 Michael Lampe - 8.0.2-4
- Rebuild for llvm 18

* Fri Jan 19 2024 Michael Lampe - 8.0.2-3
- Rebuild for llvm 17
- Fix path to clang includes

* Thu Nov 16 2023 Thomas Zimmermann <thomas.zimmermann@voestalpine.com> - 8.0.2-2
- Rebuild for RHEL 8.9

* Thu Jul 27 2023 Thomas Zimmermann <thomas.zimmermann@voestalpine.com> - 8.0.2-1
- Update to 8.0.2

* Tue May 23 2023 Thomas Zimmermann <thomas.zimmermann@voestalpine.com> - 8.0.1-2
- Rebuild for RHEL 8.8

* Fri Jan 27 2023 Thomas Zimmermann <thomas.zimmermann@voestalpine.com> - 8.0.1-1
- Update to 8.0.1

* Thu Nov 24 2022 Thomas Zimmermann <thomas.zimmermann@voestalpine.com> - 7.0.2-2
- Rebuild for RHEL 8.7
- use bundled KF5SyntaxHighlighting and litehtml

* Tue May 24 2022 Sandro Mani <manisandro@gmail.com> - 7.0.2-1
- Update to 7.0.2

* Wed Apr 27 2022 Sandro Mani <manisandro@gmail.com> - 7.0.1-1
- Update to 7.0.1

* Mon Apr 04 2022 Frantisek Zatloukal <fzatlouk@redhat.com> - 7.0.0-3
- Rebuild for llvm14

* Mon Mar 28 2022 Jan Grulich <jgrulich@redhat.com>
- Rebuild (qt5)

* Thu Mar 24 2022 Sandro Mani <manisandro@gmail.com> - 7.0.0-1
- Update to 7.0.0

* Tue Mar 22 2022 Jan Grulich <jgrulich@redhat.com>
- Rebuild (qt5)

* Fri Mar 11 2022 Sandro Mani <manisandro@gmail.com> - 7.0.0-0.4.rc1
- Update to 7.0.0-rc1

* Tue Mar 08 2022 Jan Grulich <jgrulich@redhat.com>
- Rebuild (qt5)

* Fri Feb 25 2022 Sandro Mani <manisandro@gmail.com> - 7.0.0-0.2.beta2
- Update to 7.0.0-beta2

* Sat Feb 12 2022 Sandro Mani <manisandro@gmail.com> - 7.0.0-0.1.beta1
- Update to 7.0.0-beta1

* Fri Jan 21 2022 Sandro Mani <manisandro@gmail.com> - 6.0.2-1
- Update to 6.0.2

* Fri Jan 21 2022 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Thu Dec 16 2021 Sandro Mani <manisandro@gmail.com> - 6.0.1-1
- Update to 6.0.1

* Thu Dec 02 2021 Sandro Mani <manisandro@gmail.com> - 6.0.0-1
- Update to 6.0.0

* Thu Nov 11 2021 Sandro Mani <manisandro@gmail.com> - 6.0.0-0.4.rc1
- Update to 6.0.0-rc1

* Thu Oct 28 2021 Sandro Mani <manisandro@gmail.com> - 6.0.0-0.3.beta2
- Update to 6.0.0-beta2

* Thu Oct 14 2021 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.2.beta1
- Rebuild for llvm-13.0.0

* Thu Oct 14 2021 Sandro Mani <manisandro@gmail.com> - 6.0.0-0.1.beta1
- Update to 6.0.0-beta1

* Thu Oct 07 2021 Tom Stellard <tstellar@redhat.com> - 5.0.2-2
- Rebuild for llvm-13.0.0

* Sat Oct 02 2021 Sandro Mani <manisandro@gmail.com> - 5.0.2-1
- Update to 5.0.2

* Thu Sep 16 2021 Sandro Mani <manisandro@gmail.com> - 5.0.1-1
- Update to 5.0.1

* Tue Aug 31 2021 Sandro Mani <manisandro@gmail.com> - 5.0.0-5
- Require clang-resource-filesystem

* Fri Aug 27 2021 Sandro Mani <manisandro@gmail.com> - 5.0.0-4
- Require exact clang-libs version against which qt-creator was built (#1997204)

* Thu Aug 26 2021 Sandro Mani <manisandro@gmail.com> - 5.0.0-3
- Update to 5.0.0

* Thu Aug 12 2021 Sandro Mani <manisandro@gmail.com> - 5.0.0-2.rc1
- Update to 5.0.0-rc1

* Sun Jul 25 2021 Sandro Mani <manisandro@gmail.com> - 5.0.0-1.beta1
- Update to 5.0.0-beta1

* Fri Jul 23 2021 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Wed Jun 09 2021 Sandro Mani <manisandro@gmail.com> - 4.15.1-1
- Update to 4.15.1

* Wed May 05 2021 Sandro Mani <manisandro@gmail.com> - 4.15.0-1
- Update to 4.15.0

* Wed Apr 14 2021 Sandro Mani <manisandro@gmail.com> - 4.15.0-0.3.rc1
- Update to 4.15.0-rc1

* Wed Mar 31 2021 Jonathan Wakely <jwakely@redhat.com>
- Rebuilt for removed libstdc++ symbols (#1937698)

* Thu Mar 25 2021 Sandro Mani <manisandro@gmail.com> - 4.15.0-0.2.beta2
- Update to 4.15.0-beta2

* Wed Mar 24 2021 Sandro Mani <manisandro@gmail.com> - 4.15.0-0.1.beta1
- Update to 4.15.0-beta1

* Tue Mar 16 2021 Sandro Mani <manisandro@gmail.com> - 4.14.1-3
- Re-enable journald logging capture

* Tue Mar 09 2021 Rex Dieter <rdieter@fedoraproject.org> - 4.14.1-2
- fix rpath

* Thu Feb 25 2021 Sandro Mani <manisandro@gmail.com> - 4.14.1-1
- Update to 4.14.1

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan 22 2021 Tom Stellard <tstellar@redhat.com>
- Rebuild for clang-11.1.0

* Tue Dec 29 2020 Sandro Mani <manisandro@gmail.com> - 4.14.0-2
- Switch to cmake build
- Cleanup spec

* Tue Dec 22 2020 Sandro Mani <manisandro@gmail.com> - 4.14.0-1
- Update to 4.14.0

* Fri Nov 27 2020 Rex Dieter <rdieter@fedoraproject.org> - 4.14.0-0.4.beta1
- drop hard-coded Qt5 runtime dep

* Mon Nov 23 2020 Jan Grulich <jgrulich@redhat.com>
- rebuild (qt5)

* Wed Nov 04 2020 Sandro Mani <manisandro@gmail.com> - 4.14.0-0.2.beta1
- BR elfutils-devel for perparser

* Sun Nov 01 2020 Sandro Mani <manisandro@gmail.com> - 4.14.0-0.1.beta1
- Update to 4.14.0-beta1

* Tue Oct 20 2020 Jeff Law <law@redhat.com> - 4.13.2-2
- Fix various missing #includes for gcc-11

* Mon Oct 05 2020 Sandro Mani <manisandro@gmail.com> - 4.13.2-1
- Update to 4.13.2

* Thu Sep 17 2020 Sandro Mani <manisandro@gmail.com> - 4.13.1-1
- Update to 4.13.1

* Fri Sep 11 2020 Jan Grulich <jgrulich@redhat.com>
- rebuild (qt5)

* Tue Sep  8 2020 Sandro Mani <manisandro@gmail.com>
- Rebuild (qbs)

* Wed Aug 26 2020 Sandro Mani <manisandro@gmail.com> - 4.13.0-4
- Update to 4.13.0

* Thu Aug 13 2020 Sandro Mani <manisandro@gmail.com> - 4.13.0-3.rc1
- Update to 4.13.0-rc1

* Mon Jul 27 2020 Sandro Mani <manisandro@gmail.com> - 4.13.0-2.beta2
- Update to 4.13.0-beta2

* Mon Jul 13 2020 Sandro Mani <manisandro@gmail.com> - 4.13.0-1.beta1
- Update to 4.13.0-beta1

* Wed Jul 08 2020 Sandro Mani <manisandro@gmail.com> - 4.12.4-1
- Update to 4.12.4

* Tue Jun 30 2020 Sandro Mani <manisandro@gmail.com> - 4.12.3-2
- Enable journald support (#1846808)

* Wed Jun 17 2020 Sandro Mani <manisandro@gmail.com> - 4.12.3-1
- Update to 4.12.3

* Wed Jun 03 2020 Sandro Mani <manisandro@gmail.com> - 4.12.2-1
- Update to 4.12.2

* Thu May 28 2020 Sandro Mani <manisandro@gmail.com> - 4.12.1-2
- Also look for unsiffixed qmake

* Wed May 20 2020 Sandro Mani <manisandro@gmail.com> - 4.12.1-1
- Update to 4.12.1

* Thu May 07 2020 Sandro Mani <manisandro@gmail.com> - 4.12.0-2
- Rebuild (qbs)

* Fri Apr 24 2020 Sandro Mani <manisandro@gmail.com> - 4.12.0-1
- Update to 4.12.0

* Sun Apr 12 2020 Sandro Mani <manisandro@gmail.com> - 4.12.0-0.4-rc1
- Rebuild (qt5)

* Mon Apr 06 2020 Sandro Mani <manisandro@gmail.com> - 4.12.0-0.3.rc1
- Update to 4.12.0-rc1

* Mon Apr 06 2020 Rex Dieter <rdieter@fedoraproject.org> - 4.12.0-0.2.beta1
- rebuild (qt5)

* Thu Mar 19 2020 Sandro Mani <manisandro@gmail.com> - 4.12.0-0.2.beta2
- Update to 4.12.0-beta2

* Fri Mar 06 2020 Sandro Mani <manisandro@gmail.com> - 4.12.0-0.1.beta1
- Update to 4.12.0-beta1

* Thu Feb 06 2020 Sandro Mani <manisandro@gmail.com> - 4.11.1-1
- Update to 4.11.1

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Jan 06 2020 Tom Stellard <tstellar@redhat.com> - 4.11.0-4
- Link against libclang-cpp.so
- https://fedoraproject.org/wiki/Changes/Stop-Shipping-Individual-Component-Libraries-In-clang-lib-Package

* Mon Jan 06 2020 Sandro Mani <manisandro@gmail.com> - 4.11.0-3
- Rebuild (clang)

* Fri Dec 13 2019 Sandro Mani <manisandro@gmail.com> - 4.11.0-2
- Rebuild (qbs)

* Thu Dec 12 2019 Sandro Mani <manisandro@gmail.com> - 4.11.0-1
- Update to 4.11.0

* Mon Dec 09 2019 Jan Grulich <jgrulich@redhat.com> - 4.11.0-0.5.rc1
- rebuild (qt5)

* Fri Nov 29 2019 Sandro Mani <manisandro@gmail.com> - 4.11.0-0.4.rc1
- Update to 4.11.0-rc1

* Sun Nov 17 2019 Sandro Mani <manisandro@gmail.com> - 4.11.0-0.3.beta2
- Ensure kit autodetection picks up the correct qmake-qt* (#1644989)

* Mon Nov 04 2019 Sandro Mani <manisandro@gmail.com> - 4.11.0-0.2.beta2
- Update to 4.11.0-beta2

* Fri Oct 18 2019 Sandro Mani <manisandro@gmail.com> - 4.11.0-0.1.beta1
- Update to 4.11.0-beta1

* Thu Oct 10 2019 Sandro Mani <manisandro@gmail.com> - 4.10.1-2
- Rebuild (qbs)

* Tue Oct 08 2019 Sandro Mani <manisandro@gmail.com> - 4.10.1-1
- Update to 4.10.1

* Wed Sep 25 2019 Jan Grulich <jgrulich@redhat.com> - 4.10.0-7
- rebuild (qt5)
- Fix build against clang-9

* Thu Sep 05 2019 Sandro Mani <manisandro@gmail.com> - 4.10.0-6
- Update to 4.10.0

* Mon Aug 05 2019 Sandro Mani <manisandro@gmail.com> - 4.10.0-5.rc1
- Update to 4.10.0-rc1
- Switch to botan2

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Jun 28 2019 Sandro Mani <manisandro@gmail.com> - 4.10.0-3.beta1
- Update to 4.10.0-beta2

* Tue Jun 25 2019 Rex Dieter <rdieter@fedoraproject.org> - 4.10.0-2.beta1
- rebuild (qt5)

* Wed Jun 19 2019 Sandro Mani <manisandro@gmail.com> - 4.10.0-1.beta1
- Update to 4.10.0-beta1

* Mon Jun 17 2019 Jan Grulich <jgrulich@redhat.com>
- rebuild (qt5)

* Wed Jun 05 2019 Jan Grulich <jgrulich@redhat.com> - 4.9.1-2
- rebuild (qt5)

* Tue May 28 2019 Sandro Mani <manisandro@gmail.com> - 4.9.1-1
- Update to 4.9.1

* Tue Apr 16 2019 Sandro Mani <manisandro@gmail.com> - 4.9.0-2
- Rebuild (qbs)

* Mon Apr 15 2019 Sandro Mani <manisandro@gmail.com> - 4.9.0-1
- Update to 4.9.0

* Wed Mar 27 2019 Sandro Mani <manisandro@gmail.com> - 4.9.0-0.4-rc
- Update to 4.9.0-rc

* Thu Mar 07 2019 Sandro Mani <manisandro@gmail.com> - 4.9.0-0.3.beta2
- Update to 4.9.0-beta2

* Sun Mar 03 2019 Rex Dieter <rdieter@fedoraproject.org> - 4.9.0-0.2.beta1
- rebuild (qt5)

* Thu Feb 21 2019 Sandro Mani <manisandro@gmail.com> - 4.9.0-0.1.beta1
- Update to 4.9.0-beta1

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jan 17 2019 Sandro Mani <manisandro@gmail.com> - 4.8.1-1
- Update to 4.8.1

* Wed Dec 12 2018 Rex Dieter <rdieter@fedoraproject.org> - 4.8.0-2
- rebuild (qt5)

* Thu Dec 06 2018 Sandro Mani <manisandro@gmail.com> - 4.8.0-1
- Update to 4.8.0

* Sat Nov 24 2018 Sandro Mani <manisandro@gmail.com> - 4.8.0-0.3.rc1
- Update to 4.8.0-rc1

* Sat Nov 17 2018 Sandro Mani <manisandro@gmail.com> - 4.8.0-0.2.beta2
- Update to 4.8.0-beta2

* Thu Oct 11 2018 Sandro Mani <manisandro@gmail.com> - 4.8.0-0.1.beta1
- Update to 4.8.0-beta1

* Fri Sep 21 2018 Jan Grulich <jgrulich@redhat.com> - 4.7.1-2
- rebuild (qt5)

* Thu Sep 20 2018 Sandro Mani <manisandro@gmail.com> - 4.7.1-1
- Update to 4.7.1

* Wed Jul 18 2018 Sandro Mani <manisandro@gmail.com> - 4.7.0-1
- Update to 4.7.0

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jul 05 2018 Sandro Mani <manisandro@gamil.com> - 4.7.0-0.3.rc1
- Update to 4.7.0-rc1

* Thu Jun 21 2018 Sandro Mani <manisandro@gmail.com> - 4.7.0-0.2.beta2
- Update to 4.7.0-beta2

* Thu Jun 07 2018 Sandro Mani <manisandro@gmail.com> - 4.7.0-0.1.beta1
- Update to 4.7.0-beta1

* Mon May 28 2018 Rex Dieter <rdieter@fedoraproject.org> - 4.6.1-2
- rebuild (qt5)

* Mon May 07 2018 Sandro Mani <manisandro@gmail.com> - 4.6.1-1
- Update to 4.6.1

* Wed Mar 28 2018 Sandro Mani <manisandro@gmail.com> - 4.6.0-1
- Update to 4.6.0

* Fri Mar 16 2018 Sandro Mani <manisandro@gmail.com> - 4.6.0-0.3.rc1
- Update to 4.6.0-rc1

* Wed Feb 14 2018 Jan Grulich <jgrulich@redhat.com> - 4.6.0-0.2.beta1
- rebuild (qt5)

* Thu Feb 08 2018 Sandro Mani <manisandro@gmail.com> - 4.6.0-0.1.beta1
- Update to 4.6.0-beta1

* Sun Feb 04 2018 Sandro Mani <manisandro@gmail.com> - 4.5.0-4
- BR qt5-qtquickcontrols to enable qmldesigner

* Wed Jan 17 2018 Sandro Mani <manisandro@gmail.com> - 4.5.0-3
- Rebuild for broken dependencies on F27 (#1535355)

* Wed Dec 20 2017 Jan Grulich <jgrulich@redhat.com> - 4.5.0-2
- rebuild (qt5)

* Sat Dec 09 2017 Sandro Mani <manisandro@gmail.com> - 4.5.0-1
- Update to 4.5.0

* Mon Nov 27 2017 Rex Dieter <rdieter@fedoraproject.org> - 4.5.0-0.4.rc1
- rebuild (qt5)

* Wed Nov 22 2017 Sandro Mani <manisandro@gmail.com> - 4.5.0-0.3.rc1
- Update to 4.5.0-rc1

* Tue Oct 24 2017 Jan Grulich <jgrulich@redhat.com> - 4.5.0-0.2.beta1
- rebuild (llvm-5.0)

* Thu Oct 12 2017 Sandro Mani <manisandro@gmail.com> - 4.5.0-0.1.beta1
- Update to 4.5.0-beta1

* Tue Oct 10 2017 Rex Dieter <rdieter@fedoraproject.org> - 4.4.1-2
- rebuild (qt5)

* Thu Oct 05 2017 Sandro Mani <manisandro@gmail.com> - 4.4.1-1
- Update to 4.4.1

* Sun Sep 24 2017 Sandro Mani <manisandro@gmail.com> - 4.4.0-3
- Add QMAKE_CFLAGS_ISYSTEM=-I

* Sat Sep 23 2017 Sandro Mani <manisandro@gmail.com> - 4.4.0-2
- Fix libClangCodeModel not getting built (thanks Abrahm Scully)

* Tue Sep 05 2017 Sandro Mani <manisandro@gmail.com> - 4.4.0-1
- Update to 4.4.0

* Thu Aug 17 2017 Sandro Mani <manisandro@gmail.com> - 4.4.0-0.2.rc1
- Update to 4.4.0-rc1

* Mon Jul 31 2017 Sandro Mani <manisandro@gmail.com> - 4.4.0-0.1.beta1
- Update to 4.4.0-beta1
- Drop qbs subpackage, it now lives in a separate package

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 19 2017 Rex Dieter <rdieter@fedoraproject.org> - 4.3.1-2
- rebuild (qt5)

* Fri Jun 30 2017 Sandro Mani <manisandro@gmail.com> - 4.3.1-1
- Update to 4.3.1

* Sat May 27 2017 Sandro Mani <manisandro@gmail.com> - 4.3.0-1
- Update to 4.3.0

* Thu May 11 2017 Sandro Mani <manisandro@gmail.com> - 4.3.0-0.2.rc1
- Update to 4.3.0-rc1

* Sat Apr 01 2017 Sandro Mani <manisandro@gmail.com> - 4.3.0-0.1.beta1
- Update to 4.3.0-beta1

* Fri Mar 31 2017 Rex Dieter <rdieter@fedoraproject.org> - 4.2.1-5
- rebuild (qt5)

* Fri Mar 24 2017 Igor Gnatenko <ignatenko@redhat.com> - 4.2.1-4
- Rebuild for LLVM4

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 02 2017 Sandro Mani <manisandro@gmail.com> - 4.2.1-2
- Update qt-creator_appdata.patch

* Mon Jan 23 2017 Sandro Mani <manisandro@gmail.com> - 4.2.1-1
- Update to 4.2.1

* Wed Dec 14 2016 Sandro Mani <manisandro@gmail.com> - 4.2.0-1
- Update to 4.2.0

* Wed Nov 30 2016 Sandro Mani <manisandro@gmail.com> - 4.2.0-0.4.rc1
- Update to 4.2.0-rc1

* Fri Nov 25 2016 Sandro Mani <manisandro@gmail.com> - 4.2.0-0.3.beta1
- Backport: Fix potential null pointer access in build graph loader (#1396760)

* Mon Nov 07 2016 Sandro Mani <manisandro@gmail.com> - 4.2.0-0.2.beta1
- Rebuild (clang)

* Wed Oct 26 2016 Sandro Mani <manisandro@gmail.com> - 4.2.0-0.1.beta1
- Update to 4.2.0-beta1

* Thu Sep 08 2016 Rex Dieter <rdieter@fedoraproject.org> - 4.1.0-2
- make clang support optional (now buildable on more platforms, including epel7)

* Thu Aug 25 2016 Helio Chissini de Castro <helio@kde.org> - 4.1.0-1
- 4.1.0 stable final released

* Fri Aug 12 2016 Helio Chissini de Castro <helio@kde.org> - 4.1.0-0.4.rc1
- Update appdata as requested

* Mon Aug 08 2016 Sandro Mani <manisandro@gmail.com> - 4.1.0-0.3.rc1
- Update to 4.1.0-rc1

* Sat Jul 16 2016 Sandro Mani <manisandro@gmail.com> - 4.1.0-0.2.beta1
- Rebuild (qt5-qtbase)

* Wed Jul 06 2016 Helio Chissini de Castro <helio@kde.org> - 4.1.0-0.1.beta1
- Beta1 release of 4.1.0
- Removed both rpath and build patches not needed anymore

* Thu Jun 30 2016 Rex Dieter <rdieter@fedoraproject.org> - 4.0.2-2
- rebuild (qt5-qtbase)

* Fri Jun 17 2016 Sandro Mani <manisandro@gmail.com> - 4.0.2-1
- Update to 4.0.2

* Fri Jun 10 2016 Rex Dieter <rdieter@fedoraproject.org> - 4.0.1-3
- Re-add BR: qt5-qtbase-private-devel (got lost?)

* Fri Jun 10 2016 Jan Grulich <jgrulich@redhat.com> - 4.0.1-2
- Rebuild (qt5-qtbase)

* Wed Jun 08 2016 Sandro Mani <manisandro@gmail.com> - 4.0.1-1
- Update to 4.0.1

* Wed May 11 2016 Sandro Mani <manisandro@gmail.com> - 4.0.0-1
- Update to 4.0.0

* Wed Apr 20 2016 Helio Chissini de Castro <helio@kde.org> - 4.0.0-0.3.rc1
- Update to 4.0.0 rc1

* Sun Apr 17 2016 Rex Dieter <rdieter@fedoraproject.org> - 4.0.0-0.2.beta2
- BR: qt5-qtbase-private-devel

* Thu Mar 24 2016 Sandro Mani <manisandro@gmail.com> - 4.0.0-0.1.beta1
- Update to 4.0.0 beta1

* Wed Mar 16 2016 Sandro Mani <manisandro@gmail.com> - 3.6.1-1
- Update to 3.6.1

* Tue Feb 23 2016 Sandro Mani <manisandro@gmail.com> - 3.6.0-9
- Rebuild for Qt5 ABI breakage

* Fri Feb 19 2016 Sandro Mani <manisandro@gmail.com> - 3.6.0-8
- Rebuild (clang)
- Fix build against Qt 5.6rc

* Mon Feb 08 2016 Sandro Mani <manisandro@gmail.com> - 3.6.0-7
- Add qt-creator_llvmincdir.patch to fix FTBFS

* Mon Feb 08 2016 Rex Dieter <rdieter@fedoraproject.org> 3.6.0-6
- rebuild (botan)

* Fri Feb 05 2016 Rex Dieter <rdieter@fedoraproject.org> 3.6.0-5
- add tight dep on qt5-qtbase version used to build qt-creator

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 28 2016 Adam Jackson <ajax@redhat.com> 3.6.0-3
- Rebuild for llvm 3.7.1 library split

* Thu Dec 24 2015 Sandro Mani <manisandro@gmail.com> - 3.6.0-2
- Ensure ClangCodeModel is built

* Tue Dec 15 2015 Sandro Mani <manisandro@gmail.com> - 3.6.0-1
- 3.6.0 release
- Clarify license

* Fri Nov 27 2015 Helio Chissini de Castro <helio@kde.org> - 3.6.0-0.3.rc1
- QDoc was splitted to prepare 5.6.0 changes

* Wed Nov 25 2015 Sandro Mani <manisandro@gmail.com> - 3.6.0-0.2.rc1
- 3.6.0 rc1 release

* Tue Oct 27 2015 Sandro Mani <manisandro@gmail.com> - 3.6.0-0.1.beta1
- 3.6.0 beta1 release

* Thu Oct 15 2015 Sandro Mani <manisandro@gmail.com> - 3.5.1-1
- 3.5.1 release

* Mon Aug 24 2015 Sandro Mani <manisandro@gmail.com> - 3.5.0-1
- 3.5.0 release

* Thu Aug 06 2015 Sandro Mani <manisandro@gmail.com> - 3.5.0-0.4.rc1
- 3.5.0 rc1 release

* Wed Jul 08 2015 Helio Chissini de Castro <helio@kde.org> - 3.5.0-0.3.beta1
- Update to released beta1

* Tue Jun 30 2015 Helio Chissini de Castro <helio@kde.org> - 3.5.0-0.2.1538dca
- Try to make Fedora Qt creator package more compatible with the rest of the world removing the docs patch
- Make appstream contact pointing to fedora qt-creator admins

* Fri Jun 26 2015 Helio Chissini de Castro <helio@kde.org> - 3.5.0-0.1.1538dca
- Build git package

* Sun Jun 21 2015 Sandro Mani <manisandro@gmail.com> - 3.4.1-3
- Add -translations subpackage

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun 02 2015 Sandro Mani <manisandro@gmail.com> - 3.4.1-1
- 3.4.1 release

* Fri May 01 2015 Sandro Mani <manisandro@gmail.com> - 3.4.0-3
- Fix appdata file (#1217757)

* Tue Apr 28 2015 Sandro Mani <manisandro@gmail.com> - 3.4.0-2
- Add patch to correctly call ninja-build (#1216189)

* Thu Apr 23 2015 Sandro Mani <manisandro@gmail.com> - 3.4.0-1
- 3.4.0 release

* Wed Apr 01 2015 Sandro Mani <manisandro@gmail.com> - 3.4.0-0.3.rc1
- 3.4.0 rc1 release

* Thu Mar 19 2015 Sandro Mani <manisandro@gmail.com> - 3.4.0-0.2.beta1
- Re-enable ARM build

* Thu Mar 05 2015 Sandro Mani <manisandro@gmail.com> - 3.4.0-0.1.beta1
- 3.4.0 beta1 release

* Thu Mar 05 2015 Sandro Mani <manisandro@gmail.com> - 3.3.2-1
- 3.3.2 release

* Tue Feb 24 2015 Sandro Mani <manisandro@gmail.com> - 3.3.1-1
- 3.3.1 release
- Use %%license
- Use appstream-util validate-relax
- Split application data to noarch data subpackage
- Sanitize rpaths

* Wed Dec 10 2014 Sandro Mani <manisandro@gmail.com> - 3.3.0-1
- 3.3.0 release

* Thu Nov 27 2014 Sandro Mani <manisandro@gmail.com> - 3.3.0-0.2.rc1
- 3.3.0 rc1 release
- appdata-validate -> appstream-util validate

* Wed Nov 05 2014 Sandro Mani <manisandro@gmail.com> - 3.3.0-0.1.beta1
- 3.3.0 beta1 release

* Mon Oct 13 2014 Sandro Mani <manisandro@gmail.com> - 3.2.2-1
- 3.2.2 release

* Tue Sep 16 2014 Sandro Mani <manisandro@gmail.com> - 3.2.1-1
- 3.2.1 release

* Wed Aug 20 2014 Sandro Mani <manisandro@gmail.com> - 3.2.0-1
- 3.2.0 release

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 06 2014 Sandro Mani <manisandro@gmail.com> - 3.2.0-0.3.rc1
- 3.2.0 rc1 release

* Tue Jul 29 2014 Sandro Mani <manisandro@gmail.com> - 3.2.0-0.2.beta1
- doc subpackage

* Tue Jul 15 2014 Sandro Mani <manisandro@gmail.com> - 3.2.0-0.1.beta1
- 3.2.0 beta1 release

* Thu Jun 26 2014 Sandro Mani <manisandro@gmail.com> - 3.1.2-1
- 3.1.2 release

* Sun Jun 22 2014 Sandro Mani <manisandro@gmail.com> - 3.1.1-3
- Backport upstream patch to fix dumper with gdb 7.7, see rhbz#1110980

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 20 2014 Sandro Mani <manisandro@gmail.com> - 3.1.1-1
- 3.1.1 release

* Fri Apr 04 2014 Sandro Mani <manisandro@gmail.com> - 3.1.0-0.2.rc1
- 3.1.0 rc1 release

* Tue Mar 25 2014 Sandro Mani <manisandro@gmail.com> - 3.1.0-0.1.beta
- 3.1.0 beta release

* Wed Mar 12 2014 Sandro Mani <manisandro@gmail.com> - 3.0.1-3
- Add appdata file
- ExcludeArch arm due to #1074700

* Wed Mar 05 2014 Sandro Mani <manisandro@gmail.com> - 3.0.1-2
- Build against Qt5

* Thu Feb 06 2014 Sandro Mani <manisandro@gmail.com> - 3.0.1-1
- 3.0.1 stable release
- Fix homepage URL
- Improve description

* Thu Dec 12 2013 Sandro Mani <manisandro@gmail.com> - 3.0.0-1
- 3.0.0 stable release

* Sun Dec 01 2013 Sandro Mani <manisandro@gmail.com> - 3.0.0-0.2.rc1
- 3.0.0 rc1 release

* Wed Oct 23 2013 Jaroslav Reznik <jreznik@redhat.com> - 3.0.0-0.1.beta
- 3.0.0 beta release

* Wed Oct 16 2013 Sandro Mani <manisandro@gmail.com> - 2.8.1-1
- Update to 2.8.1
- Update URL and Source0
- Remove unused (commented) stuff
- Consistently use %%{buildroot}

* Wed Oct 16 2013 Sandro Mani <manisandro@gmail.com> - 2.8.0-6
- Fix icon in desktop file

* Fri Sep 20 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 2.8.0-5
- Filter Provides/Requires for private plugin libs (#1003197).
  Let %%install section print an up-to-date filtering list.

* Sat Aug 03 2013 Petr Pisar <ppisar@redhat.com> - 2.8.0-4
- Perl 5.18 rebuild

* Fri Jul 26 2013 Dan Horák <dan[at]danny.cz> - 2.8.0-3
- build with system botan library (#912367)
- spec cleanup

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 2.8.0-2
- Perl 5.18 rebuild

* Thu Jul 11 2013 Jaroslav Reznik <jreznik@redhat.com> - 2.8.0-1
- 2.8.0 release

* Mon Jul 01 2013 Jaroslav Reznik <jreznik@redhat.com> - 2.8.0-0.2.rc
- 2.8.0 rc release

* Fri May 31 2013 Jaroslav Reznik <jreznik@redhat.com> - 2.8.0-0.1.beta
- 2.8.0 beta release

* Fri May 31 2013 Jaroslav Reznik <jreznik@redhat.com> - 2.7.1-1
- 2.7.1 release

* Thu Mar 21 2013 Jaroslav Reznik <jreznik@redhat.com> - 2.7.0-1
- 2.7.0 release

* Thu Mar 07 2013 Jaroslav Reznik <jreznik@redhat.com> - 2.7.0-0.2.rc
- 2.7.0 release candidate

* Sun Feb 10 2013 Jaroslav Reznik <jreznik@redhat.com> - 2.7.0-0.1.beta
- 2.7.0 beta release

* Wed Feb 06 2013 Jaroslav Reznik <jreznik@redhat.com> - 2.6.2-1
- 2.6.2 release

* Fri Dec 21 2012 Jaroslav Reznik <jreznik@redhat.com> - 2.6.1-1
- 2.6.1 release

* Tue Sep 11 2012 Jaroslav Reznik <jreznik@redhat.com> - 2.6.0-0.1.beta
- 2.6.0 beta release

* Wed Aug 15 2012 Jaroslav Reznik <jreznik@redhat.com> - 2.5.2-1
- 2.5.2 release

* Wed Jul 25 2012 Jaroslav Reznik <jreznik@redhat.com> - 2.5.1-1
- 2.5.1 release

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May 09 2012 Jaroslav Reznik <jreznik@redhat.com> - 2.5.0-1
- 2.5.0 release

* Tue Apr 24 2012 Jaroslav Reznik <jreznik@redhat.com> - 2.5.0-0.2.rc
- 2.5.0 rc release

* Fri Mar 16 2012 Jaroslav Reznik <jreznik@redhat.com> - 2.5.0-0.1.beta
- 2.5.0 beta release

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.1-2
- Rebuilt for c++ ABI breakage

* Wed Feb 01 2012 Jaroslav Reznik <jreznik@redhat.com> - 2.4.1-1
- 2.4.1 release
- fix upstream url
- package qmlprofiler

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-0.1.rc
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Nov 28 2011 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.4.0-0.0.rc
- 2.4.0-rc

* Wed Sep 28 2011 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.3.1-1
- 2.3.1 release

* Thu Sep 01 2011 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.3.0-1
- 2.3.0 release

* Wed Jul 13 2011 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.3.0-0.0.beta
- 2.3.0 beta

* Wed Jun 29 2011 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.2.1-2
- include qmlpuppet

* Tue Jun 21 2011 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.2.1-1
- 2.2.1

* Fri May 06 2011 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.2.0-1
- 2.2.0 final

* Wed Apr 20 2011 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.2.0-0.2.rc1
- 2.2.0 RC

* Tue Apr 05 2011 Rex Dieter <rdieter@fedoraproject.org> - 2.2.0-0.1.beta
- BR: qt4-devel-private, for QmlDesigner

* Sat Mar 26 2011 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.2.0-0.0.beta
- 2.2.0 beta

* Sat Mar 26 2011 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.1.0-5
- 2.1.0 final release

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.0-4.rc1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Nov 26 2010 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.1.0-4.rc1
- new version 2.1.0 rc1

* Tue Nov 02 2010 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.1.0-2.beta2
- new version 2.1.0 beta2

* Wed Oct 13 2010 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.1.0-1.beta1
- new version 2.1.0 beta1

* Sat Sep 11 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.0.0-2
- rebuild (#632873)

* Fri Jun 25 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.0.0-1
- 2.0.0 final

* Thu May 06 2010 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.0.0-0.3.beta1
- upgrade to qt-creator 2.0 beta1

* Thu Apr 15 2010 Itamar Reis Peixoto - 2.0.0-0.2.alpha1
- Requres qt-devel and gcc-c++ (we need it to compile programs using qt-creator)

* Tue Mar 16 2010 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 2.0.0-0.1.alpha1
- new version qt-creator 2.0 alpha1

* Tue Feb 16 2010 Rex Dieter <rdieter@fedoraproject.org> - 1.3.1-3
- add minimal qt4 runtime dep

* Thu Feb 11 2010 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.3.1-2
- include missing requires xdg-utils

* Mon Jan 25 2010 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.3.1-1
- new version 1.3.1

* Tue Dec  1 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 1.3.0-2
- Force dependency on Qt >= 4.6.0

* Tue Dec  1 2009 Lorenzo Villani <lvillani@binaryhelix.net> - 1.3.0-1
- 1.3.0 final

* Sun Nov 22 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.3.0-0.4.rc
- include demos/examples.

* Wed Nov 18 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.3.0-0.3.rc
- fix install of /usr/bin/qtcreator wrapper

* Tue Nov 17 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.3.0-0.2.rc
- new version Qt Creator 1.3 Release Candidate(RC)
- include /usr/bin/qtcreator wrapper to /usr/bin/qtcreator.bin

* Wed Oct 14 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.3.0-0.1.beta
- new version 1.3.0-beta

* Sat Sep 12 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.2.90-1
- new version 1.2.90 (Qt Creator Technology Snapshot 1.2.90)

* Wed Aug 12 2009 Ville Skyttä <ville.skytta@iki.fi> - 1.2.1-3
- Use upstream gzipped tarball instead of zip.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.2.1-1
- new version 1.2.1

* Mon Jul 13 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.2.0-2
- fix BZ #498563 patch from Michel Salim <salimma@fedoraproject.org>
- Update GTK icon cache

* Sun Jun 28 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.2.0-1
- new version 1.2.0

* Sat Apr 25 2009 Muayyad Saleh Alsadi <alsadi@ojuba.org> - 1.1.0-2
- fix icons

* Thu Apr 23 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.1.0-1
- qt-creator 1.1.0
- include missing BuildRequires desktop-file-utils

* Fri Mar 20 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.0.0-4
- fix lib's loading in 64 bit machines

* Wed Mar 18 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.0.0-3
- Changed License to LGPLv2 with exceptions and BR to qt4-devel >= 4.5.0

* Tue Mar 17 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.0.0-2
- Improved Version to make it more compatible with fedora guidelines

* Sun Mar 15 2009 Itamar Reis Peixoto <itamar@ispbrasil.com.br> - 1.0.0-1
- initial RPM release
