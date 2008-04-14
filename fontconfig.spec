%define fontconfig_major 1
%define lib_name %mklibname %{name} %{fontconfig_major}
%define develname %mklibname %name -d

%define freetype_version 2.3.5

Summary: Font configuration library
Name: fontconfig
Version: 2.5.91
Release: %mkrel 1
License: MIT
Group: System/X11
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
# (fc) 2.1-4mdk default configuration (rawhide) + (pablo) 2.2-3mdk adds font aliases for various languages
Patch1: fontconfig-mdvconfig.patch

URL: http://fontconfig.org/
BuildRoot: %{_tmppath}/fontconfig-%{version}-root

Requires(post): %{lib_name}  >= %{version}-%{release}
BuildRequires: freetype2-devel >= %{freetype_version}

BuildRequires: ed
BuildRequires: docbook-utils
BuildRequires: docbook-utils-pdf
BuildRequires: docbook-dtd31-sgml
BuildRequires: docbook-dtd41-sgml
BuildRequires: lynx
BuildRequires: libxml2-devel
BuildRequires: libxml2-utils

# fwang: add conflicts to ease upgrade
Conflicts:	x11-font-wqy-bitmapfont < 1.0-0.20070901.1

%description
Fontconfig is designed to locate fonts within the
system and select them according to requirements specified by 
applications.

%package -n %{lib_name}
Summary: Font configuration and customization library
Group: System/Libraries
Requires: %{name} >= %{version}-%{release}
Provides: lib%{name} = %{version}-%{release}
Provides: %{name}-libs = %{version}-%{release}

%description -n %{lib_name}
Fontconfig is designed to locate fonts within the
system and select them according to requirements specified by 
applications.

%package -n %{develname}
Summary: Font configuration and customization library
Group: Development/C
Provides: lib%{name}-devel = %{version}-%{release}
Provides: %{name}-devel = %{version}-%{release}
Requires: %{name} = %{version}-%{release}
Requires: %{lib_name} = %{version}-%{release}
Requires: freetype2-devel >= %{freetype_version}
Obsoletes: %mklibname -d %name 1

%description -n %{develname}
The fontconfig-devel package includes the header files,
and developer docs for the fontconfig package.

Install fontconfig-devel if you want to develop programs which 
will use fontconfig.

%prep
%setup -q
%patch1 -p1 -b .mdvconfig

%build
%configure2_5x --localstatedir=/var \
   --with-add-fonts="/usr/lib/X11/fonts,/usr/X11R6/lib/X11/fonts,/opt/ttfonts,/usr/share/yudit/fonts" \
   --enable-libxml2

%make

make check

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d
cp %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} %{SOURCE8} %{SOURCE9} %{SOURCE10} $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d 

# needed in case main config files isn't up to date
cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d/00-cache.conf
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
<!-- Font cache directory list -->

        <cachedir>/var/cache/fontconfig</cachedir>
        <cachedir>~/.fontconfig</cachedir>

</fontconfig>
EOF

ln -s ../conf.avail/25-unhint-nonlatin.conf $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d

# ensure we ship only valid config files
# copy need by dtdvalid
cp -f $RPM_BUILD_ROOT%{_sysconfdir}/fonts/fonts.dtd $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d/
xmllint --noout --dtdvalid $RPM_BUILD_ROOT%{_sysconfdir}/fonts/fonts.dtd $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d/??-*.conf
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d/fonts.dtd

# remove unpackaged files
rm -rf $RPM_BUILD_ROOT%{_datadir}/doc/fontconfig 

%clean
rm -rf $RPM_BUILD_ROOT

%post
%{_bindir}/fc-cache --force --system-only >/dev/null

%post -n %{lib_name} -p /sbin/ldconfig

%postun -n %{lib_name} -p /sbin/ldconfig

%triggerprein -- fontconfig < 2.4.0
rm -f %{_var}/cache/fontconfig/*.cache-2

%files
%defattr(-, root, root)
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
%defattr(-, root, root)
%{_libdir}/*.so.*

%files -n %{develname}
%defattr(-, root, root)
%doc doc/fontconfig-devel doc/fontconfig-devel.txt 
%{_libdir}/*.la
%{_libdir}/*.a
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
%{_mandir}/man3/*
