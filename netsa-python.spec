%define name netsa-python
%define version 1.4.3
%define release 1

Summary: NetSA Python
Name: %{name}
Version: %{version}
Release: %{release}
Source: %{name}-%{version}.tar.gz
License: GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: NetSA Group <netsa-help@cert.org>
Url: http://tools.netsa.cert.org/netsa-python/index.html
Requires: netsa_silk >= 1.0
Provides: netsa_silk_impl

%description
A grab-bag of Python routines and frameworks that the NetSA group at SEI
CERT have found helpful when developing analyses using the SiLK toolkit.

%prep
%setup -q

%build
python setup.py build

%install
python setup.py install --record=INSTALLED_FILES_ALL \
    --root=$RPM_BUILD_ROOT --prefix=%{_prefix}
grep -v "/netsa_silk\\.py" INSTALLED_FILES_ALL > INSTALLED_FILES_NETSA_PYTHON
grep "/netsa_silk\\.py" INSTALLED_FILES_ALL > INSTALLED_FILES_NETSA_SILK

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES_NETSA_PYTHON
%defattr(-,root,root)

%package -n netsa_silk
Group: Development/Libraries
Summary: netsa_silk netsa-python PySiLK integration
Version: 1.0
Requires: netsa_silk_impl

%description -n netsa_silk
A shared API for working with common Internet data in both netsa-python
and PySiLK.

%files -n netsa_silk -f INSTALLED_FILES_NETSA_SILK
%defattr(-,root,root)
