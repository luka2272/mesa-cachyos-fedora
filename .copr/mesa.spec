Name:           mesa
Version:        25.1.1
Release:        1%{?dist}
Epoch:          1
Summary:        Open-source OpenGL, Vulkan, and OpenCL drivers

License:        MIT and BSD and SGI-B-2.0
URL:            https://www.mesa3d.org/
Source0:        https://archive.mesa3d.org//mesa-%{version}.tar.xz
Patch0:         https://gitlab.freedesktop.org/mesa/mesa/-/commit/e6481d3f42e0cd735fda38fb3029e6f8abf5a0e6.patch

BuildRequires:  gcc, clang, meson, ninja-build
BuildRequires:  libdrm-devel, elfutils-libelf-devel, libglvnd-devel, libva-devel, libvdpau-devel
BuildRequires:  libX11-devel, libxcb-devel, libXext-devel, libxshmfence-devel, libXxf86vm-devel
BuildRequires:  libXrandr-devel, libxml2-devel, expat-devel, zlib-devel, libzstd-devel
BuildRequires:  spirv-tools-devel, spirv-llvm-translator-devel, systemd-devel, wayland-devel
BuildRequires:  wayland-protocols-devel, llvm-devel, lm_sensors-devel
BuildRequires:  python3-mako, python3-packaging, python3-ply, python3-yaml
BuildRequires:  rust, rust-packaging, cbindgen, glslang-devel, cmake, libclc-devel
BuildRequires:  valgrind-devel, python3-sphinx, python3-sphinx_rtd_theme
BuildRequires:  xorg-x11-proto-devel, xcb-util-devel, xcb-util-image-devel, xcb-util-renderutil-devel

%description
Mesa is an open-source implementation of the OpenGL specification - a system for rendering interactive 3D graphics. Mesa also includes Vulkan and OpenCL implementations.

%prep
%autosetup -p1 -n mesa-%{version}
echo "%{version}-%{release}" > VERSION

%build
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

%install
%meson_install

%files
%license docs/license.rst
%doc docs/*

%changelog
* Thu May 29 2025 You <you@example.com> - 1:25.1.1-1
- Import of Mesa 25.1.1 with Vulkan, VAAPI, Rusticl and documentation support based on CachyOS patches
