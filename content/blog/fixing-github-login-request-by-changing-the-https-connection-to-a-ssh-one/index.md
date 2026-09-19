+++
title = "Fixing github login request by changing the HTTPS connection to a SSH one"
description = "If you have old repositories from github on your computer and try to push to them, you might see a login page asking for your password and…"
date = 2023-02-09T09:07:47.072Z
tags = ["git", "github", "tip", "tips-and-tri"]
medium = "https://medium.com/@jadi/fixing-github-login-request-by-changing-the-https-connection-to-a-ssh-one-f4a2380cc050"
+++

If you have old repositories from github on your computer and try to push to them, you might see a login page asking for your password and even if you provide it, you will get an error that logging in with error is disabled.

To resolve this, you have to 1) get a token and use that or 2) change your https connections to SSH ones if you already have your keys on github.

I’m going to show you how the 2nd method works just as a note to myself.

first check the remote URLs:

`$ git remote -v
origin [https://github.com/jadijadi/repo_name.git](https://github.com/jadijadi/sms_serial_verification.git) (fetch)
origin [https://github.com/jadijadi/repo_name.git](https://github.com/jadijadi/sms_serial_verification.git) (push)`

now its enough to change this url to the SSH one:

`$ git remote set-url origin [git@github.com](mailto:git@github.com):jadijadi/repo_name.git
$ git remote -v
origin [git@github.com](mailto:git@github.com):jadijadi/repo_name.git (fetch)
origin [git@github.com](mailto:git@github.com):jadijadi/repo_name.git (push)`

easy and straightforward.

Note: this is a note-to-self. You need to have your SSH keys working on github for this method to work

---
*Originally published on [Medium](https://medium.com/@jadi/fixing-github-login-request-by-changing-the-https-connection-to-a-ssh-one-f4a2380cc050).*
