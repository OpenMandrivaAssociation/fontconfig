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

Summary:	Font configuration library
Name:		fontconfig
Version:	2.10.2
Release:	2
License:	MIT
Group:		System/X11
URL:		http://fontconfig.org/
Source0:	http://www.freedesktop.org/software/fontconfig/release/%{name}-%{version}.tar.bz2
# (fc) 2.3.2-3mdk prefer urw fonts
Source1:	30-mdv-urwfonts.conf
# (fc) 2.3.2-3mdk disable antialiasing for some fonts
Source3:	20-mdv-disable-antialias.conf
# (fc) 2.3.2-3mdk  Avoid KDE/QT uses some bitmapped fonts (guisseppe)
Source5:	30-mdv-avoid-bitmap.conf
# (fc) 2.4.2-1mdv disable embedded bitmap for big size (Mdv bug #25924)
Source8:	26-mdv-no-embeddedbitmap.conf
# (fc) 2.4.92-1mdv enable embeddedbitmap on some CJK fonts (Fedora)
Source10:	25-no-bitmap-fedora.conf
# (fc) 2.1-4mdk change order of default fonts
Source11: fc-cache.filter
Source12: fc-cache.script
Patch1:		fontconfig-mdvconfig.patch

BuildRequires:	ed
#BuildRequires:	ibxml2-utils
BuildRequires:	lynx
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

Provides:	lib%{name} = %{version}-%{release}
Provides:	%{name}-libs = %{version}-%{release}
# fwang: add conflicts to ease upgrade
Conflicts:	x11-font-wqy-bitmapfont < 1.0-0.20070901.1

%description
Fontconfig is designed to locate fonts within the
system and select them according to requirements specified by 
applications.

%package -n %{lib_name}
Summary:	Font configuration and customization library
Group:		System/Libraries

%description -n %{lib_name}
Fontconfig is designed to locate fonts within the
system and select them according to requirements specified by 
applications.

%package -n %{develname}
Summary:	Font configuration and customization library
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{lib_name} = %{version}-%{release}

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
%makeinstall_std

mkdir -p %{buildroot}%{_sysconfdir}/fonts/conf.d
cp %{SOURCE1} %{SOURCE3} %{SOURCE5} %{SOURCE8} %{SOURCE10} %{buildroot}%{_sysconfdir}/fonts/conf.d 

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

ln -s ../../../%{_datadir}/%{name}/conf.avail/25-unhint-nonlatin.conf %{buildroot}%{_sysconfdir}/fonts/conf.d

# remove unpackaged files
rm -rf %{buildroot}%{_datadir}/doc/fontconfig 

# install filetriggers
install -d -m 0755 %{buildroot}%{_var}/lib/rpm/filetriggers
install -m 0644 %{SOURCE11} %{buildroot}%{_var}/lib/rpm/filetriggers
install -m 0755 %{SOURCE12} %{buildroot}%{_var}/lib/rpm/filetriggers

# we don't want these
find %{buildroot} -name "*.la" -delete

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

%files -n %{lib_name}
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%doc doc/fontconfig-devel doc/fontconfig-devel.txt 
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
%{_mandir}/man3/*

%changelog
* Sun Apr 15 2012 Tomasz Pawel Gajc <tpg@mandriva.org> 2.9.0-1
+ Revision: 791165
- update patch 1
- update to new version 2.9.0

* Thu Nov 24 2011 Matthew Dawkins <mattydaw@mandriva.org> 2.8.0-8
+ Revision: 733233
- rebuild
- spec clean up
- removed dep loop of main <> lib pkgs
- disabled static build
- removed .la files
- moved lib provides to main for lsb
- removed reqs in devel pkg
- removed defattr
- removed old ldconfig scriptlets
- added check section
- removed clean section
- converted BRs to pkgconfig provides
- removed mkrel & BuildRoot
- employeed apply_patches

* Tue May 03 2011 Oden Eriksson <oeriksson@mandriva.com> 2.8.0-7
+ Revision: 664317
- mass rebuild

* Fri Feb 11 2011 Funda Wang <fwang@mandriva.org> 2.8.0-6
+ Revision: 637221
- convert rpm filetrigger to rpm5 standard triggers

* Wed Dec 29 2010 Funda Wang <fwang@mandriva.org> 2.8.0-5mdv2011.0
+ Revision: 625776
- rebuild

* Tue Dec 28 2010 Funda Wang <fwang@mandriva.org> 2.8.0-4mdv2011.0
+ Revision: 625493
- rebuild for new fontconfig

* Thu Dec 02 2010 Oden Eriksson <oeriksson@mandriva.com> 2.8.0-3mdv2011.0
+ Revision: 605174
- rebuild

* Mon Jan 18 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 2.8.0-2mdv2010.1
+ Revision: 493195
- Add filetriggers to run fc-cache

* Thu Nov 19 2009 Frederic Crozat <fcrozat@mandriva.com> 2.8.0-1mdv2010.1
+ Revision: 467386
- Release 2.8.0

* Thu Sep 24 2009 Olivier Blin <blino@mandriva.org> 2.7.3-2mdv2010.0
+ Revision: 448269
- add bootstrap build option (from Arnaud Patard)
- allow to build rpm without doc, getting docbook-utils is a nightmare
  due to circular build deps including fontconfig. break that.
  (from Arnaud Patard)

* Mon Sep 14 2009 Frederic Crozat <fcrozat@mandriva.com> 2.7.3-1mdv2010.0
+ Revision: 440613
- Release 2.7.3

* Mon Aug 31 2009 Funda Wang <fwang@mandriva.org> 2.7.1-2mdv2010.0
+ Revision: 422926
- prefer micro hei for chinese locale

* Tue Jul 28 2009 Frederic Crozat <fcrozat@mandriva.com> 2.7.1-1mdv2010.0
+ Revision: 402510
- Release 2.7.1
- Regenerate patch0

* Thu Jun 25 2009 Frederic Crozat <fcrozat@mandriva.com> 2.7.0-1mdv2010.0
+ Revision: 389057
- Release 2.7.0
- Regenerate patch0 (partially merged)

* Wed Apr 15 2009 Funda Wang <fwang@mandriva.org> 2.6.0-5mdv2009.1
+ Revision: 367542
- fix bug#48071, specify correct font size when using embedded bitmap fonts

* Tue Feb 03 2009 Frederic Crozat <fcrozat@mandriva.com> 2.6.0-4mdv2009.1
+ Revision: 336914
- Drop yudit directory from default config, not useful and causes polling on most systems where it is not installed

* Sat Sep 27 2008 Funda Wang <fwang@mandriva.org> 2.6.0-3mdv2009.0
+ Revision: 288843
- adopt to new chiinese font names

* Sat Jul 12 2008 Funda Wang <fwang@mandriva.org> 2.6.0-2mdv2009.0
+ Revision: 234178
- Prefer WenQuanYi fonts with Chinese

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Tue Jun 03 2008 Frederic Crozat <fcrozat@mandriva.com> 2.6.0-1mdv2009.0
+ Revision: 214728
- Release 2.6.0

* Wed May 28 2008 Frederic Crozat <fcrozat@mandriva.com> 2.5.93-1mdv2009.0
+ Revision: 212682
- Release 2.5.93 (2.6 RC3)
- Regenerate patch1, almost everything got merged upstream \o/

  + Funda Wang <fwang@mandriva.org>
    - The font name of Chinese fonts changed

* Mon Apr 14 2008 Paulo Andrade <pcpa@mandriva.com.br> 2.5.91-1mdv2009.0
+ Revision: 193442
- Update to version 2.5.91.

* Mon Jan 14 2008 Paulo Andrade <pcpa@mandriva.com.br> 2.5.0-2mdv2008.1
+ Revision: 151842
- Update BuildRequires and rebuild.
- Move %%triggerprein in spec file as it was being interpreted as an %%clean
  command and exiting the rpm build process with an error exit status.

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Nov 14 2007 Frederic Crozat <fcrozat@mandriva.com> 2.5.0-1mdv2008.1
+ Revision: 108636
- Release 2.5.0

* Tue Nov 06 2007 Frederic Crozat <fcrozat@mandriva.com> 2.4.92-1mdv2008.1
+ Revision: 106413
- Release 2.4.92
- Update source4 and rename it : partially merged upstream
- Remove source6 (no longer needed), source7 (merged upstream)
- Rename source8 (partially handled by upstream)
- Source10 (Fedora): enable embedded bitmap on some CJK fonts (other part is partially merged)
- Remove patches 2 (merged upsteam), 3 (no longer needed), 4 (merged upstream)
- Update patch1 to move some configuration part in upstream files
- Remove upstream merged part of the changes

* Mon Oct 15 2007 Frederic Crozat <fcrozat@mandriva.com> 2.4.2-9mdv2008.1
+ Revision: 98588
- Patch4 (SUSE): fix duplicated pattern in Qt (Mdv bug #34753, Novell bug #244579)

* Tue Sep 11 2007 Frederic Crozat <fcrozat@mandriva.com> 2.4.2-8mdv2008.0
+ Revision: 84453
- Update source3 to disable all rules until QT4 is fixed, including minimal size rules

* Sat Sep 01 2007 Funda Wang <fwang@mandriva.org> 2.4.2-7mdv2008.0
+ Revision: 77327
- Move wqy config rule into main fontconfig package

* Wed Aug 29 2007 Frederic Crozat <fcrozat@mandriva.com> 2.4.2-6mdv2008.0
+ Revision: 74722
- Rename all mdv configuration files to use the upstream ordering (Mdv bug #26818)
- Update source5 to also provide Fixed font substitute for QT
- Update source1 to provide Fixed font alias (and use Liberation font for MS aliases)
- enable back 20-fix-globaladvanced.conf
- Update source3 to not disable AA on some CJK fonts to workaround QT4 bug (Mdv bug #30877)
- Update source6 with new aliases from Fedora and Hirosi UTUMI
- Validate all configuration file when building package
- Patch2 (GIT): various fixes
- Patch3 (SUSE): fix crash with invalid configuration

* Thu Aug 16 2007 Thierry Vignaud <tv@mandriva.org> 2.4.2-5mdv2008.0
+ Revision: 64224
- tag /etc/fonts/fonts.dtd as %%conffile

* Fri Apr 20 2007 Funda Wang <fwang@mandriva.org> 2.4.2-4mdv2008.0
+ Revision: 15246
- really disable wqy-bitmapfont.
- really disable wqy-bitmapfont.

* Thu Apr 19 2007 Funda Wang <fwang@mandriva.org> 2.4.2-3mdv2008.0
+ Revision: 14925
- Drop wqy-bitmapfont from alternative list.


* Fri Dec 29 2006 Frederic Crozat <fcrozat@mandriva.com> 2.4.2-2mdv2007.0
+ Revision: 102607
- bunzip patch
- Update patch0 / source 3 for new japanese fonts (Mdv bug #27161)
- Release 2.4.2
- Add source8: disable embedded pixmap for big size (Mdv bug #25924)
- Import fontconfig

* Tue Sep 19 2006 Frederic Crozat <fcrozat@mandriva.com> 2.4.1-1mdv2007.0
- Release 2.4.1
- reupdate patch1, to really fix DejaVu preference over Vera
- Remove patch2, merged upstream

* Sat Sep 16 2006 Frederic Crozat <fcrozat@mandriva.com> 2.4.0-3mdv2007.0
- Update patch1 to prefer DejaVu over Vera (regression for QT) (Mdv bug #25648)

* Wed Sep 13 2006 Frederic Crozat <fcrozat@mandriva.com> 2.4.0-2mdv2007.0
- Patch2 (GIT): add ppc64 signature
- Config files are no longer noreplace, otherwise update may break (Mdv bug #25609)
- Users should create additionnal files in /etc/fonts/conf.d

* Tue Sep 12 2006 Frederic Crozat <fcrozat@mandriva.com> 2.4.0-1mdv2007.0
- Release 2.4.0 (yes, it is stable)
- Regenerate patch1
- Add source6 (previously in patch1)
- Remove patch2 (merged upstream)-
- Update source4 to no longer disable hinting for CJK (Mdv bug #22629)
- Update source1 to fix Mdv bug #21940

* Sat May 20 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.95-3mdk
- Rebuild with modular xorg

* Fri May 19 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.95-2mdk
- Patch2 (DavidTurner): speedup fontconfig cache regeneration

* Thu Apr 27 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.95-1mdk
- Release 2.3.95
- Regenerate patch1
- Regenerate source1, symbol part is now merged upstream

* Mon Feb 27 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.94-1mdk
- Release 2.3.94

* Mon Feb 20 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.93-11mdk
- New CVS Snapshot (20060218)
- Remove patches 2, 3, 4, 5, 6, 7 (merged upstream)
- Force a system cache cleanup when upgrading for earlier releases

* Fri Feb 03 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.93-10mdk
- Patch7 (SUSE): fix endless loop with symlink pointing to parent dir

* Thu Feb 02 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.93-9mdk
- Patch2 (SUSE): fix crash
- Patch3 (SUSE): fix font subdir parsing
- Patch4 (SUSE): code cleanup
- Patch5 (SUSE): memleak fix
- Patch6 (SUSE): fix cache update check

* Tue Jan 31 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.93-8mdk
- Update to CVS snapshot 20060131
- Remove patches 2, 3, 4, 5 (merged upstream)

* Mon Jan 30 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.93-7mdk
- Patch5: fix old manpages (Mdk bug #20893)

* Thu Jan 12 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.93-6mdk
- Patch4 (Mike Fabian): normalize path in fc-cache

* Thu Jan 12 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.93-5mdk
- Patch2 (Mike Fabian): fix global dir handling (fix some crash)
- Patch3 (Mike Fabian): fix one crash in fc-cat

* Wed Jan 11 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.93-4mdk
- Update to CVS snapshot 20060111
- remove patches 2 & 3 (merged upstream)

* Wed Jan 04 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.93-3mdk
- Patch3: resolve path argument in fc-cache

* Wed Jan 04 2006 Frederic Crozat <fcrozat@mandriva.com> 2.3.93-2mdk
- System cache files are now located in /var/cache/fontconfig

* Mon Jan 02 2006 Helio Chissini de Castro <helio@mandriva.com> 2.3.93-1mdk
- Update for final 2.3.93
- Remove bad cmap patch
- Added L.Lunak patch to avoid random crashes with memory map

* Wed Nov 30 2005 Frederic Crozat <fcrozat@mandriva.com> 2.3.92-7mdk
- Update to 2.3.93-CVS snapshot 20051130
- Remove patches 14, 15, 16, 17, 18, 19 (merged upstream), patch13 (no longer needed)

* Wed Nov 23 2005 Frederic Crozat <fcrozat@mandriva.com> 2.3.92-6mdk
- Patch18: fix fc-match -s not detected correctly
- Patch19: fix warnings

* Fri Nov 18 2005 Frederic Crozat <fcrozat@mandriva.com> 2.3.92-5mdk
- Patch16: fix invalid free in config load (reported by SadEagle)
- Patch17: fix crash in fc-cat

* Thu Nov 17 2005 Frederic Crozat <fcrozat@mandriva.com> 2.3.92-4mdk
- Patch15 (sunmoon1997): fix crash with invalid config file

* Wed Nov 16 2005 Frederic Crozat <fcrozat@mandriva.com> 2.3.92-3mdk
- Update patch7 and source3 with new chinese fonts (Mdk bug #19811)

* Wed Nov 16 2005 Frederic Crozat <fcrozat@mandriva.com> 2.3.92-2mdk
- Patch14: add warnings when invalid const value are used
- Update source6, don't blacklist Luxi Mono

* Wed Nov 09 2005 Frederic Crozat <fcrozat@mandriva.com> 2.3.92-1mdk
- Release 2.3.92 (development release) aka mmap cache 
- Remove patches 0 (no longer needed), 14 (merged upstream)
- Regenerate patch7
- Replace patch5 with source6 (replacing patch with config file is always better)
- Patch13: prevent cache corruption
- use libxml2 instead of expat

* Thu Aug 18 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 2.3.2-5mdk
- built-in libtool fixes

* Sat Aug 13 2005 Frederic Crozat <fcrozat@mandriva.com> 2.3.2-4mdk
- fix prereq, it was incorrect
- reduce patch 7, remove patches 9, 10, 13, use several individual 
  configuration files in conf.d, suggestion from Funda Wang (Mdk bug #17237)
- add more aliases for Helvetica (Guiseppe)

* Thu Aug 11 2005 Nicolas Lécureuil <neoclust@mandriva.org> 2.3.2-3mdk
- Fix PreReq
     - Close ticket 17438

* Wed Aug 03 2005 Frederic Crozat <fcrozat@mandriva.com> 2.3.2-2mdk 
- Patch14 (CVS): don't include config files ending with .rpmnew/.rpmsave

* Fri Apr 29 2005 Frederic Crozat <fcrozat@mandriva.com> 2.3.2-1mdk
- New release 2.3.2
- regenerate patch 7

* Mon Mar 14 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.3.1-2mdk 
- Really update patch 8

* Thu Mar 10 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.3.1-1mdk 
- Release 2.3.1
- Update patch8 (fix Mdk bug 13357)

* Wed Mar 02 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.3.0-1mdk 
- Release 2.3.0
- Regenerate patch 8

* Wed Feb 16 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.2.99-3mdk 
- Update patch7 to fix default chinese fonts (Funda Wang) (Mdk bug #13357)

* Fri Feb 04 2005 Pablo Saratxaga <pablo@mandrakesoft.com> 2.2.99-2mdk>
- aliases for the new Han and tifinagh fonts

* Mon Jan 31 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.2.99-1mdk
- New release 2.2.99

* Wed Jan 12 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.2.98-2mdk 
- Update patch8 to no discard bitmap fonts

* Tue Jan 11 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.2.98-1mdk 
- Release 2.2.98
- Remove patches 3, 8, 11 (merged upstream)
- Regenerate patches 5, 7

* Wed Nov 10 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.2.96-8mdk
- patch 13: dejavu is vera compatible (vera+extra symbols)

* Sat Sep 25 2004 Pablo Saratxaga <pablo@mandrakesoft.com> 2.2.96-7mdk
- fixed some of the aliases to mach new names (and comments about
  fonts coverage)
- disabled hinting for CJK fonts (UTUMI Hirosi patch)

* Wed Aug 11 2004 Pablo Saratxaga <pablo@mandrakesoft.com> 2.2.96-6mdk
- fixed width of dual width monospace fonts (typically CJK fonts)
- improved language coverage detection

* Wed Aug 11 2004 Pablo Saratxaga <pablo@mandrakesoft.com> 2.2.96-5mdk
- disactivated hinting for "Mukti Narrow" and "Likhan"
- inclusion of culmus.conf
- "Mitra Mono" (bengali monospace font) added to monospace aliases

* Fri Aug 06 2004 Pablo Saratxaga <pablo@mandrakesoft.com> 2.2.96-4mdk
- Some more font aliases

* Wed Jul 28 2004 Christiaan Welvaart <cjw@daneel.dyndns.org> 2.2.96-3mdk
- add BuildRequires: lynx

* Fri Jul 09 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.2.96-2mdk
- Fix buildrequires

* Tue Jul 06 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.2.96-1mdk
- Release 2.2.96 
- Enable libtoolize

* Wed Jun 09 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.2.95-1mdk
- Release 2.2.95
- Remove patch10 (merged upstream)

* Fri May 14 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.2.94-1mdk
- Release 2.2.94
- Patch10 : fix build with latest freetype
- Fix recognition of some bitmap fonts (Mdk bug #9652)
- Remove patch6 (merged upstream)
- Regenerate patch7 and add more aliases for some known fonts (Fedora)
- Regenerate patch9

* Sat Apr 03 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.2.2-1mdk
- Release 2.2.2
- Remove patch10 (merged upstream)

