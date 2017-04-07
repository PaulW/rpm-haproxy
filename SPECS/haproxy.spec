%define haproxy_user    haproxy
%define haproxy_group   %{haproxy_user}
%define haproxy_home    %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy
%define haproxy_datadir %{_datadir}/haproxy
%global _hardened_build 1
Name:           haproxy
Version:        1.7.5
Release:        3%{?dist}.1
Summary:        TCP/HTTP proxy and load balancer for high availability environments
Group:          System Environment/Daemons
License:        GPLv2+
URL:            http://www.haproxy.org/
Source0:        http://www.haproxy.org/download/1.7/src/%{name}-%{version}.tar.gz
Source1:        %{name}.service
Source2:        %{name}.cfg
Source3:        %{name}.logrotate
Source4:        %{name}.sysconfig
Source5:        halog.1
BuildRequires:  pcre-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
BuildRequires:  systemd-units
Requires(pre):      shadow-utils
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
%description
HAProxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
 - route HTTP requests depending on statically assigned cookies
 - spread load among several servers while assuring server persistence
   through the use of HTTP cookies
 - switch to backup servers in the event a main server fails
 - accept connections to special ports dedicated to service monitoring
 - stop accepting connections without breaking existing ones
 - add, modify, and delete HTTP headers in both directions
 - block requests matching particular patterns
 - report detailed status to authenticated users from a URI
   intercepted by the application
%prep
%setup -q
%define __perl_requires /bin/true
%build
regparm_opts=
%ifarch %ix86 x86_64
regparm_opts="USE_REGPARM=1"
%endif
%{__make} %{?_smp_mflags} CPU="generic" TARGET="linux2628" USE_OPENSSL=1 USE_PCRE=1 USE_ZLIB=1 ${regparm_opts} ADDINC="%{optflags}" USE_LINUX_TPROXY=1 ADDLIB="%{__global_ldflags}" DEFINE=-DTCP_USER_TIMEOUT=18
pushd contrib/halog
%{__make} halog OPTIMIZE="%{optflags}"
popd
pushd contrib/iprange
%{__make} iprange OPTIMIZE="%{optflags}"
popd
%install
%{__make} install-bin DESTDIR=%{buildroot} PREFIX=%{_prefix} TARGET="linux2628"
%{__make} install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}
%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{haproxy_confdir}/%{name}.cfg
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -p -D -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -p -D -m 0644 %{SOURCE5} %{buildroot}%{_mandir}/man1/halog.1
%{__install} -d -m 0755 %{buildroot}%{haproxy_home}
%{__install} -d -m 0755 %{buildroot}%{haproxy_datadir}
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -p -m 0755 ./contrib/halog/halog %{buildroot}%{_bindir}/halog
%{__install} -p -m 0755 ./contrib/iprange/iprange %{buildroot}%{_bindir}/iprange
%{__install} -p -m 0644 ./examples/errorfiles/* %{buildroot}%{haproxy_datadir}
for httpfile in $(find ./examples/errorfiles/ -type f)
do
    %{__install} -p -m 0644 $httpfile %{buildroot}%{haproxy_datadir}
done
%{__rm} -rf ./examples/errorfiles/
find ./examples/* -type f ! -name "*.cfg" -exec %{__rm} -f "{}" \;
for textfile in $(find ./ -type f -name "*.txt" -o -name README)
do
    %{__mv} $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    %{__rm} -f $textfile.old
done
%pre
getent group %{haproxy_group} >/dev/null || \
       groupadd -g 188 -r %{haproxy_group}
getent passwd %{haproxy_user} >/dev/null || \
       useradd -u 188 -r -g %{haproxy_group} -d %{haproxy_home} \
       -s /sbin/nologin -c "haproxy" %{haproxy_user}
exit 0
%post
%systemd_post %{name}.service
%preun
%systemd_preun %{name}.service
%postun
%systemd_postun_with_restart %{name}.service
%files
%defattr(-,root,root,-)
%doc doc/* examples/
%doc CHANGELOG LICENSE README ROADMAP VERSION
%dir %{haproxy_confdir}
%dir %{haproxy_datadir}
%{haproxy_datadir}/*
%config(noreplace) %{haproxy_confdir}/%{name}.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_unitdir}/%{name}.service
%{_sbindir}/%{name}
%{_sbindir}/%{name}-systemd-wrapper
%{_bindir}/halog
%{_bindir}/iprange
%{_mandir}/man1/*
%attr(-,%{haproxy_user},%{haproxy_group}) %dir %{haproxy_home}
%changelog
* Fri Apr  7 2017 Paul Bramhall <paulwamp@gmail.com> - 1.7.5-1
- updated to 1.7.5

* Tue Feb  6 2017 Tiago Cruz <tiago.cruz@movile.com> - 1.7.2-1
- updated to 1.7.2
- changed to target linux2628 due to cpu-map and USE_CPU_AFFINITY
- included user/group haproxy in package
- added support to openssl

* Tue Oct 13 2015 Willy Tarreau <w@1wt.eu> - 1.6.0-1
- updated to 1.6.0

* Tue Oct  6 2015 Willy Tarreau <w@1wt.eu> - 1.6-dev7-1
- updated to 1.6-dev7

* Mon Sep 28 2015 Willy Tarreau <w@1wt.eu> - 1.6-dev6-1
- updated to 1.6-dev6

* Mon Sep 14 2015 Willy Tarreau <w@1wt.eu> - 1.6-dev5-1
- updated to 1.6-dev5

* Sun Aug 30 2015 Willy Tarreau <w@1wt.eu> - 1.6-dev4-2
- updated to 1.6-dev4

* Sun Aug 30 2015 Willy Tarreau <w@1wt.eu> - 1.6-dev4-1
- updated to 1.6-dev4

* Wed Jul 22 2015 Willy Tarreau <w@1wt.eu> - 1.6-dev3-1
- updated to 1.6-dev3

* Wed Jun 17 2015 Willy Tarreau <w@1wt.eu> - 1.6-dev2-1
- updated to 1.6-dev2

* Wed Mar 11 2015 Willy Tarreau <w@1wt.eu> - 1.6-dev1-1
- updated to 1.6-dev1

* Thu Jun 19 2014 Willy Tarreau <w@1wt.eu> - 1.6-dev0-1
- updated to 1.6-dev0

* Thu Jun 19 2014 Willy Tarreau <w@1wt.eu> - 1.5.0-1
- updated to 1.5.0

* Wed May 28 2014 Willy Tarreau <w@1wt.eu> - 1.5-dev26-1
- updated to 1.5-dev26

* Sat May 10 2014 Willy Tarreau <w@1wt.eu> - 1.5-dev25-1
- updated to 1.5-dev25

* Sat Apr 26 2014 Willy Tarreau <w@1wt.eu> - 1.5-dev24-1
- updated to 1.5-dev24

* Wed Apr 23 2014 Willy Tarreau <w@1wt.eu> - 1.5-dev23-1
- updated to 1.5-dev23

* Mon Feb  3 2014 Willy Tarreau <w@1wt.eu> - 1.5-dev22-1
- updated to 1.5-dev22

* Tue Dec 17 2013 Willy Tarreau <w@1wt.eu> - 1.5-dev21-1
- updated to 1.5-dev21

* Mon Dec 16 2013 Willy Tarreau <w@1wt.eu> - 1.5-dev20-1
- updated to 1.5-dev20

* Mon Jun 17 2013 Willy Tarreau <w@1wt.eu> - 1.5-dev19-1
- updated to 1.5-dev19

* Wed Apr  3 2013 Willy Tarreau <w@1wt.eu> - 1.5-dev18-1
- updated to 1.5-dev18

* Fri Dec 28 2012 Willy Tarreau <w@1wt.eu> - 1.5-dev17-1
- updated to 1.5-dev17

* Mon Dec 24 2012 Willy Tarreau <w@1wt.eu> - 1.5-dev16-1
- updated to 1.5-dev16

* Wed Dec 12 2012 Willy Tarreau <w@1wt.eu> - 1.5-dev15-1
- updated to 1.5-dev15

* Mon Nov 26 2012 Willy Tarreau <w@1wt.eu> - 1.5-dev14-1
- updated to 1.5-dev14

* Thu Nov 22 2012 Willy Tarreau <w@1wt.eu> - 1.5-dev13-1
- updated to 1.5-dev13

* Mon Sep 10 2012 Willy Tarreau <w@1wt.eu> - 1.5-dev12-1
- updated to 1.5-dev12

* Mon Jun  4 2012 Willy Tarreau <w@1wt.eu> - 1.5-dev11-1
- updated to 1.5-dev11

* Mon May 14 2012 Willy Tarreau <w@1wt.eu> - 1.5-dev10-1
- updated to 1.5-dev10

* Tue May  8 2012 Willy Tarreau <w@1wt.eu> - 1.5-dev9-1
- updated to 1.5-dev9

* Mon Mar 26 2012 Willy Tarreau <w@1wt.eu> - 1.5-dev8-1
- updated to 1.5-dev8

* Sat Sep 10 2011 Willy Tarreau <w@1wt.eu> - 1.5-dev7-1
- updated to 1.5-dev7

* Fri Apr  8 2011 Willy Tarreau <w@1wt.eu> - 1.5-dev6-1
- updated to 1.5-dev6

* Tue Mar 29 2011 Willy Tarreau <w@1wt.eu> - 1.5-dev5-1
- updated to 1.5-dev5

* Sun Mar 13 2011 Willy Tarreau <w@1wt.eu> - 1.5-dev4-1
- updated to 1.5-dev4

* Thu Nov 11 2010 Willy Tarreau <w@1wt.eu> - 1.5-dev3-1
- updated to 1.5-dev3

* Sat Aug 28 2010 Willy Tarreau <w@1wt.eu> - 1.5-dev2-1
- updated to 1.5-dev2

* Wed Aug 25 2010 Willy Tarreau <w@1wt.eu> - 1.5-dev1-1
- updated to 1.5-dev1

* Sun May 23 2010 Willy Tarreau <w@1wt.eu> - 1.5-dev0-1
- updated to 1.5-dev0

* Sun May 16 2010 Willy Tarreau <w@1wt.eu> - 1.4.6-1
- updated to 1.4.6

* Thu May 13 2010 Willy Tarreau <w@1wt.eu> - 1.4.5-1
- updated to 1.4.5

* Wed Apr  7 2010 Willy Tarreau <w@1wt.eu> - 1.4.4-1
- updated to 1.4.4

* Tue Mar 30 2010 Willy Tarreau <w@1wt.eu> - 1.4.3-1
- updated to 1.4.3

* Wed Mar 17 2010 Willy Tarreau <w@1wt.eu> - 1.4.2-1
- updated to 1.4.2

* Thu Mar  4 2010 Willy Tarreau <w@1wt.eu> - 1.4.1-1
- updated to 1.4.1

* Fri Feb 26 2010 Willy Tarreau <w@1wt.eu> - 1.4.0-1
- updated to 1.4.0

* Tue Feb  2 2010 Willy Tarreau <w@1wt.eu> - 1.4-rc1-1
- updated to 1.4-rc1

* Mon Jan 25 2010 Willy Tarreau <w@1wt.eu> - 1.4-dev8-1
- updated to 1.4-dev8

* Mon Jan 25 2010 Willy Tarreau <w@1wt.eu> - 1.4-dev7-1
- updated to 1.4-dev7

* Fri Jan  8 2010 Willy Tarreau <w@1wt.eu> - 1.4-dev6-1
- updated to 1.4-dev6

* Sun Jan  3 2010 Willy Tarreau <w@1wt.eu> - 1.4-dev5-1
- updated to 1.4-dev5

* Mon Oct 12 2009 Willy Tarreau <w@1wt.eu> - 1.4-dev4-1
- updated to 1.4-dev4

* Thu Sep 24 2009 Willy Tarreau <w@1wt.eu> - 1.4-dev3-1
- updated to 1.4-dev3

* Sun Aug  9 2009 Willy Tarreau <w@1wt.eu> - 1.4-dev2-1
- updated to 1.4-dev2

* Wed Jul 29 2009 Willy Tarreau <w@1wt.eu> - 1.4-dev1-1
- updated to 1.4-dev1

* Tue Jun 09 2009 Willy Tarreau <w@1wt.eu> - 1.4-dev0-1
- updated to 1.4-dev0

* Sun May 10 2009 Willy Tarreau <w@1wt.eu> - 1.3.18-1
- updated to 1.3.18

* Sun Mar 29 2009 Willy Tarreau <w@1wt.eu> - 1.3.17-1
- updated to 1.3.17

* Sun Mar 22 2009 Willy Tarreau <w@1wt.eu> - 1.3.16-1
- updated to 1.3.16

* Sat Apr 19 2008 Willy Tarreau <w@1wt.eu> - 1.3.15-1
- updated to 1.3.15

* Wed Dec  5 2007 Willy Tarreau <w@1wt.eu> - 1.3.14-1
- updated to 1.3.14

* Thu Oct 18 2007 Willy Tarreau <w@1wt.eu> - 1.3.13-1
- updated to 1.3.13

* Sun Jun 17 2007 Willy Tarreau <w@1wt.eu> - 1.3.12-1
- updated to 1.3.12

* Sun Jun  3 2007 Willy Tarreau <w@1wt.eu> - 1.3.11.4-1
- updated to 1.3.11.4

* Mon May 14 2007 Willy Tarreau <w@1wt.eu> - 1.3.11.3-1
- updated to 1.3.11.3

* Mon May 14 2007 Willy Tarreau <w@1wt.eu> - 1.3.11.2-1
- updated to 1.3.11.2

* Mon May 14 2007 Willy Tarreau <w@1wt.eu> - 1.3.11.1-1
- updated to 1.3.11.1

* Mon May 14 2007 Willy Tarreau <w@1wt.eu> - 1.3.11-1
- updated to 1.3.11

* Thu May 10 2007 Willy Tarreau <w@1wt.eu> - 1.3.10.2-1
- updated to 1.3.10.2

* Tue May 09 2007 Willy Tarreau <w@1wt.eu> - 1.3.10.1-1
- updated to 1.3.10.1

* Tue May 08 2007 Willy Tarreau <w@1wt.eu> - 1.3.10-1
- updated to 1.3.10

* Sun Apr 15 2007 Willy Tarreau <w@1wt.eu> - 1.3.9-1
- updated to 1.3.9

* Tue Apr 03 2007 Willy Tarreau <w@1wt.eu> - 1.3.8.2-1
- updated to 1.3.8.2

* Sun Apr 01 2007 Willy Tarreau <w@1wt.eu> - 1.3.8.1-1
- updated to 1.3.8.1

* Sun Mar 25 2007 Willy Tarreau <w@1wt.eu> - 1.3.8-1
- updated to 1.3.8

* Wed Jan 26 2007 Willy Tarreau <w@1wt.eu> - 1.3.7-1
- updated to 1.3.7

* Wed Jan 22 2007 Willy Tarreau <w@1wt.eu> - 1.3.6-1
- updated to 1.3.6

* Wed Jan 07 2007 Willy Tarreau <w@1wt.eu> - 1.3.5-1
- updated to 1.3.5

* Wed Jan 02 2007 Willy Tarreau <w@1wt.eu> - 1.3.4-1
- updated to 1.3.4

* Wed Oct 15 2006 Willy Tarreau <w@1wt.eu> - 1.3.3-1
- updated to 1.3.3

* Wed Sep 03 2006 Willy Tarreau <w@1wt.eu> - 1.3.2-1
- updated to 1.3.2

* Wed Jul 09 2006 Willy Tarreau <w@1wt.eu> - 1.3.1-1
- updated to 1.3.1

* Wed May 21 2006 Willy Tarreau <willy@w.ods.org> - 1.2.14-1
- updated to 1.2.14

* Wed May 01 2006 Willy Tarreau <willy@w.ods.org> - 1.2.13-1
- updated to 1.2.13

* Wed Apr 15 2006 Willy Tarreau <willy@w.ods.org> - 1.2.12-1
- updated to 1.2.12

* Wed Mar 30 2006 Willy Tarreau <willy@w.ods.org> - 1.2.11-1
- updated to 1.2.11.1

* Wed Mar 19 2006 Willy Tarreau <willy@w.ods.org> - 1.2.10-1
- updated to 1.2.10

* Wed Mar 15 2006 Willy Tarreau <willy@w.ods.org> - 1.2.9-1
- updated to 1.2.9

* Sat Jan 22 2005 Willy Tarreau <willy@w.ods.org> - 1.2.3-1
- updated to 1.2.3 (1.1.30)

* Sun Nov 14 2004 Willy Tarreau <w@w.ods.org> - 1.1.29-1
- updated to 1.1.29
- fixed path to config and init files
- statically linked PCRE to increase portability to non-pcre systems

* Sun Jun  6 2004 Willy Tarreau <willy@w.ods.org> - 1.1.28-1
- updated to 1.1.28
- added config check support to the init script

* Tue Oct 28 2003 Simon Matter <simon.matter@invoca.ch> - 1.1.27-1
- updated to 1.1.27
- added pid support to the init script

* Wed Oct 22 2003 Simon Matter <simon.matter@invoca.ch> - 1.1.26-2
- updated to 1.1.26

* Thu Oct 16 2003 Simon Matter <simon.matter@invoca.ch> - 1.1.26-1
- initial build
