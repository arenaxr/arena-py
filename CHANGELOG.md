# Changelog

ARENA-py notable changes. Started 2021-02-19 (version 0.1.12).

## [0.1.46] - 2022-13-20
### Changed
- Fixed some small bugs.

## [0.1.45] - 2022-12-20
### Changed
- Account for `arenaxr.org` as hostname for legacy applications.
- Fixed some small bugs.

## [0.1.44] - 2022-06-06
### Added
- Scale param to `cli_args`.
- Support for `Device` and `Scene` in the same script.
### Changed
- Refactored auth with data encapsulation.
- Fixed several small bugs.

## [0.1.43] - 2021-11-17
### Added
- Device sensor connections: `device=Device(host="arena.org", device="robot1")`.
- More error handling for network configuration issues.

## [0.1.42] - 2021-10-04
### Changed
- Improved auth flow when CWD is Home.
- Check for expired local MQTT token.

### Added
- CLI option for all apps: `Scene(cli-args=True)`.

## [0.1.41] - 2021-09-08
### Changed
- Revert using orjson library.

## [0.1.40] - 2021-08-20
### Changed
- Use orjson library for faster JSON parsing.

## [0.1.39] - 2021-07-28
### Added
- Attribute `jitsi-video`.
- MQTT CLI pub/sub scripts: `arena-py-pub` and `arena-py-sub`.

### Changed
- Remove local objects when receiving `delete` message.
- MQTT CLI auto-generates topic from `object_id` when undefined.

## [0.1.38] - 2021-07-06
### Added
- Auth scripts: `arena-py-signout` and `arena-py-permissions`.
- Ability to request video token.

### Changed
- Improved auto-detect signout when server changes.

## [0.1.37] - 2021-06-23
### Changed
- Google OAuth localhost flow restored.

## [0.1.36] - 2021-06-14
### Changed
- Google OAuth localhost flow removed, replaced with console flow.

## [0.1.35] - 2021-06-08
### Changed
- MQTT broker connection uses encrypted TLS.

## [0.1.34] - 2021-05-18
### Changed
- Remove default color from `Object`s.

## [0.1.33] - 2021-05-18
### Added
- `Object`s start with a default color of `(128,128,128)`.
- Add first draft of ARENA-py CLI (similar to mosquitto_pub/sub)!
Usage: `python3 -m arena -s <scene> -a <pub/sub> ...`
Type `python3 -m arena -h` for options.

### Changed
- Do not accept None for host, realm, scene in `Scene` constructor.

## [0.1.32] - 2021-05-16
### Added
- Programs will now disconnect and exit on an exception.
- Added try except block on message parsing.
- `WindowsSelectorEventLoopPolicy` added for Windows Python >=3.8

## [0.1.31] - 2021-05-10
### Changed
- `add_msg_callback` auto subscribes to topic.
- Possibly fix `Color` bug with invalid colors.

## [0.1.30] - 2021-04-29
### Changed
- Remove top-level landmark type.

### Added
- Replace with new landmark attribute.

## [0.1.29] - 2021-04-29
### Changed
- Auto-detect headless auth from SSH terminal.
- Remove localhost tests from debug flag.
- Color bug fix (blue and green were flipped).

## [0.1.28] - 2021-04-16
### Changed
- Reworked env/local token storage.

## [0.1.27] - 2021-04-15
### Changed
- Better timing on `scene.run_forever`.
- Move MQTT token check to work better on ARTS.

## [0.1.26] - 2021-04-07
### Changed
- Fix additional numpy and scipy version issues.

## [0.1.25] - 2021-04-03
### Changed
- Downgrade numpy and scipy versions.

## [0.1.24] - 2021-03-31
### Changed
- Bug fix with `ThickLine`.

### Added
- Add various example programs for every attribute and object.
- Add `TextInput` attribute and example.

## [0.1.23] - 2021-03-21
### Changed
- Queue all incoming MQTT messages for processing and remove `network_loop_interval`.

### Added
- Add `end_program_callback`, which is called whenever client disconnects.

## [0.1.22] - 2021-03-13
### Changed
- Remove `Color` in `Material` deprecation.
- Fix undeclared variable `password` bug.

## [0.1.21] - 2021-03-07
### Changed
- Async MQTT loop cancellation bug fixes.

## [0.1.20] - 2021-03-07
### Changed
- Event loop bug fixes.

## [0.1.19] - 2021-03-02
### Added
- `on_msg_callback` receives __all__ messages, including duplicates from other callbacks.
- Object children now have the class variable `object_type` which is the name of the object_type for the class.

### Changed
- Library calls `get_persisted_objs` on connect to cache persisted objects.
- Object instances now all have `clickable` property which checks if the Object is clickable.
- Improved event loop using more advanced asyncio for MQTT client loop and message processing.

## [0.1.18] - 2021-03-02
### Added
- Use `scene.get_persisted_objs()` to get all persisted objects in a scene.

### Changed
- Improved message parsing and Object creation whenever a message arrives.
- Callbacks and event handlers now take __three__ arguments (`scene`, `obj`/`evt`, `msg`). `scene` is a reference to the scene.
`obj`/`evt` is an `Object` or `Event` (depending on the callback/handler). `msg` is the raw JSON message if needed by user.

## [0.1.17] - 2021-03-02
### Changed
- Event handler bug fix.

## [0.1.16] - 2021-03-01
### Changed
- Bug fix with turning dictionaries into Material as.

## [0.1.15] - 2021-02-27
### Changed
- Bug fix with get_persisted_obj. Ensures that `persist` is True.

## [0.1.14] - 2021-02-24
### Added
- Allow user defined username and passwords with env vars `ARENA_USERNAME`, `ARENA_PASSWORD`. Need to
specify both to bypass auth.

### Changed
- scene callbacks (`on_msg`, `new_obj`, `delete_obj`, etc.) have an `Object` instance as an argument rather than dict.
- `get_persisted_obj` returns an `Object`.

## [0.1.13] - 2021-02-19
### Added
- Support for scene landmarks with the `scene.add_landmark` method.

### Changed
- Bug fix with `scene.new_obj_callback` which didn't work well with code that updated `scene.users`.

## [0.1.12] - 2021-02-19
### Added
- Support for user callbacks (`user_join_callback`, `user_left_callback`).
- Use these callbacks to handle when a user joins and leaves, respectively.
- `scene.users` will give now you a dictionary of users, mapping `object_id`'s to `Camera` objects.
- Add Changelog.md to keep track of changes.

### Changed
- `Arena` class renamed to `Scene`, but using `Arena` is still allowed. Updated examples to reflect this.
- Tiny bug fix with `update_objects`.
