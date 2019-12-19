%define major 1
%define libname %mklibname %{name} %{major}
%define devname %mklibname %{name} -d
%define rebuild_doc 0

%global optflags %{optflags} -O3

Summary:	Font configuration library
Name:		fontconfig
Version:	2.13.1
Release:	5
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

Patch0:		https://src.fedoraproject.org/cgit/rpms/fontconfig.git/plain/fontconfig-sleep-less.patch
Patch1:		https://src.fedoraproject.org/cgit/rpms/fontconfig.git/plain/fontconfig-stop-cleanup-uuid.patch
Patch2:		fontconfig-omdv-config.patch
Patch3:		fontconfig-2.11.95-wine-assert-nonfatal.patch


Patch12:         fontconfig-2.13.0-fonts-nanum.patch
Patch13:         fontconfig-2.13.0-lcdfilterlegacy.patch
Patch15:         fontconfig-2.13.0-old-diff-gz-06-ubuntu-lcddefault.patch
Patch17:         fontconfig-2.13.0-ubuntu-add-hinting-and-antialiasing-confs.patch
Patch18:         fontconfig-2.13.0-ubuntu-add-monospace-lcd-filter-conf.patch

BuildRequires:	ed
BuildRequires:	pkgconfig(expat)
BuildRequires:	lynx
BuildRequires:	gperf
BuildRequires:	pkgconfig(bzip2)
BuildRequires:	pkgconfig(freetype2) >= 2.3.5
BuildRequires:	pkgconfig(uuid)
BuildRequires:	gettext-devel
BuildRequires:	pkgconfig(json-c)
%if %rebuild_doc
# Actually, we don't really need whole set of texlive packages
# but it's hard to find what exactly we need. So we use texlive.
BuildRequires:	texlive
BuildRequires:	docbook-utils
BuildRequires:	docbook-utils-pdf
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	docbook-dtd41-sgml
%endif
Requires(post): /bin/sh

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

%prep
%autosetup -p1

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
	--with-add-fonts="/usr/share/fonts,/usr/share/X11/fonts/Type1,/usr/share/X11/fonts/TTF,/usr/local/share/fonts,/usr/lib/X11/fonts,/opt/ttfonts"

%make_build LIBS="-lbz2"

%install
%make_install

mkdir -p %{buildroot}%{_sysconfdir}/fonts/conf.d
cp %{SOURCE1} %{SOURCE3} %{SOURCE4} %{SOURCE5} %{SOURCE8} %{SOURCE10} %{buildroot}%{_sysconfdir}/fonts/conf.d

ln -s ../../..%{_datadir}/%{name}/conf.avail/25-unhint-nonlatin.conf %{buildroot}%{_sysconfdir}/fonts/conf.d
ln -s ../../..%{_datadir}/%{name}/conf.avail/10-sub-pixel-rgb.conf %{buildroot}%{_sysconfdir}/fonts/conf.d

# remove unpackaged files
rm -rf %{buildroot}%{_datadir}/doc/fontconfig 

%find_lang %{name}
%find_lang %{name}-conf

%post
%{_bindir}/fc-cache --force --system-only >/dev/null

%triggerprein -- fontconfig < 2.4.0
rm -f %{_var}/cache/fontconfig/*.cache-2

%transfiletriggerin -- /usr/share/fonts /usr/share/X11/fonts/Type1 /usr/local/share/fonts /usr/lib/X11/fonts /opt/ttfonts
%{_bindir}/fc-cache -s

%transfiletriggerpostun -- /usr/share/fonts /usr/share/X11/fonts/Type1 /usr/local/share/fonts /usr/lib/X11/fonts /opt/ttfonts
%{_bindir}/fc-cache -s

%files -f %{name}.lang -f %{name}-conf.lang
%doc README AUTHORS COPYING doc/fontconfig-user.html doc/fontconfig-user.txt
%dir %{_var}/cache/fontconfig
%{_bindir}/*
%dir %{_sysconfdir}/fonts
%dir %{_sysconfdir}/fonts/conf.d
%{_datadir}/%{name}/conf.avail
%{_datadir}/xml/fontconfig/fonts.dtd
%{_datadir}/gettext/its/*
# those files must NOT have noreplace option
%config %{_sysconfdir}/fonts/fonts.conf
%config %{_sysconfdir}/fonts/conf.d/*.conf
%config %{_sysconfdir}/fonts/conf.d/README
%{_mandir}/man1/*
%{_mandir}/man5/*

%files -n %{libname}
%{_libdir}/libfontconfig.so.%{major}*

%files -n %{devname}
%doc doc/fontconfig-devel doc/fontconfig-devel.txt 
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
%{_mandir}/man3/*
