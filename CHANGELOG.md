# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.5.0] - 2019-10-02
### Added
- `Hub` objects now have the method `on_ping` that allows you to hook custom
behavior for when a connection receives a ping message from the client. This
hook will receive the connection as only argument.

## [2.4.2] - 2019-09-30
### Fixed
- Readded accidentally deleted functionality (`connection.api`,
`hub.on_connect`, `hub.on_disconnect`)

## [2.4.1] - 2019-09-27
### Fixed
- Fix one slow connection slowing down the entire system.

## [2.4.0] - 2019-09-26
### Fixed
- Make `pong` messages send as raw text again instead of JSON.
- Do not double JSON encode messages.
- Do not crash on dead websocket connection.

## [2.3.0] - 2019-09-24
### Added
- A `FORWARD_IP` setting was added that allows you to specify which key from
the request environment should be used to set the `X-Forwarded-For` header so
that the requests made appear to come from the original user's IP. By default
this setting defaults to `None` which disables automatically filling the
`X-Forwarded-For` header altogether.
### Fixed
- A lock was added per connection for writing to the socket to fix an issue
where concurrent writes would cause issues.

## [2.2.0] - 2019-04-09
### Added
- `Connection` objects now have an `api` attribute that can be used as an
easy way to interface with the connected Binder API. This handles things like
cookies, CSRF, and Auth tokens for you.
- `Hub` objects now have the methods `on_connect` and `on_disconnect` that
allow you to hook custom behavior for when a connection respectively connects
or disconnects. This hook will receive the connection as only argument.
- A `USER_ID_PATH` setting was added that allows you to specify which keys
should be followed to find the user id from the bootstrap response. This
setting defaults to `['user', 'id']` which is compatible with how it used to
work.

## [2.1.2] - 2018-09-14
No changelog was kept up until this version.

[Unreleased]: https://github.com/CodeYellowBV/high-templar/compare/2.5.0...HEAD
[2.5.0]: https://github.com/CodeYellowBV/high-templar/compare/2.4.2...2.5.0
[2.4.2]: https://github.com/CodeYellowBV/high-templar/compare/2.4.1...2.4.2
[2.4.1]: https://github.com/CodeYellowBV/high-templar/compare/2.4.0...2.4.1
[2.4.0]: https://github.com/CodeYellowBV/high-templar/compare/2.3.0...2.4.0
[2.3.0]: https://github.com/CodeYellowBV/high-templar/compare/2.2.0...2.3.0
[2.2.0]: https://github.com/CodeYellowBV/high-templar/compare/2.1.2...2.2.0
[2.1.2]: https://github.com/CodeYellowBV/high-templar/releases/tag/2.1.2

