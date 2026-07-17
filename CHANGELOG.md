# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- A `CONNECTION_HEADERS` setting was added that allows you to specify custom
headers that will be sent with every request from a connection. This setting
accepts a mapping of header names to `connection.header.Header` objects which
can retrieve values from get params, cookies etc.
- The `X-Real-IP` header of the connection is now forwarded to the backend by
default. Without it the backend attributes every request to the host High
Templar dials it from, rather than to the client that opened the websocket.
- An `API_SOCKET` setting was added that makes requests to the backend go over
the given unix socket rather than over TCP. This is for deployments where the
backend is otherwise only reachable back through a proxy, which overwrites
`X-Real-IP` with the address of the machine dialling it. `API_URL` is still
required, and must be an `http://` url: the socket does not speak TLS, the path
prefix is still prepended to every request, and the host, while it no longer
decides where the connection goes, is still sent as the `Host` header and so
must be one the backend accepts.

### Removed
- The `FORWARD_IP` setting has been removed. It read the value of the given key
from the WSGI request environment and sent it on as `X-Forwarded-For`. The
request environment has not existed since the rewrite to Quart, which dropped
the code that read the setting but left the setting itself in place, so it has
had no effect since. `X-Real-IP` is now forwarded by default instead; note that
this is a different header, chosen because a proxy overwrites it rather than
appending to it, and so it cannot be set by the client.

### Fixed
- The message consumer queue is now declared `exclusive` instead of
`auto_delete`. RabbitMQ 4 refuses to declare a transient non-exclusive queue,
which stopped the consumer before it bound to the exchange, so no triggered
messages were delivered. The queue is private to a single consumer, so
`exclusive` is the correct declaration and also works on RabbitMQ 3. The test
suite pins RabbitMQ 3.13, matching the version our projects run, but the
consumer now works on both 3 and 4.

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

