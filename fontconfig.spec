%define major 1
%define lib_name %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

%define bootstrap 0
%{?_without_bootstrap: %global bootstrap 0}
%{?_with_bootstrap: %global bootstrap 1}
%define rebuild_doc	1
%if %{bootstrap}
%define rebuild_doc 0
%endif

Summary: Font configuration library
Name: fontconfig
Version: 2.8.0
Release: 8
License: MIT
Group: System/X11
URL: http://fontconfig.org/
Source0: http://fontconfig.org/release/fontconfig-%{version}.tar.gz
# (fc) 2.3.2-3mdk prefer urw fonts
Source1: 30-mdv-urwfonts.conf
# (fc) 2.3.2-3mdk dualwidth for CJK
Source2: 20-mdv-CJK-dualwidth.conf
# (fc) 2.3.2-3mdk disable antialiasing for some fonts
Source3: 20-mdv-disable-antialias.conf
# (fc) 2.3.2-3mdk disable hinting for some fonts/languages
Source4: 25-mdv-CJK-disable-hinting.conf
# (fc) 2.3.2-3mdk  Avoid KDE/QT uses some bitmapped fonts (guisseppe)
Source5: 30-mdv-avoid-bitmap.conf
# (fc) 2.4.2-1mdv disable embedded bitmap for big size (Mdv bug #25924)
Source8: 26-mdv-no-embeddedbitmap.conf
# (fwang): 2.4.2-7mdv move wqy-bitmap font rule into fontconfig package
Source9: 85-wqy-bitmapsong.conf
# (fc) 2.4.92-1mdv enable embeddedbitmap on some CJK fonts (Fedora)
Source10: 25-no-bitmap-fedora.conf
# (fc) 2.1-4mdk change order of default fonts
Patch1: fontconfig-mdvconfig.patch

BuildRequires: ed
BuildRequires: libxml2-utils
BuildRequires: lynx
BuildRequires: pkgconfig(freetype2) >= 2.3.5
BuildRequires: pkgconfig(libxml-2.0)
%if %rebuild_doc
BuildRequires: docbook-utils
BuildRequires: docbook-utils-pdf
BuildRequires: docbook-dtd31-sgml
BuildRequires: docbook-dtd41-sgml
%endif

Provides: lib%{name} = %{version}-%{release}
Provides: %{name}-libs = %{version}-%{release}
# fwang: add conflicts to ease upgrade
Conflicts:	x11-font-wqy-bitmapfont < 1.0-0.20070901.1

%description
Fontconfig is designed to locate fonts within the
system and select them according to requirements specified by 
applications.

%package -n %{lib_name}
Summary: Font configuration and customization library
Group: System/Libraries

%description -n %{lib_name}
Fontconfig is designed to locate fonts within the
system and select them according to requirements specified by 
applications.

%package -n %{develname}
Summary: Font configuration and customization library
Group: Development/C
Provides: %{name}-devel = %{version}-%{release}
Requires: %{lib_name} = %{version}-%{release}
Obsoletes: %mklibname -d %{name} 1

%description -n %{develname}
The fontconfig-devel package includes the header files,
and developer docs for the fontconfig package.

Install fontconfig-devel if you want to develop programs which 
will use fontconfig.

%prep
%setup -q
%apply_patches

%build
%if !%rebuild_doc
export HASDOCBOOK=no
%endif

%configure2_5x \
	--disable-static \
	--localstatedir=/var \
	--with-add-fonts="/usr/lib/X11/fonts,/usr/X11R6/lib/X11/fonts,/opt/ttfonts" \
	--enable-libxml2

%make

%install
rm -rf %{buildroot}
%makeinstall_std
find %{buildroot} -name "*.la" -delete

mkdir -p %{buildroot}%{_sysconfdir}/fonts/conf.d
cp %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} %{SOURCE8} %{SOURCE9} %{SOURCE10} %{buildroot}%{_sysconfdir}/fonts/conf.d 

# needed in case main config files isn't up to date
cat << EOF > %{buildroot}%{_sysconfdir}/fonts/conf.d/00-cache.conf
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
<!-- Font cache directory list -->

        <cachedir>/var/cache/fontconfig</cachedir>
        <cachedir>~/.fontconfig</cachedir>

</fontconfig>
EOF

ln -s ../conf.avail/25-unhint-nonlatin.conf %{buildroot}%{_sysconfdir}/fonts/conf.d

# ensure we ship only valid config files
# copy need by dtdvalid
cp -f %{buildroot}%{_sysconfdir}/fonts/fonts.dtd %{buildroot}%{_sysconfdir}/fonts/conf.d/
xmllint --noout --dtdvalid %{buildroot}%{_sysconfdir}/fonts/fonts.dtd %{buildroot}%{_sysconfdir}/fonts/conf.d/??-*.conf
rm -f %{buildroot}%{_sysconfdir}/fonts/conf.d/fonts.dtd

# remove unpackaged files
rm -rf %{buildroot}%{_datadir}/doc/fontconfig 

%check
make check

%post
%{_bindir}/fc-cache --force --system-only >/dev/null

%triggerprein -- fontconfig < 2.4.0
rm -f %{_var}/cache/fontconfig/*.cache-2

%triggerin -- /usr/share/fonts/*, /usr/lib/X11/fonts/*, /usr/X11R6/lib/X11/fonts/*, /opt/ttfonts/*
%{_bindir}/fc-cache -s

%triggerpostun -- /usr/share/fonts/*, /usr/lib/X11/fonts/*, /usr/X11R6/lib/X11/fonts/*, /opt/ttfonts/*
%{_bindir}/fc-cache -s

%files
%doc README AUTHORS COPYING doc/fontconfig-user.html doc/fontconfig-user.txt
%dir %{_var}/cache/fontconfig
%{_bindir}/*
%dir %{_sysconfdir}/fonts
%dir %{_sysconfdir}/fonts/conf.d
%dir %{_sysconfdir}/fonts/conf.avail
%config %{_sysconfdir}/fonts/fonts.dtd
# those files must NOT have noreplace option
%config %{_sysconfdir}/fonts/fonts.conf
%config %{_sysconfdir}/fonts/conf.d/*.conf
%config %{_sysconfdir}/fonts/conf.d/README
%config %{_sysconfdir}/fonts/conf.avail/*.conf
%{_mandir}/man1/*
%{_mandir}/man5/*

%files -n %{lib_name}
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%doc doc/fontconfig-devel doc/fontconfig-devel.txt 
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
%{_mandir}/man3/*

