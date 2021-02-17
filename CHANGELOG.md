# CHANGELOG

Use semantic versioning, follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## Unreleased
### Added
- Assign component ids from private user range
- Parsing message definitions from a binary DataFlash log

## [v1.2.0] - 2021-01-22
### Added
- DataFlash messages `ERR`, `MAVC`
- Documentation comments for Ardupilot messages
- Type hints and Numpy style docstring for all methods in Dataflash
- Script for creating Kaitai Struct definition

### Changed
- Released version names starting with a `v`
- Migrated repository to Github
- Automatic download of releases from Github, no API key required
- Assign consecutive DataFlash message ids
- Using `float` instead of `double` in demo script

### Removed
- Automatic releasing through Gitlab CI

### Fixed
- Handling of unitless DataFlash messages by `write_header`

## [1.1.3] - 2020-11-06
*Reuploaded manually after migration from Gitlab*

### Added
- Automatic script to download and install the custom dialect
- Debugging messages from `common.xml`, including `STATUSTEXT`

### Changed
- Renamed the python dialect module to `oblot` from `archer` to match auto-built Releases

## 1.1.2 - 2020-11-01
### Added
- Messages to control and monitor motors on a dyno

### Changed
- `OBLOT_DYNO_FORCE` also has timestamp and sensor id

## 1.1.0 - 2020-10-25
### Added
- CI setup for automated MAVLink generation
- `pymavlink` dialect for Python
- Zipped include folders for C
- Message and command to handle dynamometric station

[v1.2.0]: https://github.com/wut-daas/oblot-embedded/releases/tag/v1.2.0
[1.1.3]: https://github.com/wut-daas/oblot-embedded/releases/tag/1.1.3
