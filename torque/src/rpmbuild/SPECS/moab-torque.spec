%global pkg_name moab-torque
%global pkg_ver 6.1.2
%global pkg_rls 7aci
%global pkg_summ Tera-scale Open-source Resource and QUEue manager
%global pkg_desc TORQUE is an open source resource manager providing control over batch\
jobs and distributed compute nodes. It is a community effort based on\
the original *PBS project and, with more than 5,200 patches, has\
incorporated significant advances in the areas of scalability, fault\
tolerance, and feature extensions contributed by NCSA, OSC, USC, the\
U.S. Dept of Energy, Sandia, PNNL, U of Buffalo, TeraGrid, and many\
other leading edge HPC organizations.


# Set some variables for reuse
%define _prefix /usr/local
%define _mandir %{_prefix}/man
%define _infodir %{_prefix}/info
%define _initddir %{_sysconfdir}/init.d
%define torquehomedir /var/spool/torque
%define pbs_server torque01.util.production.int.aci.ics.psu.edu
%define nvml_lib /usr/lib64/nvidia
%define nvml_inc /usr/local/cuda-8.0/include
%define sendmail /sbin/sendmail
%define xauth /usr/bin/xauth 

%if 0%{?el6:1}
%define hwlocpkg hwloc1.11.4
%define hwlocdir /opt/aci/sys/hwloc
%define hwlocopt --with-hwloc-path=%{hwlocdir}
%else
%define hwlocpkg hwloc
%define hwlocdir /usr
%endif

# Conditional build items

### Features disabled by default
%bcond_with nvidia
#%bcond_with cgroups
#%bcond_with drmaa
#%bcond_with gui
#%bcond_with memacct
#%bcond_with munge
#%bcond_with numa
#%bcond_with pam
#%bcond_with top
#%bcond_with readline
%bcond_with autoconf
%bcond_with disable_bind_outbound_sockets

### Features enabled by default
#%bcond_without clients
#%bcond_without debug
%bcond_without mom
#%bcond_without scp
%bcond_without server
#%bcond_without spool
#%bcond_without syslog
#%bcond_without xauth
%bcond_without appendgpu

### Autoconf style macros
%define ac_with_nvidia %{?with_nvidia:--enable-nvidia-gpus --with-nvml-lib=%{nvml_lib} --with-nvml-include=%{nvml_inc}}
%define ac_with_mom --%{?with_mom:en}%{!?with_mom:dis}able-mom
%define ac_with_server --%{?with_server:en}%{!?with_server:dis}able-server
%define ac_with_disable_bind_outbound_sockets --disable-bind-outbound-sockets

# some binaries under /bin in el6 are only provided in /usr/bin in el7+.
# the el7 rpms actually provide the old location, but can't be used as a rpm requirement
# introducing the rootbin macro for this, as none seems to exists
%if 0%{?el6:1}
%define rootbin /bin
%else
%define rootbin /usr/bin
%endif

### Define appended string for gpu-enabled builds
%define gpu_suffix %{?with_appendgpu:-gpu}%{!?with_appendgpu:%{nil}}

### Do not strip executables when debugging.
%global __os_install_post /usr/lib/rpm/brp-compress
%global __debug_install_post %{nil}
%global debug_package %{nil}


Name:          %{pkg_name}
Version:       %{pkg_ver}
Release:       %{pkg_rls}%{?dist}
Summary:       Tera-scale Open-source Resource and QUEue manager
License:       OpenPBS and TORQUEv1.1
Group:         Applications/System
URL:           http://www.adaptivecomputing.com/products/open-source/torque/
Source0:       torque-%{version}.tar.gz
Patch1:        nvml.patch
Patch2:        revise.patch
Patch3:        TRQ-4057-mom.patch
Patch4:        cgroups-log.patch
Patch5:        TRQ-4035-KNL-crash6111.patch
Patch6:        TRQ-4036-arst_string.patch
Patch7:        TRQ-4047-memory-only-nodes.patch
Patch8:        trq-4051.6111.loggingpatch.patch
Patch9:        TRQ-4213.612.patch
Patch10:       TRQ-4208.612.patch
Patch11:       trq-4250.612.patch3.txt
Patch12:       MissingGPU.patch
%if 0%{?with_nvidia}
AutoReq:   no
%endif
BuildRequires: openssl-devel libxml2-devel boost-devel pam-devel xauth 
BuildRequires: pkgconfig(hwloc) %{?with_nvidia:cuda-nvml-dev-8-0}
Requires:      zlib libxml2 openssl
Conflicts:     pbspro, openpbs, openpbs-oscar
Conflicts:     moab-torque%{!?with_nvidia:%{gpu_suffix}}
Provides:      pbs
Provides:      torque
Provides:       moab-torque%{?with_nvidia:%{gpu_suffix}}

%description
TORQUE is an open source resource manager providing control over batch
jobs and distributed compute nodes. It is a community effort based on
the original *PBS project and, with more than 5,200 patches, has
incorporated significant advances in the areas of scalability, fault
tolerance, and feature extensions contributed by NCSA, OSC, USC, the
U.S. Dept of Energy, Sandia, PNNL, U of Buffalo, TeraGrid, and many
other leading edge HPC organizations.


%package common%{?with_nvidia:%{gpu_suffix}}
Summary:   TORQUE Common Files
Group:     Applications/System
%if 0%{?with_nvidia}
AutoReq:   no
%endif
Requires:  syslog %{?with_nvidia:/usr/lib64/nvidia/libnvidia-ml.so.1}
Provides:  torque-common
Provides:  pbs-common
Conflicts: moab-torque-common%{!?with_nvidia:%{gpu_suffix}}

%description common%{?with_nvidia:%{gpu_suffix}}
Common files shared by TORQUE Server, Client, and MOM packages


%package client%{?with_nvidia:%{gpu_suffix}}
Summary:   TORQUE Client
Group:     Applications/System
%if 0%{?with_nvidia}
AutoReq:   no
%endif
Requires:  moab-torque-common%{?with_nvidia:%{gpu_suffix}} = %{version}-%{release}
Requires:  syslog %{?with_nvidia:/usr/lib64/nvidia/libnvidia-ml.so.1}
Provides:  torque-client
Provides:  pbs-client
Conflicts: moab-torque-client%{!?with_nvidia:%{gpu_suffix}}

%description client%{?with_nvidia:%{gpu_suffix}}
TORQUE Client provides the client utilities necessary for interacting with
TORQUE Server.


%if %{with mom}
%package mom%{?with_nvidia:%{gpu_suffix}}
Summary:   TORQUE MOM agent
Group:     Applications/System
%if 0%{?with_nvidia}
AutoReq:   no
%endif
Requires:  moab-torque-client%{?with_nvidia:%{gpu_suffix}} = %{version}-%{release}
Requires:  libcgroup
Requires:  %{hwlocpkg}
Requires:  %{rootbin}/lssubsys %{?with_nvidia:/usr/lib64/nvidia/libnvidia-ml.so.1}
Provides:  torque-mom
Provides:  pbs-mom
Conflicts: moab-torque-mom%{!?with_nvidia:%{gpu_suffix}}

%description mom%{?with_nvidia:%{gpu_suffix}}
TORQUE MOM provides the agent necessary for each compute node in a
TORQUE-managed batch system.
%endif


%package pam%{?with_nvidia:%{gpu_suffix}}
Summary:   PAM module for TORQUE MOM nodes
Group:     Applications/System
%if 0%{?with_nvidia}
AutoReq:   no
%endif
Requires:  moab-torque-mom%{?with_nvidia:%{gpu_suffix}} = %{version}-%{release}
Requires:  pam
Provides:  torque-pam
Provides:  pbs-pam
Conflicts: moab-torque-pam%{!?with_nvidia:%{gpu_suffix}}

%description pam%{?with_nvidia:%{gpu_suffix}}
A simple PAM module to authorize users on PBS MOM nodes with a running job.


%if %{with server}
%package server%{?with_nvidia:%{gpu_suffix}}
Summary:   TORQUE Server
Group:     Applications/System
%if 0%{?with_nvidia}
AutoReq:   no
%endif
Requires:  moab-torque-client%{?with_nvidia:%{gpu_suffix}} = %{version}-%{release}
Requires:  libcgroup
Requires:  %{hwlocpkg}
Requires:  %{rootbin}/lssubsys
Requires:  %{sendmail}
Provides:  torque-server
Provides:  pbs-server
Conflicts: moab-torque-server%{!?with_nvidia:%{gpu_suffix}}

%description server%{?with_nvidia:%{gpu_suffix}}
TORQUE Resource Manager provides control over batch jobs and distributed
computing resources. It is an advanced open-source product based on the
original PBS project* and incorporates the best of both community and
professional development.
%endif


%package devel%{?with_nvidia:%{gpu_suffix}}
Summary:   TORQUE Development Files
Group:     Applications/System
%if 0%{?with_nvidia}
AutoReq:   no
%endif
Requires:  moab-torque-client%{?with_nvidia:%{gpu_suffix}} = %{version}-%{release}
Provides:  torque-devel
Provides:  pbs-devel
Conflicts: moab-torque-devel%{!?with_nvidia:%{gpu_suffix}}

%description devel%{?with_nvidia:%{gpu_suffix}}
Development headers and libraries for TORQUE


%prep
%setup -q -n torque-%{version}
#%patch1 -p 1
#%patch2 -p 1
%patch3 -p 1
#%patch4 -p 1
#%patch5 -p 1
#%patch6 -p 1
#%patch7 -p 1
#%patch8 -p 1
%patch9 -p 1
%patch10 -p 1
%patch11 -p 1
%patch12 -p 1

%build
# Increase debugging over default level of 2
CFLAGS="-g3 -O0"
CXXFLAGS="-g3 -O0"
LDFLAGS="-g3 -O0 $(pkg-config hwloc --libs)"
export CFLAGS CXXFLAGS LDFLAGS
%if %{with autoconf}
sh ./autogen.sh
%endif
%configure --includedir=%{_includedir}/torque \
    --oldincludedir=/usr/include --datarootdir=%{_datarootdir} \
    --localedir=%{_datadir}/locale --docdir=%{_docdir} \
    --htmldir=%{_datadir}/doc --dvidir=%{_datadir}/doc \
    --pdfdir=%{_datadir}/doc --psdir=%{_datadir}/doc \
    --with-server-home=%{torquehomedir} --with-sendmail=%{sendmail} \
    --disable-dependency-tracking --disable-qsub-keep-override --with-debug \
    --without-tcl --with-rcp=scp --enable-syslog --disable-munge-auth \
    --disable-blcr --disable-cpuset --enable-spool --disable-gui \
    %{ac_with_server} %{ac_with_mom} %{ac_with_disable_bind_outbound_sockets} \
    --with-pam --enable-cgroups --with-xauth=%{xauth} \
    %{?hwlocopt:%{hwlocopt}} %{ac_with_nvidia} --disable-gcc-warnings \
    --with-default-server=%{pbs_server}

make %{?_smp_mflags}

%install
%{__make} DESTDIR=%{buildroot} INSTALL="install -p" install

# Remove some unneeded libraries
rm -f %{buildroot}%{_libdir}/*.{a,la}
rm -f %{buildroot}/%{_lib}/security/pam_pbssimpleauth.{a,la}

# Remove man pages for binaries we aren't building
rm -f %{buildroot}%{_mandir}/man1/basl2c.1
#rm -f %{buildroot}%{_mandir}/man8/pbs_sched*
rm -f %{buildroot}%{_mandir}/man1/xpbs*

# Remove remnants of pbs_sched since this build is for use with Moab
#rm -f %{buildroot}%{_sbindir}/pbs_sched
#rm -f %{buildroot}%{_sbindir}/qschedd
#rm -Rf %{buildroot}%{torquehomedir}/sched_priv

# Add hwloc path for ldconfig on RHEL 6 system
%if 0%{?el6:1}
cat <<EOF >%{buildroot}/etc/ld.so.conf.d/torque.conf
%{hwlocdir}/lib
/usr/local/lib64
EOF
%endif

%if %{with mom}
echo '$pbsserver %{pbs_server}' > %{buildroot}%{torquehomedir}/mom_priv/config
%else
rm -f %{buildroot}%{_mandir}/man8/pbs_mom*
%endif

# Moab requires a libtorque.so.0, but works with libtorque.so.2
%{__ln_s} libtorque.so.2 %{buildroot}%{_libdir}/libtorque.so.0


%if %{with server}
# Create necessary directories
mkdir %{buildroot}%{torquehomedir}/server_priv/{bad_job_state,node_usage}

# Create ghost serverdb
touch %{buildroot}%{torquehomedir}/server_priv/serverdb
%else
rm -f %{buildroot}%{_mandir}/man8/pbs_server*
%endif


%post common%{?with_nvidia:%{gpu_suffix}}
/sbin/ldconfig

%postun common%{?with_nvidia:%{gpu_suffix}} -p /sbin/ldconfig

%post client%{?with_nvidia:%{gpu_suffix}}
%if 0%{?el6:1}
if [ $1 -eq 1 ]; then
    chkconfig --add trqauthd >/dev/null 2>&1 || :
    chkconfig trqauthd on >/dev/null 2>&1 || :
    service trqauthd start >/dev/null 2>&1 || :
else
    service trqauthd try-restart >/dev/null 2>&1 || :
fi
%else
%systemd_post trqauthd.service
%endif

%preun client%{?with_nvidia:%{gpu_suffix}}
%if 0%{?el6:1}
if [ $1 -eq 0 ]; then
    chkconfig trqauthd off >/dev/null 2>&1 || :
    service trqauthd stop >/dev/null 2>&1 || :
    chkconfig --del trqauthd >/dev/null 2>&1 || :
fi
%else
%systemd_preun trqauthd.service
%endif

%if %{with mom}
%post mom%{?with_nvidia:%{gpu_suffix}}
if [ $1 -eq 1 ]; then
    grep 'PBS services' /etc/services >/dev/null 2>&1 || cat <<-EOF >>/etc/services
    # Standard PBS services
    pbs           15001/tcp           # pbs server (pbs_server)
    pbs           15001/udp           # pbs server (pbs_server)
    pbs_mom       15002/tcp           # mom to/from server
    pbs_mom       15002/udp           # mom to/from server
    pbs_resmom    15003/tcp           # mom resource management requests
    pbs_resmom    15003/udp           # mom resource management requests
    pbs_sched     15004/tcp           # scheduler
    pbs_sched     15004/udp           # scheduler
    trqauthd      15005/tcp           # authorization daemon
    trqauthd      15005/udp           # authorization daemon
EOF
fi

%if 0%{?el6:1}
if [ $1 -eq 1 ]; then
    chkconfig --add pbs_mom >/dev/null 2>&1 || :
    chkconfig pbs_mom on >/dev/null 2>&1 || :
    service pbs_mom start >/dev/null 2>&1 || :
else
    service pbs_mom try-restart >/dev/null 2>&1 || :
fi
%else
%systemd_post pbs_mom.service
%endif

%preun mom%{?with_nvidia:%{gpu_suffix}}
%if 0%{?el6:1}
if [ $1 -eq 0 ]; then
    chkconfig pbs_mom off >/dev/null 2>&1 || :
    service pbs_mom stop >/dev/null 2>&1 || :
    chkconfig --del pbs_mom >/dev/null 2>&1 || :
fi
%else
%systemd_preun pbs_mom.service
%endif
%endif

%if %{with server}
%post server%{?with_nvidia:%{gpu_suffix}}
if [ $1 -eq 1 ]; then
    grep 'PBS services' /etc/services >/dev/null 2>&1 || cat <<-EOF >>/etc/services
    # Standard PBS services
    pbs           15001/tcp           # pbs server (pbs_server)
    pbs           15001/udp           # pbs server (pbs_server)
    pbs_mom       15002/tcp           # mom to/from server
    pbs_mom       15002/udp           # mom to/from server
    pbs_resmom    15003/tcp           # mom resource management requests
    pbs_resmom    15003/udp           # mom resource management requests
    pbs_sched     15004/tcp           # scheduler
    pbs_sched     15004/udp           # scheduler
    trqauthd      15005/tcp           # authorization daemon
    trqauthd      15005/udp           # authorization daemon
EOF
    if [ ! -e %{torque_home}/server_priv/serverdb ]; then
        TORQUE_SERVER=`hostname`

        pbs_server -t create -f >/dev/null 2>&1 || :
        sleep 1
        qmgr -c "set server scheduling = true" >/dev/null 2>&1 || :
        qmgr -c "set server managers += root@$TORQUE_SERVER" >/dev/null 2>&1 || :
        qmgr -c "set server managers += %{torque_user}@$TORQUE_SERVER" >/dev/null 2>&1 || :
        qmgr -c "create queue batch queue_type = execution" >/dev/null 2>&1 || :
        qmgr -c "set queue batch started = true" >/dev/null 2>&1 || :
        qmgr -c "set queue batch enabled = true" >/dev/null 2>&1 || :
        qmgr -c "set queue batch resources_default.walltime = 1:00:00" >/dev/null 2>&1 || :
        qmgr -c "set queue batch resources_default.nodes = 1" >/dev/null 2>&1 || :
        qmgr -c "set server default_queue = batch" >/dev/null 2>&1 || :
        qmgr -c "set node $TORQUE_SERVER state = free" >/dev/null 2>&1 || :
        killall -TERM pbs_server >/dev/null 2>&1 || :
    fi
fi

%if 0%{?el6:1}
if [ $1 -eq 1 ]; then
    chkconfig --add pbs_server >/dev/null 2>&1 || :
    chkconfig pbs_server on >/dev/null 2>&1 || :
    service pbs_server start >/dev/null 2>&1 || :
else
    service pbs_server try-restart >/dev/null 2>&1 || :
fi
%else
%systemd_post pbs_server.service
%endif

%preun server%{?with_nvidia:%{gpu_suffix}}
%if 0%{?el6:1}
if [ $1 -eq 0 ]; then
    chkconfig pbs_server off >/dev/null 2>&1 || :
    service pbs_server stop >/dev/null 2>&1 || :
    chkconfig --del pbs_server >/dev/null 2>&1 || :
fi
%else
%systemd_preun pbs_server.service
%endif
%endif

%files common%{?with_nvidia:%{gpu_suffix}}
%defattr(-, root, root)
%doc INSTALL INSTALL.GNU CHANGELOG PBS_License.txt README.* Release_Notes src/pam/README.pam
%doc doc/READ_ME doc/doc_fonts doc/soelim.c doc/ers
%config(noreplace) /etc/ld.so.conf.d/torque.conf
%config(noreplace) %{torquehomedir}/pbs_environment
%config(noreplace) %{torquehomedir}/server_name
%dir %{torquehomedir}/checkpoint
%dir %{torquehomedir}/spool
%{_libdir}/libtorque.so*

%files pam%{?with_nvidia:%{gpu_suffix}}
%defattr(-, root, root)
%doc src/pam/README.pam
/%{_lib}/security/pam_pbssimpleauth.so

%files client%{?with_nvidia:%{gpu_suffix}}
%defattr(-, root, root)
%{_bindir}/q*
%{_bindir}/chk_tree
%{_bindir}/hostn
%{_bindir}/nqs2pbs
%{_bindir}/pbs_track
%{_bindir}/pbsdsh
%{_bindir}/pbsnodes
%{_bindir}/printjob
%{_bindir}/printserverdb
%{_bindir}/printtracking
%{_bindir}/tracejob
%{_sbindir}/trqauthd
%if 0%{?el6:1}
%{_initddir}/trqauthd
%else
%{_unitdir}/trqauthd.service
%endif
/etc/profile.d/torque.sh
/etc/profile.d/torque.csh
%{_mandir}/man1/nqs2pbs.1
%{_mandir}/man1/pbs.1
%{_mandir}/man1/pbsdsh.1
%{_mandir}/man1/qalter.1
%{_mandir}/man1/qchkpt.1
%{_mandir}/man1/qdel.1
%{_mandir}/man1/qgpumode.1
%{_mandir}/man1/qgpureset.1
%{_mandir}/man1/qhold.1
%{_mandir}/man1/qmgr.1
%{_mandir}/man1/qmove.1
%{_mandir}/man1/qmsg.1
%{_mandir}/man1/qorder.1
%{_mandir}/man1/qrerun.1
%{_mandir}/man1/qrls.1
%{_mandir}/man1/qselect.1
%{_mandir}/man1/qsig.1
%{_mandir}/man1/qstat.1
%{_mandir}/man1/qsub.1
%{_mandir}/man7/pbs_job_attributes.7
%{_mandir}/man7/pbs_queue_attributes.7
%{_mandir}/man7/pbs_resources.7
%{_mandir}/man7/pbs_resources_aix4.7
%{_mandir}/man7/pbs_resources_aix5.7
%{_mandir}/man7/pbs_resources_darwin.7
%{_mandir}/man7/pbs_resources_digitalunix.7
%{_mandir}/man7/pbs_resources_freebsd.7
%{_mandir}/man7/pbs_resources_fujitsu.7
%{_mandir}/man7/pbs_resources_hpux10.7
%{_mandir}/man7/pbs_resources_hpux11.7
%{_mandir}/man7/pbs_resources_irix5.7
%{_mandir}/man7/pbs_resources_irix6.7
%{_mandir}/man7/pbs_resources_irix6array.7
%{_mandir}/man7/pbs_resources_linux.7
%{_mandir}/man7/pbs_resources_netbsd.7
%{_mandir}/man7/pbs_resources_solaris5.7
%{_mandir}/man7/pbs_resources_solaris7.7
%{_mandir}/man7/pbs_resources_sp2.7
%{_mandir}/man7/pbs_resources_sunos4.7
%{_mandir}/man7/pbs_resources_unicos8.7
%{_mandir}/man7/pbs_resources_unicosmk2.7
%{_mandir}/man7/pbs_server_attributes.7
%{_mandir}/man8/pbsnodes.8
%{_mandir}/man8/qdisable.8
%{_mandir}/man8/qenable.8
%{_mandir}/man8/qrun.8
%{_mandir}/man8/qstart.8
%{_mandir}/man8/qstop.8
%{_mandir}/man8/qterm.8


%files devel%{?with_nvidia:%{gpu_suffix}}
%defattr(-, root, root)
%{_bindir}/pbs-config
%dir %{_includedir}/torque
%{_includedir}/torque/*
%{_mandir}/man3/pbs_alterjob.3
%{_mandir}/man3/pbs_checkpointjob.3
%{_mandir}/man3/pbs_connect.3
%{_mandir}/man3/pbs_default.3
%{_mandir}/man3/pbs_deljob.3
%{_mandir}/man3/pbs_disconnect.3
%{_mandir}/man3/pbs_fbserver.3
%{_mandir}/man3/pbs_get_server_list.3
%{_mandir}/man3/pbs_geterrmsg.3
%{_mandir}/man3/pbs_gpumode.3
%{_mandir}/man3/pbs_gpureset.3
%{_mandir}/man3/pbs_holdjob.3
%{_mandir}/man3/pbs_locate.3
%{_mandir}/man3/pbs_manager.3
%{_mandir}/man3/pbs_movejob.3
%{_mandir}/man3/pbs_msgjob.3
%{_mandir}/man3/pbs_orderjob.3
%{_mandir}/man3/pbs_rerunjob.3
%{_mandir}/man3/pbs_rescquery.3
%{_mandir}/man3/pbs_rescreserve.3
%{_mandir}/man3/pbs_rlsjob.3
%{_mandir}/man3/pbs_runjob.3
%{_mandir}/man3/pbs_selectjob.3
%{_mandir}/man3/pbs_selstat.3
%{_mandir}/man3/pbs_sigjob.3
%{_mandir}/man3/pbs_stagein.3
%{_mandir}/man3/pbs_statjob.3
%{_mandir}/man3/pbs_statnode.3
%{_mandir}/man3/pbs_statque.3
%{_mandir}/man3/pbs_statserver.3
%{_mandir}/man3/pbs_submit.3
%{_mandir}/man3/pbs_terminate.3
%{_mandir}/man3/tm.3


%if %{with mom}
%files mom%{?with_nvidia:%{gpu_suffix}}
%defattr(-, root, root)
%if 0%{?el6:1}
%{_initddir}/pbs_mom
%else
%{_unitdir}/pbs_mom.service
%endif
%{_mandir}/man8/pbs_mom.8
%{_sbindir}/momctl
%{_sbindir}/pbs_demux
%{_sbindir}/pbs_mom
%{_sbindir}/qnoded
%dir %{torquehomedir}/aux
%dir %{torquehomedir}/mom_logs
%dir %{torquehomedir}/mom_priv
%dir %{torquehomedir}/undelivered
%dir %{torquehomedir}/mom_priv/jobs
%config(noreplace) %{torquehomedir}/mom_priv/config
/etc/profile.d/torque.sh
/etc/profile.d/torque.csh
%endif


%if %{with server}
%files server%{?with_nvidia:%{gpu_suffix}}
%defattr(-, root, root)
%attr(0755, root, root) %{_sbindir}/pbs_server
%{_sbindir}/qserverd
%if 0%{?el6:1}
%{_initddir}/pbs_server
%else
%{_unitdir}/pbs_server.service
%endif
%{_mandir}/man8/pbs_server.8
%dir %{torquehomedir}/server_priv
%dir %{torquehomedir}/server_logs
%config(noreplace) %{torquehomedir}/server_priv/nodes
%ghost %config(noreplace) %{torquehomedir}/server_priv/serverdb
%dir %{torquehomedir}/server_priv/accounting
%dir %{torquehomedir}/server_priv/acl*
%dir %{torquehomedir}/server_priv/arrays
%dir %{torquehomedir}/server_priv/bad_job_state
%dir %{torquehomedir}/server_priv/credentials
%dir %{torquehomedir}/server_priv/disallowed_types
%dir %{torquehomedir}/server_priv/hostlist
%dir %{torquehomedir}/server_priv/jobs
%dir %{torquehomedir}/server_priv/node_usage
%dir %{torquehomedir}/server_priv/queues
# if scheduler
%attr(0755, root, root) %{_sbindir}/pbs_sched
%attr(0755, root, root) %{_sbindir}/qschedd
%{_mandir}/man8/pbs_sched*
%dir %{torquehomedir}/sched_priv
%{torquehomedir}/sched_priv/dedicated_time
%{torquehomedir}/sched_priv/holidays
%{torquehomedir}/sched_priv/resource_group
%{torquehomedir}/sched_priv/sched_config
# endif scheduler

%endif

%changelog
* Tue Jul 03 2018 Adam Focht <abf123@psu.edu> 6.1.2-0.5
- Add TRQ-4213 patch (release 5)
* Mon May 14 2018 Adam Focht <abf123@psu.edu> 6.1.2-0.4
- Add TRQ4208 patch for Adaptive case 26228 (release 4)
