%define major	1
%define libname %mklibname %{name} %{major}
%define devname %mklibname %{name} -d

%define bootstrap 1
%{?_without_bootstrap: %global bootstrap 0}
%{?_with_bootstrap: %global bootstrap 1}
%define rebuild_doc	0
%if %{bootstrap}
%define rebuild_doc 0
%endif

Summary:	Font configuration library
Name:		fontconfig
Version:	2.12.1
Release:	1
License:	MIT
Group:		System/X11
Url:		http://fontconfig.org/
Source0:	http://www.freedesktop.org/software/fontconfig/release/%{name}-%{version}.tar.bz2
# (fc) 2.3.2-3mdk prefer urw fonts
Source1:	30-mdv-urwfonts.conf
# (fc) 2.3.2-3mdk disable antialiasing for some fonts
Source3:	20-mdv-disable-antialias.conf
# (tpg) use Antiqua Poltawski for polish language
Source4:	65-lang-pl.conf
# (fc) 2.3.2-3mdk  Avoid KDE/QT uses some bitmapped fonts (guisseppe)
Source5:	30-mdv-avoid-bitmap.conf
# (fc) 2.4.2-1mdv disable embedded bitmap for big size (Mdv bug #25924)
Source8:	26-mdv-no-embeddedbitmap.conf
# (fc) 2.4.92-1mdv enable embeddedbitmap on some CJK fonts (Fedora)
Source10:	25-no-bitmap-fedora.conf
# (fc) 2.1-4mdk change order of default fonts
Source11:	fc-cache.filter
Source12:	fc-cache.script
Patch0:		fontconfig-sleep-less.patch
Patch1:		fontconfig-omdv-config.patch
Patch2:		fontconfig-2.11.95-wine-assert-nonfatal.patch
BuildRequires:	ed
BuildRequires:	libxml2-utils
BuildRequires:	lynx
BuildRequires:	bzip2-devel
BuildRequires:	pkgconfig(freetype2) >= 2.3.5
BuildRequires:	pkgconfig(libxml-2.0)
%if %rebuild_doc
# Actually, we don't really need whole set of texlive packages
# but it's hard to find what exactly we need. So we use texlive.
BuildRequires:	texlive
BuildRequires:	docbook-utils
BuildRequires:	docbook-utils-pdf
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	docbook-dtd41-sgml
%endif

%description
Fontconfig is designed to locate fonts within the
system and select them according to requirements specified by 
applications.

%package -n %{libname}
Summary:	Font configuration and customization library
Group:		System/Libraries

%description -n	%{libname}
This package contains the shared library for %{name}.

%package -n %{devname}
Summary:	Font configuration and customization library
Group:		Development/C
Provides:	%{name}-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}

%description -n	%{devname}
The fontconfig-devel package includes the header files,
and developer docs for the fontconfig package.

%track
prog %name = {
	url = http://www.freedesktop.org/software/fontconfig/release/
	version = %version
	regex = %name-(__VER__)\.tar\.bz2
}

%prep
%setup -q
%apply_patches

# disable Werror for aarch64
# you can remove it in future
sed -i 's/-Werror//g' configure.ac
# (tpg) rebuild just to nuke rpath
libtoolize -f
autoreconf -fi

%build
%if !%rebuild_doc
export HASDOCBOOK=no
%endif

%configure \
	--disable-static \
	--localstatedir=/var \
	--disable-libxml2 \
	--with-add-fonts="/usr/lib/X11/fonts,/usr/X11R6/lib/X11/fonts,/opt/ttfonts" \
	--enable-libxml2

%make LIBS="-lbz2"

%install
%makeinstall_std

mkdir -p %{buildroot}%{_sysconfdir}/fonts/conf.d
cp %{SOURCE1} %{SOURCE3} %{SOURCE4} %{SOURCE5} %{SOURCE8} %{SOURCE10} %{buildroot}%{_sysconfdir}/fonts/conf.d

ln -s ../../..%{_datadir}/%{name}/conf.avail/25-unhint-nonlatin.conf %{buildroot}%{_sysconfdir}/fonts/conf.d
ln -s ../../..%{_datadir}/%{name}/conf.avail/10-sub-pixel-rgb.conf %{buildroot}%{_sysconfdir}/fonts/conf.d

# remove unpackaged files
rm -rf %{buildroot}%{_datadir}/doc/fontconfig 

# install filetriggers
install -d -m 0755 %{buildroot}%{_var}/lib/rpm/filetriggers
install -m 0644 %{SOURCE11} %{buildroot}%{_var}/lib/rpm/filetriggers
install -m 0755 %{SOURCE12} %{buildroot}%{_var}/lib/rpm/filetriggers

%post
%{_bindir}/fc-cache --force --system-only >/dev/null

%triggerprein -- fontconfig < 2.4.0
rm -f %{_var}/cache/fontconfig/*.cache-2

%files
%doc README AUTHORS COPYING doc/fontconfig-user.html doc/fontconfig-user.txt
%dir %{_var}/cache/fontconfig
%{_bindir}/*
%dir %{_sysconfdir}/fonts
%dir %{_sysconfdir}/fonts/conf.d
%{_datadir}/%{name}/conf.avail
%{_datadir}/xml/fontconfig/fonts.dtd
# those files must NOT have noreplace option
%config %{_sysconfdir}/fonts/fonts.conf
%config %{_sysconfdir}/fonts/conf.d/*.conf
%config %{_sysconfdir}/fonts/conf.d/README
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_var}/lib/rpm/filetriggers/fc-cache.*

%files -n %{libname}
%{_libdir}/libfontconfig.so.%{major}*

%files -n %{devname}
%doc doc/fontconfig-devel doc/fontconfig-devel.txt 
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
%{_mandir}/man3/*
