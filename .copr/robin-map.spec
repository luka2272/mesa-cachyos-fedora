%global debug_package %{nil}
Name: robin-map
Version: 1.4.0
Release: 0
Summary: C++ implementation of a fast hash map and hash set using robin hood hashing
URL: https://github.com/Tessil/robin-map/
License: MIT
BuildRequires: cmake make gcc-c++
Source: https://github.com/Tessil/robin-map/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

%package devel
Summary: %{summary}.

%description devel
%{summary}.

%description
%{summary}.


%prep
%autosetup

%build
%cmake -DPHMAP_BUILD_TESTS=OFF -DPHMAP_BUILD_EXAMPLES=OFF
%cmake_build

%install
%cmake_install

%files devel
%dir %_includedir/tsl
%_includedir/tsl/*.h
%dir %_datadir/cmake/tsl-%name
%_datadir/cmake/tsl-%name/*.cmake
