# OBLOT Embedded

Libraries and conventions used in electronic devices developed for OBLOT research centre

---

## MAVLink

Generated files can be downloaded from the [Releases page](https://github.com/wut-daas/oblot-embedded/releases)

### C headers

Unpack the zip file and place the include folder in your project include path. Recommended use:

```C
#include "mavlink/oblot/mavlink.h"
```

### Python dialect

To use the dialect place the py file in `site-packages\pymavlink\dialects\v20` of your Python environment. Usage of `venv` is strongly recommended.

Example use:

```Python
from pymavlink.dialects.v20 import oblot

mav = oblot.MAVLink(open('path-to-raw-log-file.bin', 'wb'))
```

[This script](tools/oblot-viewer/download_dialect.py) can be used to download and install the latest module in currently used Python environment.
