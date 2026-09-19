+++
title = "Change the owner of the last git commit"
description = "It happens! You are working for your company and cloned a repository and commiting something.. but you have commited using your global…"
date = 2023-07-11T08:36:07.871Z
tags = ["commit", "git", "identity", "note-to-self", "tips"]
medium = "https://medium.com/@jadi/change-the-owner-of-the-last-git-commit-6a04e5c1e705"
+++

It happens! You are working for your company and cloned a repository and commiting something.. but you have commited using your global identity. The solution is simple, using this command you can change the name and the email of the last commit:

```
git commi --amend --author="Jadi <jadijadi@gmail.com>"
```

As a side note, you can change your username and email which is used in git commits for a specific git repository via these commands WHEN you are in that git repositories directory:

```
git config user.name "Jadi"
git config user.email "jadijadi@gmail.com"
```

Or if you want to do it globally this is the way:

```
git config - global user.name "Jadi"
git config - global user.email "jadijadi@gmail.com"
```

---
*Originally published on [Medium](https://medium.com/@jadi/change-the-owner-of-the-last-git-commit-6a04e5c1e705).*
