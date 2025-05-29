Name:           mesa
Version:        25.1.1
Release:        1%{?dist}
Epoch:          1
Summary:        Open-source OpenGL, Vulkan, and OpenCL drivers (64-bit and 32-bit)

License:        MIT and BSD and SGI-B-2.0
URL:            https://www.mesa3d.org/
Source0:        https://mesa.freedesktop.org/archive/mesa-%{version}.tar.xz
Patch0:         https://gitlab.freedesktop.org/mesa/mesa/-/commit/e6481d3f42e0cd735fda38fb3029e6f8abf5a0e6.patch

BuildRequires:  gcc, gcc-c++, clang, meson, ninja-build
BuildRequires:  libdrm-devel, libelf-devel, libglvnd-devel, libva-devel, libvdpau-devel
BuildRequires:  libx11-devel, libxcb-devel, libxext-devel, libxshmfence-devel, libxxf86vm-devel
BuildRequires:  libxrandr-devel, libxml2-devel, expat-devel, zlib-devel, zstd-devel
BuildRequires:  spirv-tools-devel, spirv-llvm-translator-devel, systemd-devel, wayland-devel
BuildRequires:  wayland-protocols-devel, llvm-devel, lm_sensors-devel
BuildRequires:  python3-mako, python3-packaging, python3-ply, python3-yaml
BuildRequires:  rust, rust-packaging, cbindgen, glslang-devel, cmake, libclc-devel
BuildRequires:  valgrind-devel, python3-sphinx, python3-sphinx_rtd_theme
BuildRequires:  xorg-x11-proto-devel, xcb-util-devel, xcb-util-image-devel, xcb-util-renderutil-devel
# 32-bit support
BuildRequires:  glibc-devel.i686, libdrm-devel.i686, libelf-devel.i686, libglvnd-devel.i686
BuildRequires:  libx11-devel.i686, libxcb-devel.i686, libxext-devel.i686, libxshmfence-devel.i686
BuildRequires:  libxxf86vm-devel.i686, llvm-libs.i686, lm_sensors-libs.i686
BuildRequires:  spirv-tools-libs.i686, wayland-devel.i686, zlib-devel.i686, zstd-devel.i686
BuildRequires:  clang-libs.i686, expat-devel.i686, systemd-devel.i686, libva-devel.i686
BuildRequires:  libvdpau-devel.i686, libxrandr-devel.i686, libxml2-devel.i686

%description
Mesa is an open-source implementation of the OpenGL specification - a system for rendering interactive 3D graphics. Mesa also includes Vulkan and OpenCL implementations. This package contains both 64-bit and 32-bit driver libraries.

%prep
%autosetup -p1 -n mesa-%{version}
echo "%{version}-%{release}" > VERSION

%build
# 64-bit build
%meson \
  -D android-libbacktrace=disabled \
  -D b_ndebug=true \
  -D gallium-drivers=r300,r600,radeonsi,nouveau,virgl,svga,llvmpipe,softpipe,iris,crocus,i915,zink,d3d12 \
  -D gallium-extra-hud=true \
  -D gallium-rusticl=true \
  -D gallium-xa=disabled \
  -D gles1=disabled \
  -D html-docs=enabled \
  -D libunwind=disabled \
  -D microsoft-clc=disabled \
  -D valgrind=enabled \
  -D video-codecs=all \
  -D vulkan-drivers=amd,gfxstream,intel,intel_hasvk,nouveau,swrast,virtio,microsoft-experimental \
  -D vulkan-layers=device-select,intel-nullhw,overlay,screenshot,vram-report-limit
%meson_build

# 32-bit build
mkdir -p build32
meson setup build32 mesa-%{version} \
  --cross-file=/usr/share/meson/cross/32bit.txt \
  -D android-libbacktrace=disabled \
  -D b_ndebug=true \
  -D gallium-drivers=r300,r600,radeonsi,nouveau,virgl,svga,llvmpipe,softpipe,iris,crocus,i915,zink,d3d12 \
  -D gallium-extra-hud=true \
  -D gallium-rusticl=true \
  -D gallium-xa=disabled \
  -D gles1=disabled \
  -D html-docs=disabled \
  -D libunwind=disabled \
  -D microsoft-clc=disabled \
  -D valgrind=disabled \
  -D video-codecs=all \
  -D vulkan-drivers=amd,gfxstream,intel,intel_hasvk,nouveau,swrast,virtio,microsoft-experimental \
  -D vulkan-layers=device-select,intel-nullhw,overlay,screenshot,vram-report-limit
meson compile -C build32

%install
%meson_install
meson install -C build32 --destdir=%{buildroot}/lib32

%files
%license docs/license.rst
%doc docs/*

%files lib32
%license docs/license.rst
%dir /lib32
/lib32/usr/lib/*.so*
/lib32/usr/share/vulkan/icd.d/*
/lib32/usr/share/vulkan/implicit_layer.d/*

%changelog
* Thu May 29 2025 You <you@example.com> - 1:25.1.1-1
- Initial import of Mesa 25.1.1 (64-bit and 32-bit build based on CachyOS PKGBUILD)
