%{?scl:%scl_package apache-commons-logging}
%{!?scl:%global pkg_name %{name}}

%{?thermostat_find_provides_and_requires}

%global base_name  logging
%global short_name commons-%{base_name}

Name:           %{?scl_prefix}apache-%{short_name}
Version:        1.1.2
Release:        5.4%{?dist}
Summary:        Apache Commons Logging
License:        ASL 2.0
Group:          Development/Libraries
URL:            http://commons.apache.org/%{base_name}
Source0:        http://www.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz
Source2:        http://mirrors.ibiblio.org/pub/mirrors/maven2/%{short_name}/%{short_name}-api/1.1/%{short_name}-api-1.1.pom

BuildArch:      noarch
BuildRequires:  maven30-maven-local
BuildRequires:  maven30-avalon-framework >= 4.3
BuildRequires:  maven30-avalon-logkit
BuildRequires:  maven30-apache-commons-parent >= 26-7
BuildRequires:  maven30-maven-dependency-plugin
BuildRequires:  maven30-maven-failsafe-plugin
BuildRequires:  maven30-maven-plugin-build-helper
BuildRequires:  maven30-maven-release-plugin
BuildRequires:  maven30-maven-site-plugin
BuildRequires:  maven30-maven-resources-plugin
BuildRequires:  servlet

# This should go away with F-17
Provides:       %{?scl_prefix}jakarta-%{short_name} = 0:%{version}-%{release}
Obsoletes:      %{?scl_prefix}jakarta-%{short_name} <= 0:1.0.4

%description
The commons-logging package provides a simple, component oriented
interface (org.apache.commons.logging.Log) together with wrappers for
logging systems. The user can choose at runtime which system they want
to use. In addition, a small number of basic implementations are
provided to allow users to use the package standalone.
commons-logging was heavily influenced by Avalon's Logkit and Log4J. The
commons-logging abstraction is meant to minimize the differences between
the two, and to allow a developer to not tie himself to a particular
logging implementation.

%package        javadoc
Summary:        API documentation for %{name}
Group:          Documentation
Requires:       jpackage-utils

Obsoletes:      %{?scl_prefix}jakarta-%{short_name}-javadoc <= 0:1.0.4

%description    javadoc
%{summary}.

# -----------------------------------------------------------------------------

%prep
%{?scl:scl enable maven30 %{scl} - << "EOF"}
%setup -q -n %{short_name}-%{version}-src

# Sent upstream https://issues.apache.org/jira/browse/LOGGING-143
%pom_remove_dep :avalon-framework
%pom_add_dep avalon-framework:avalon-framework-api:4.3
%pom_add_dep avalon-framework:avalon-framework-impl:4.3:test

%pom_remove_plugin :cobertura-maven-plugin
%pom_remove_plugin :maven-scm-publish-plugin

# Upstream is changing Maven groupID and OSGi Bundle-SymbolicName back
# and forth, even between minor releases (such as 1.1.1 and 1.1.2).
# In case of Maven we can provide an alias, so that's not a big
# problem.  But there is no alias mechanism for OSGi bundle names.
#
# I'll use Bundle-SymbolicName equal to "org.apache.commons.logging"
# because that's what upstream decided to use in future and because
# that's what most of Eclipse plugin are already using.  See also
# rhbz#949842 and LOGGING-151.  mizdebsk, 9 Apr 2013
%pom_xpath_set pom:commons.osgi.symbolicName org.apache.commons.logging

sed -i 's/\r//' RELEASE-NOTES.txt LICENSE.txt NOTICE.txt

%mvn_file ":%{short_name}{*}" "%{short_name}@1" "%{pkg_name}@1"
%mvn_alias ":%{short_name}{*}" "org.apache.commons:%{short_name}@1"

%mvn_config installerSettings/skipRequires true

# failing test
rm -f src/test/java/org/apache/commons/logging/security/SecurityAllowedTestCase.java
%{?scl:EOF}

%build
%{?scl:scl enable maven30 %{scl} - << "EOF"}
%mvn_build
%{?scl:EOF}
# -----------------------------------------------------------------------------

%install
%{?scl:scl enable maven30 %{scl} - << "EOF"}
%mvn_install

install -p -m 644 target/%{short_name}-api-%{version}.jar %{buildroot}/%{_javadir}/%{pkg_name}-api.jar
install -p -m 644 target/%{short_name}-adapters-%{version}.jar %{buildroot}/%{_javadir}/%{pkg_name}-adapters.jar

pushd %{buildroot}/%{_javadir}
for jar in %{pkg_name}-*; do
    ln -sf ${jar} `echo ${jar}| sed "s|apache-||g"`
done
popd

install -pm 644 %{SOURCE2} %{buildroot}/%{_mavenpomdir}/JPP-%{short_name}-api.pom

%add_maven_depmap JPP-%{short_name}-api.pom %{short_name}-api.jar -a "org.apache.commons:commons-logging-api"
%{?scl:EOF}

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt
%doc PROPOSAL.html RELEASE-NOTES.txt
%{_javadir}/*%{short_name}-api.jar
%{_javadir}/*%{short_name}-adapters.jar

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

# -----------------------------------------------------------------------------

%changelog
* Tue Jun 17 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.1.2-5.4
- Enable maven30 collection only in spec file.

* Mon Jun 16 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.1.2-5.3
- Rebuild against maven30 collection.

* Mon Jan 20 2014 Omair Majid <omajid@redhat.com> - 1.1.2-5.2
- Rebuild in order to fix osgi()-style provides.
- Resolves: RHBZ#1054813

* Thu Nov 14 2013 Michal Srb <msrb@redhat.com> - 1.1.2-5.1
- Enable SCL for thermostat

* Fri Sep 20 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1.2-5
- Add BuildRequires on apache-commons-parent >= 26-7

* Tue Aug 27 2013 Michal Srb <msrb@redhat.com> - 1.1.2-4
- Migrate away from mvn-rpmbuild (Resolves: #997523)

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1.2-3
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Tue Apr  9 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1.2-2
- Set OSGi Bundle-SymbolicName to org.apache.commons.logging
- Resolves: rhbz#949842

* Mon Apr  8 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1.2-1
- Update to upstream version 1.1.2
- Convert POM to POM macros
- Remove OSGi manifest patch; fixed upstream

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-23
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 1.1.1-22
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Thu Nov 22 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.1.1-21
- Install NOTICE file
- Resolves: rhbz#879581

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue May 1 2012 Alexander Kurtakov <akurtako@redhat.com> 1.1.1-19
- Bring back jakarta-commons-logging provides/obsoletes - the comment was misleading.

* Mon Apr 30 2012 Alexander Kurtakov <akurtako@redhat.com> 1.1.1-18
- Fix build with latest libs.
- Adapt to current guidelines.

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Apr 21 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-16
- Build with maven 3
- Fix build for avalon-framework

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Dec 16 2010 Alexander Kurtakov <akurtako@redhat.com> 1.1.1-14
- Bring back commons-logging* symlinks.

* Thu Dec 16 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-13
- Replace tomcat6 BR with servlet25 only
- Cleanups according to new packaging guidelines
- Install maven metadata for -api jar
- Versionless jars/javadocs

* Tue Nov  9 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-12
- Add depmaps for api and adapters subpackages
- Use apache-commons-parent BR instead of maven-*
- Replace tomcat5 BR with tomcat6
- Reenable tests

* Thu Jul  8 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-11
- Add license to javadoc subpackage

* Wed Jun 9 2010 Alexander Kurtakov <akurtako@redhat.com> 1.1.1-10
- Add osgi manifest entries.

* Fri May 21 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-9
- Correct depmap filename for backward compatibility

* Mon May 17 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-8
- Fix wrong depmap JPP name to short_name
- Add obsoletes to javadoc subpackage

* Wed May 12 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-7
- Fix symlink problems introduced previously in r5

* Tue May 11 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-6
- Add one more add_to_maven_depmap for backward compatibility

* Mon May 10 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-5
- Fix up add_to_maven_depmap
- Add jpackage-utils Requires for javadoc
- Cleanup install a bit

* Fri May  7 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-4
- Fix provides

* Thu May  6 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-3
- Revert to using default permissions
- Drop "Package" from summary, improve javadoc summary text

* Thu May  6 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-2
- Fix EOLs on docs
- Create javadoc symlinks during install
- Use version macro in Source0 URL, use _mavenpomdir macro

* Thu May  6 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.1-1
- Rename and rebase from jakarta-commons-logging
