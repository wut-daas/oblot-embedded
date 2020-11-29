# CHANGELOG

Use semantic versioning, follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## Unreleased
### Added
- DataFlash messages `ERR`, `MAVC`
- Documentation comments for Ardupilot messages

### Changed
- Assign consecutive DataFlash message ids
- Using `float` instead of `double` in demo script

## [1.1.3] - 2020-11-06
### Added
- Automatic script to download and install the custom dialect
- Debugging messages from `common.xml`, including `STATUSTEXT`

### Changed
- Renamed the python dialect module to `oblot` from `archer` to match auto-built Releases

## [1.1.2] - 2020-11-01
### Added
- Messages to control and monitor motors on a dyno

### Changed
- `OBLOT_DYNO_FORCE` also has timestamp and sensor id

## [1.1.0] - 2020-10-25
### Added
- CI setup for automated MAVLink generation
- `pymavlink` dialect for Python
- Zipped include folders for C
- Message and command to handle dynamometric station

[1.1.3]: https://gitlab.com/wut-daas/oblot-embedded/-/releases/1.1.3
[1.1.2]: https://gitlab.com/wut-daas/oblot-embedded/-/releases/1.1.2
[1.1.0]: https://gitlab.com/wut-daas/oblot-embedded/-/releases/1.1.0
