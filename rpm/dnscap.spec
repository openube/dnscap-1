Name:           dnscap
Version:        1.7.1
Release:        1%{?dist}
Summary:        Network capture utility designed specifically for DNS traffic
Group:          Productivity/Networking/DNS/Utilities

License:        BSD-3-Clause
URL:            https://www.dns-oarc.net/tools/dnscap
# Using same naming as to build debs, get the source (and rename it) at
# https://www.dns-oarc.net/tools/dnscap and change %setup
Source0:        %{name}_%{version}.orig.tar.gz

BuildRequires:  libpcap-devel
BuildRequires:  ldns-devel
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool

%description
dnscap is a network capture utility designed specifically for DNS
traffic. It produces binary data in pcap(3) format. This utility
is similar to tcpdump(1), but has a number of features tailored
to DNS transactions and protocol options.


%prep
%setup -q -n %{name}_%{version}


%build
sh autogen.sh
%configure
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root)
%{_bindir}/*
%{_datadir}/doc/*
%{_mandir}/man1/*
%{_libdir}/*


%changelog
* Wed Dec 27 2017 Jerry Lundström <lundstrom.jerry@gmail.com> 1.7.1-1
- Release 1.7.1
  * The library used for parsing DNS (libbind) is unable to parse DNS
    messages when there is padding at the end (the UDP/TCP payload is larger
    then the DNS message). This has been fixed by trying to find the actual
    DNS message size, walking all labels and RR data, and then retry parsing.
  * Other changes and bug-fixes:
    - Fix size when there is a VLAN to match output of `use_layers` yes/no
    - Add test of VLAN matching
    - Fix `hashtbl.c` building in `rssm`
    - Add test with padded DNS message
  * Commits:
    49e5400 Fix #127: If `ns_initparse()` returns `EMSGSIZE`, try and get
            actual size and reparse
    99bda0b Fix #98: VLAN
* Tue Dec 19 2017 Jerry Lundström <lundstrom.jerry@gmail.com> 1.7.0-1
- Release 1.7.0
  * This release adds IP fragmentation handling by using layers in pcap-thread
    which also adds a new flag to output and modules. `DNSCAP_OUTPUT_ISLAYER`
    indicates that `pkt_copy` is equal to `payload` since the layers of the
    traffic have already been parsed. IP fragments are reassembled with the
    `pcap_thread_ext_frag` extension that is included in pcap-thread.
  * New extended (`-o`) options:
    - `use_layers`: Use pcap-thread layers to handle the traffic
    - `defrag_ipv4`: Enabled IPv4 de-fragmentation
    - `defrag_ipv6`: Enabled IPv6 de-fragmentation
    - `max_ipv4_fragments`: Set maximum fragmented IPv4 packets to track
    - `max_ipv4_fragments_per_packet`: Set the maximum IPv4 fragments per
      tracked packet
    - `max_ipv6_fragments`: Set maximum fragmented IPv6 packets to track
    - `max_ipv6_fragments_per_packet`: Set the maximum IPv6 fragments per
      tracked packet
  * Currently `-w` does not work with `use_layers` and the plugins `pcapdump`
    and `royparse` will discard output with the flag `DNSCAP_OUTPUT_ISLAYER`
    because they need access to the original packet.
  * The `rzkeychange` plugin now encodes certain flag bits in the data that
    it reports for RFC8145 key tag signaling. The flags of interest are:
    `DO`, `CD`, and `RD`. These are encoded in an bit-mask as a hexadecimal
    value before the `_ta` component of the query name.
  * Other changes and bug-fixes:
    - Fix #115: document `-g` output, see `OUTPUT FORMATS` `diagnostic` in
      `dnscap(1)` man-page
    - Add test to match output from non-layers runs with those using layers
    - Add test with fragmented DNS queries
    - Fix #120: CBOR/CDS compiles again, update tinycbor to v0.4.2
    - Fix `ip->ip_len` byte order
    - Fix parsing of IP packets with padding or missing parts of payload
  * Commits:
    0347f74 Add AUTHORS section in man-page
    ef1b68c Fix CID 1463073
    8a79f89 Layers
    a404d08 Update pcap-thread to v3.1.0, add test for padding fixes
    08402f1 Fix byte order bug.  ip->ip_len must be evaluated with ntohs().
    d6d2340 CBOR/CDS and formatting
    85ec2d8 Fix #87: IP fragmentation reassembly
    22bfd4a Documentation
    c35f19f Adding flag bits to rzkeychange RFC8145 key tag signaling data.
            This may be useful to find "false" key tag signals from sources
            that don't actually perform DNSSEC validation.
* Fri Dec 01 2017 Jerry Lundström <lundstrom.jerry@gmail.com> 1.6.0-1
- Release 1.6.0
  * New additions to the plugins:
    - `rzkeychange` can now collect RFC8145 key tag signaling. Signals are
      saved during the collection interval, and then sent to the specified
      `-k <zone>`, one at a time, at the end of the interval. Only root zone
      signals are collected. Added by Duane Wessels (@wessels).
    - `royparse` is a new plugin to splits a PCAP into two streams, queries
      in PCAP format and responses in ASCII format. Created by Roy Arends
      (@RoyArends).
    - `txtout` new option `-s` for short output, only print QTYPE and QNAME
      for IN records. Added by Paul Hoffman (@paulehoffman)
    - The extension interface has been extended with `DNSCAP_EXT_IA_STR` to
      export the `ia_str()` function.
  * Bugfixes and other changes:
    - Remove duplicated hashtbl code
    - `rssm`: fix bug where count in table was taken out as `uint16_t` but
      was a `uint64_t`
    - Handle return values from hashtbl functions
    - `txtout`: removed unused `-f` options
    - Change `ia_str()` to use buffers with correct sizes, thanks to
      @RoyArends for spotting this!
  * Commits:
    3f78a31 Add copy/author text
    1bd914d Fix CID 1462343, 1462344, 1462345
    f9bb955 Fix `fprintf()` format for message size
    abedf84 Fix #105: `inet_ntop` buffers
    bfdcd0d Addresses the suggestions from Jerry.
    dda0996 royparse :)
    4f6520a royparse plugin finished
    f1aa4f2 Fix #103: Remove `opt_f`
    32355b7 Rearrange code to keep the change smaller and fix indentation
    d6612c1 Added -s to txtout for short output
    9d8d1ef Check return of `snprintf()`
    55f5aba Format code
    9f19ec3 Fixed memory leak in rzkeychange_keytagsignal()
    58b8784 Fix memory leaks and better return value checks in
            rzkeychange_submit_counts()
    b06659f Add server and node to keytag signal query name
    705a866 Always free response packets in rzkeychange plugin.
    e802843 Implement RFC8145 key tag signal collection in rzkeychange plugin
    5fbf6d0 Added extension for ia_str() so it can be used by rzkeychange
            plugin.
    3be8b8f Split `dnscap.c` into more files
    e431d14 Fix #92: hashtbl
* Mon Aug 21 2017 Jerry Lundström <lundstrom.jerry@gmail.com> 1.5.1-1
- Release 1.5.1
  * Compatibility fixes for FreeBSD 11.1+ which is now packing `struct ip`
    and for OpenBSD.
  * Commits:
    17e3c92 FreeBSD is packing `struct ip`, need to `memcpy()`
    f8add66 Code formatting
    38cd585 Add documentation about libbind
    d1dd55b Fix #82: Update dependencies for OpenBSD
* Tue Jun 06 2017 Jerry Lundström <lundstrom.jerry@gmail.com> 1.5.0-1
- Release 1.5.0
  * Added support for writing gzipped PCAP if the `-W` suffix ends with
    `.gz` and made `-X` work without `-x`. New inteface for plugins to
    tell them what extensions are available and a new plugin `rzkeychange`.
  * Plugin extensions:
    - Call `plugin_extension(ext, arg)` to tell plugin what extensions exists
    - Add extension for checking responder (`is_responder()`)
  * The rzkeychange plugin was developed by Duane Wessels 2016 in support
    of the root zone ZSK size increase. It is also being used in support of
    the 2017 root KSK rollover and collects the following measurements:
    - total number of responses sent
    - number of responses with TC bit set
    - number of responses over TCP
    - number of DNSKEY responses
    - number of ICMP_UNREACH_NEEDFRAG messages received
    - number of ICMP_TIMXCEED_INTRANS messages received
    - number of ICMP_TIMXCEED_REASS messages received
  * Other fixes (author Duane Wessels):
    - 232cbd0: Correct comment description for meaning of IPPROTO_AH
    - 181eaa4: Add #include <sys/time.h> for struct timeval on NetBSD
  * Commits:
    1d894e2 Make -x and -X work correctly together and update man-page
    34bc54c Make the -X option work without requiring a -x option.
    f43222e Fix CID 1440488, 1440489, 1440490
    aa54395 Update pcap-thread to v2.1.3
    81174ce Prepare SPEC for OSB/COPR
    21d7468 New plugin rzkeychange and plugin extensions
    38491a3 Config header is generated by autotools
    419a8ab Small tweaks and fixes for gzip support
    1967abc updated for earlier BSD versions
    f135c90 added auto gzip if the -W suffix ends with .gz
  * Commits during development of rzkeychange (author Duane Wessels):
    - 620828d: Add rzkeychange -z option to specify resolver IP addresses
    - 1f77987: Add -p and -t options to rzkeychange plugin to configure an
      alternate port and TCP. Useful for ssh tunnels.
    - 2a571f1: Split ICMP time exceeded counter into two counters for time
      exceeded due to TTL and another due to fragmentation
    - e4ee2d3: The rzkeychange data collection plugin uses
      `DNSCAP_EXT_IS_RESPONDER` extension to know if an IP address is a
      "responder" or not, because when dnscap is instructed to collect ICMP
      with -I, it processes all ICMP packets, not just those limited to
      responders (or initiators).
    - cee16b8: Add ICMP Time Exceeded to counters
    - ad8a227: Counting source IPs has performance impacts. #ifdef'd out for
      now add ICMP "frag needed" counts
    - c25e72b: Implemented DNS queries with ldns. First there will be some
      test queries to ensure the zone is reachable and configured to receive
      data. Then a query naming the fields, followed by the periodic queries
      delivering counts.
    - fd23be7: Make report zone, server, node command line argumements mandatory
    - 137789b: Adding rzkeychange plugin files
* Wed Mar 29 2017 Jerry Lundström <lundstrom.jerry@gmail.com> 1.4.1-1
- Release 1.4.1
  * Fixed an issue that when compiled with libpcap that had a specific
    feature enabled it would result in a runtime error which could not be
    worked around.
  * Also fixed various compatibility issues and updated dependency
    documentation for CentOS.
  * Commits:
    785d4c4 Fix compiler warnings
    2d4df8d Fix #65: Update pcap-thread to v2.1.2
    26d3fbc Fix #64: Add missing dependency
    55e6741 Update pcap-thread to v2.1.1, fix issue with libpcap timestamp
            type
    c6fdb7a Fix typo and remove unused variables
* Mon Feb 27 2017 Jerry Lundström <lundstrom.jerry@gmail.com> 1.4.0-1
- Release 1.4.0
  * Until it can be confirmed that the threaded code works as well as the
    non-threaded code it has been made optional and requires a configuration
    option to enable it during compilation.
  * New extended option:
    - `-o pcap_buffer_size=<bytes>` can be used to increase the capture
      buffer within pcap-thread/libpcap, this can help mitigate dropped
      packets by the kernel during breaks (like when closing dump file).
  * Commits:
    1c6fbb2 Update copyright year
    63ef665 Suppress OpenBSD warnings about symbols
    2c99946 pcap-thread v2.0.0, disable threads, errors handling
    4cade97 Fix #56: Update pcap-thread to v1.2.2 and add test
* Fri Dec 23 2016 Jerry Lundström <lundstrom.jerry@gmail.com> 1.3.0-1
- Release 1.3.0
  * Rare lockup has been fixed that could happen if a signal was received
    in the wrong thread at the wrong time due to `pcap_thread_stop()`
    canceling and waiting on threads to join again. The handling of signals
    have been improved for threaded and non-threaded operations.
  * New features:
    - Experimental CBOR DNS Stream format output, see `CBOR_DNS_STREAM.md`
    - Extended options to specify user and group to use when dropping
      privileges, see EXTENDED OPTIONS in man-page
  * Commits:
    a5fa14e Signal and threads
    3868104 Use old style C comments
    7946be5 Clarify building
    d5463b4 RPM spec and various automake fixes
    df206bf Resource data indexing and documentation
    0e2d0fe Fix #22, fix #43: Update README
    5921d73 Add stream option RLABELS and RLABEL_MIN_SIZE
    6dd6ec1 Implement experimental CBOR DNS Stream Format
    4baf695 Fix #37: Extended options to specifty user/group to use when
            dropping privileges
    61d830a Fix #35: Use `AC_HEADER_TIME` and fix warning
* Thu Dec 15 2016 Jerry Lundström <lundstrom.jerry@gmail.com> 1.2.0-1
- Initial package
