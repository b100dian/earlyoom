Name:       earlyoom
Summary:    Early OOM daemon
Version:    1.9.0
Release:    1
License:    MIT
URL:        https://github.com/rfjakob/earlyoom
Source0:    %{name}-%{version}.tar.gz
Patch0:     0001-Make-earlyoom.service-compatible-with-systemd-238.patch

BuildRequires:  systemd
Requires(post): systemd
Requires(postun): systemd

%description
earlyoom checks the amount of available memory and free swap and kills
the largest process (highest oom_score) when both fall below a threshold,
before the kernel enters a long reclaim/thrashing phase.

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
# without GO
CFLAGS="%{optflags}" LDFLAGS="%{?__global_ldflags}" \
make %{?_smp_mflags} \
    VERSION=v%{version} \
    PREFIX=%{_prefix} \
    BINDIR=%{_bindir} \
    SYSCONFDIR=%{_sysconfdir} \
    earlyoom earlyoom.service

%install
rm -rf %{buildroot}
install -D -m 755 earlyoom %{buildroot}%{_bindir}/earlyoom
install -D -m 644 earlyoom.service %{buildroot}%{_unitdir}/earlyoom.service
install -D -m 644 earlyoom.default %{buildroot}%{_sysconfdir}/default/earlyoom
install -d %{buildroot}%{_unitdir}/multi-user.target.wants
ln -s ../earlyoom.service %{buildroot}%{_unitdir}/multi-user.target.wants/earlyoom.service

%post
systemctl daemon-reload || :

%postun
systemctl daemon-reload || :
if [ $1 -ge 1 ]; then
    systemctl try-restart earlyoom.service || :
fi

%files
%defattr(-,root,root,-)
%license LICENSE
%doc README.md MANPAGE.md
%{_bindir}/earlyoom
%{_unitdir}/earlyoom.service
%{_unitdir}/multi-user.target.wants/earlyoom.service
%config(noreplace) %{_sysconfdir}/default/earlyoom
