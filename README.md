# OBLOT Embedded

Libraries and conventions used in electronic devices developed for OBLOT research centre

[![pipeline status](https://gitlab.com/wut-daas/oblot-embedded/badges/master/pipeline.svg)](https://gitlab.com/wut-daas/oblot-embedded/commits/master)

---

## MAVLink

Generated files can be downloaded from the [Releases page](https://gitlab.com/wut-daas/oblot-embedded/-/releases)

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

After [creating a Gitlab access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#creating-a-personal-access-token) with `read_api` scope, [this script](tools/oblot-viewer/download_dialect.py) can be used to download and install the latest module.
