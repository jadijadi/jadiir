+++
title = "How Traceroute works — internally"
description = "Ever wondered how traceroute actually figures out every router between you and a website? In this video, we dive deep into what’s really…"
date = 2025-11-20T03:34:33.178Z
tags = ["devops", "linux", "network"]
medium = "https://medium.com/@jadi/how-traceroute-works-internally-0cc9eaeadd64"
+++

Ever wondered how traceroute actually figures out every router between you and a website? In this video, we dive deep into what’s really happening under the hood — the TTL tricks, the ICMP time-exceeded replies, and how your computer basically forces the internet to reveal every hop along the way. I’ll walk through real packets, show you why traceroute sends three probes per hop, and explain how it magically prints hostnames even though you rarely see reverse-DNS traffic in the capture. If you’ve ever used traceroute for debugging, learning networking, or just satisfying your curiosity, this breakdown will make the command finally “click.” Perfect for anyone into networking, hacking, sysadmin work, or just internet nerdery in general.

{{< youtube _kppVskiDTE >}}

---
*Originally published on [Medium](https://medium.com/@jadi/how-traceroute-works-internally-0cc9eaeadd64).*
