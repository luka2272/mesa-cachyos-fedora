%global maj_ver 20
%global min_ver 1
%global patch_ver 0
%global baserelease 0.1

%ifarch ppc64le
# Limit build jobs on ppc64 systems to avoid running out of memory.
%global _smp_mflags -j8
%endif

%global install_prefix %{_libdir}/llvm%{maj_ver}
%global pkg_libdir %{install_prefix}/lib/

# Disable debuginfo on ppc64le to reduce disk space usage.
%ifarch ppc64le
%global _find_debuginfo_dwz_opts %{nil}
%global debug_package %{nil}
%endif

%if 0%{?rhel} == 8
%global python3_pkgversion 3.12
%global __python3 /usr/bin/python3.12
%endif

%if 0%{?rhel} < 10
%global gcc_toolset gcc-toolset-14
%endif

Name:		llvm-compat%{maj_ver}
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	%{baserelease}%{?dist}
Summary:	The Low Level Virtual Machine

License:	NCSA
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/llvm-%{version}.src.tar.xz
Source1:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/clang-%{version}.src.tar.xz
Source2:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/cmake-%{version}.src.tar.xz


# RHEL-specific patch to avoid unwanted recommonmark dep
#Patch101:	0101-Deactivate-markdown-doc.patch


BuildRequires:  gcc
BuildRequires:  gcc-c++
%if 0%{?rhel} < 10
BuildRequires:	%{gcc_toolset}-gcc
BuildRequires:	%{gcc_toolset}-gcc-c++
BuildRequires:	%{gcc_toolset}-gcc-plugin-annobin
%endif
BuildRequires:	cmake
BuildRequires:	zlib-devel
BuildRequires:  libffi-devel
BuildRequires:	ncurses-devel
BuildRequires:	multilib-rpm-config
BuildRequires:	ninja-build
BuildRequires:	python%{python3_pkgversion}-devel

%ifarch %{valgrind_arches}
# Enable extra functionality when run the LLVM JIT under valgrind.
BuildRequires:  valgrind-devel
%endif

Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

%description
LLVM is a compiler infrastructure designed for compile-time, link-time,
runtime, and idle-time optimization of programs from arbitrary programming
languages. The compiler infrastructure includes mirror sets of programming
tools as well as libraries with equivalent functionality.

%package libs
Summary:	LLVM shared libraries


%description libs
Shared libraries for the LLVM compiler infrastructure.

%prep
%setup -T -q -b 2 -n cmake-%{version}.src
cd ..
mv cmake-%{version}.src cmake

%setup -T -q -b 1 -n clang-%{version}.src
%autopatch -m100 -p2
cd ..
mv clang-%{version}.src clang

%setup -q -n llvm-%{version}.src
%autopatch -M100 -p2


%build
%if 0%{?rhel} < 10
source /opt/rh/%{gcc_toolset}/enable
%endif

%ifarch s390 %ix86
# Decrease debuginfo verbosity to reduce memory consumption during final library linking
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

cd ..

mkdir llvm-build
pushd llvm-build

# force off shared libs as cmake macros turns it on.
%cmake ../llvm-%{version}.src -G Ninja \
	-B . \
	-DBUILD_SHARED_LIBS:BOOL=OFF \
	-DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
	-DPython3_EXECUTABLE=%{__python3} \
%ifarch ppc64le
	-DCMAKE_BUILD_TYPE=Release \
%else
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
%endif
%ifarch s390 %ix86
	-DCMAKE_C_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
	-DCMAKE_CXX_FLAGS_RELWITHDEBINFO="%{optflags} -DNDEBUG" \
%endif
	\
	-DLLVM_TARGETS_TO_BUILD="X86;AMDGPU;PowerPC;NVPTX;SystemZ;AArch64;ARM;Mips;BPF;WebAssembly" \
	-DCMAKE_INSTALL_PREFIX=%{install_prefix} \
	-DLLVM_ENABLE_EH=ON \
	-DLLVM_ENABLE_FFI:BOOL=ON \
	-DLLVM_ENABLE_RTTI:BOOL=ON \
	-DLLVM_BUILD_LLVM_DYLIB:BOOL=ON \
	-DLLVM_DYLIB_EXPORT_ALL:BOOL=ON \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_INCLUDE_TESTS=OFF \
	-DLLVM_INCLUDE_BENCHMARKS=OFF \
	-DLLVM_ENABLE_PROJECTS=clang  \
	-DLLVM_BUILD_DOCS=OFF \
	-DLLVM_INCLUDE_DOCS=OFF

%ninja_build LLVM
%ninja_build libclang.so
%ninja_build libclang-cpp.so

popd

%install

mkdir -p %{buildroot}%{pkg_libdir}
install -m 0755 ../llvm-build/lib/libLLVM.so.%{maj_ver}* %{buildroot}%{pkg_libdir}
install -m 0755 ../llvm-build/lib/libclang.so.%{maj_ver}* %{buildroot}%{pkg_libdir}
install -m 0755 ../llvm-build/lib/libclang-cpp.so.%{maj_ver}* %{buildroot}%{pkg_libdir}

ln -sf libLLVM.so.%{maj_ver}.%{min_ver}.%{patch_ver} %{buildroot}%{pkg_libdir}/libLLVM-%{maj_ver}.so
ln -sf libclang.so.%{maj_ver}.%{min_ver}.%{patch_ver} %{buildroot}%{pkg_libdir}/libclang.so.%{maj_ver}.%{min_ver}

# Create ld.so.conf.d entry
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
cat >> %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf << EOF
%{pkg_libdir}
EOF

%check

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files

%files libs
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
%{pkg_libdir}/libLLVM-%{maj_ver}.so
%{pkg_libdir}/libLLVM.so.*
%{pkg_libdir}/libclang*.so.*
