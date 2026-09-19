+++
title = "Find the memory consumption of a Python Object"
description = "Here is the snippet I use. Its not perfect but does the job."
date = 2024-10-24T06:55:36.244Z
tags = ["programming", "python", "snippet"]
medium = "https://medium.com/@jadi/find-the-memory-consumption-of-a-python-object-69a803b144a8"
+++

Here is the snippet I use. Its not perfect but does the job.

```
import sys
from types import ModuleType, FunctionType
from gc import get_referents

# Custom objects know their class.
# Function objects seem to know way too much, including modules.
# Exclude modules as well.
BLACKLIST = type, ModuleType, FunctionType

def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size
```

---
*Originally published on [Medium](https://medium.com/@jadi/find-the-memory-consumption-of-a-python-object-69a803b144a8).*
