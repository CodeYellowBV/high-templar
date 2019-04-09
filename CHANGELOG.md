# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
