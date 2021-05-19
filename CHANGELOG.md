# Changelog

ARENA-py notable changes. Started 2021-19-2 (version 0.1.12).

## [0.1.33] - 2021-18-5
### Changed
- Do not accept None for host, realm, scene in `Scene` constructor.

## [0.1.32] - 2021-16-5
### Added
- Programs will now disconnect and exit on an exception.
- Added try except block on message parsing.
- `WindowsSelectorEventLoopPolicy` added for Windows Python >=3.8

## [0.1.31] - 2021-10-5
### Changed
- `add_msg_callback` auto subscribes to topic.
- Possibly fix `Color` bug with invalid colors.

## [0.1.30] - 2021-29-4
### Changed
- Remove top-level landmark type.

### Added
- Replace with new landmark attribute.

## [0.1.29] - 2021-29-4
### Changed
- Auto-detect headless auth from SSH terminal.
- Remove localhost tests from debug flag.
- Color bug fix (blue and green were flipped).

## [0.1.28] - 2021-16-4
### Changed
- Reworked env/local token storage.

## [0.1.27] - 2021-15-4
### Changed
- Better timing on `scene.run_forever`.
- Move MQTT token check to work better on ARTS.

## [0.1.26] - 2021-7-4
### Changed
- Fix additional numpy and scipy version issues.

## [0.1.25] - 2021-3-4
### Changed
- Downgrade numpy and scipy versions.

## [0.1.24] - 2021-31-3
### Changed
- Bug fix with `ThickLine`.

### Added
- Add various example programs for every attribute and object.
- Add `TextInput` attribute and example.

## [0.1.23] - 2021-21-3
### Changed
- Queue all incoming MQTT messages for processing and remove `network_loop_interval`.

### Added
- Add `end_program_callback`, which is called whenever client disconnects.

## [0.1.22] - 2021-13-3
### Changed
- Remove `Color` in `Material` deprecation.
- Fix undeclared variable `password` bug.

## [0.1.21] - 2021-7-3
### Changed
- Async MQTT loop cancellation bug fixes.

## [0.1.20] - 2021-7-3
### Changed
- Event loop bug fixes.

## [0.1.19] - 2021-2-3
### Added
- `on_msg_callback` receives __all__ messages, including duplicates from other callbacks.
- Object children now have the class variable `object_type` which is the name of the object_type for the class.

### Changed
- Library calls `get_persisted_objs` on connect to cache persisted objects.
- Object instances now all have `clickable` property which checks if the Object is clickable.
- Improved event loop using more advanced asyncio for MQTT client loop and message processing.

## [0.1.18] - 2021-2-3
### Added
- Use `scene.get_persisted_objs()` to get all persisted objects in a scene.

### Changed
- Improved message parsing and Object creation whenever a message arrives.
- Callbacks and event handlers now take __three__ arguments (`scene`, `obj`/`evt`, `msg`). `scene` is a reference to the scene.
`obj`/`evt` is an `Object` or `Event` (depending on the callback/handler). `msg` is the raw JSON message if needed by user.

## [0.1.17] - 2021-2-3
### Changed
- Event handler bug fix.

## [0.1.16] - 2021-1-3
### Changed
- Bug fix with turning dictionaries into Material as.

## [0.1.15] - 2021-27-2
### Changed
- Bug fix with get_persisted_obj. Ensures that `persist` is True.

## [0.1.14] - 2021-24-2
### Added
- Allow user defined username and passwords with env vars `ARENA_USERNAME`, `ARENA_PASSWORD`. Need to
specify both to bypass auth.

### Changed
- scene callbacks (`on_msg`, `new_obj`, `delete_obj`, etc.) have an `Object` instance as an argument rather than dict.
- `get_persisted_obj` returns an Object.

## [0.1.13] - 2021-19-2
### Added
- Support for scene landmarks with the `scene.add_landmark` method.

### Changed
- Bug fix with `scene.new_obj_callback` which didn't work well with code that updated `scene.users`.

## [0.1.12] - 2021-19-2
### Added
- Support for user callbacks (`user_join_callback`, `user_left_callback`).
- Use these callbacks to handle when a user joins and leaves, respectively.
- `scene.users` will give now you a dictionary of users, mapping `object_id`'s to `Camera` objects.
- Add Changelog.md to keep track of changes.

### Changed
- `Arena` class renamed to `Scene`, but using `Arena` is still allowed. Updated examples to reflect this.
- Tiny bug fix with `update_objects`.

[0.1.31]: https://github.com/conix-center/ARENA-py/tree/724e14f4e37112b96d90e94d9e521800bdea0997
[0.1.30]: https://github.com/conix-center/ARENA-py/tree/625355e515539a7fb40e17f6b0668a2488176d4d
[0.1.29]: https://github.com/conix-center/ARENA-py/tree/bd364bec29109c8dd12cce35e612df50f8cfb9e0
[0.1.28]: https://github.com/conix-center/ARENA-py/tree/5b9273747f68f538d6130427da877541daa02d32
[0.1.27]: https://github.com/conix-center/ARENA-py/tree/5e5150dd8e723915abbaaec68183a16a00cef852
[0.1.26]: https://github.com/conix-center/ARENA-py/tree/be42141a15c62f14312cc51e6c3813e990aedce1
[0.1.25]: https://github.com/conix-center/ARENA-py/tree/f12c50e990dd645875be3ae31be5840feb8a98aa
[0.1.24]: https://github.com/conix-center/ARENA-py/tree/619be18bd16178fc40b9e670c313f578789845ea
[0.1.23]: https://github.com/conix-center/ARENA-py/tree/53c0ac608db99d8df0c0ad775cdc4f67df55558b
[0.1.23]: https://github.com/conix-center/ARENA-py/tree/53c0ac608db99d8df0c0ad775cdc4f67df55558b
[0.1.22]: https://github.com/conix-center/ARENA-py/tree/ed54a9d33b0be93d6cc51ed2db7cd5de0248735d
[0.1.21]: https://github.com/conix-center/ARENA-py/tree/c5e561285ddd6135aa03974ab8b686ba74299520
[0.1.20]: https://github.com/conix-center/ARENA-py/tree/a8a2d11ea6718740e0fdaf299d1297ebd37c632f
[0.1.19]: https://github.com/conix-center/ARENA-py/tree/985111ab1e146c95b177338141760fafc909c1a0
[0.1.18]: https://github.com/conix-center/ARENA-py/tree/120b675928e7c8f215f3910e4157890944d0b2e8
[0.1.17]: https://github.com/conix-center/ARENA-py/tree/0a7897c89bd4a08c03c0c626601e4686cacc368c
[0.1.16]: https://github.com/conix-center/ARENA-py/tree/8e42dac35a9de7a6b610a1b6663606d1adf1a17e
[0.1.15]: https://github.com/conix-center/ARENA-py/tree/e8182f476ebdb9c2878e16cefea9671a6f5c49f6
[0.1.14]: https://github.com/conix-center/ARENA-py/tree/d4c2d6627f38bd05264dd2a2da3f852648e5ee39
[0.1.13]: https://github.com/conix-center/ARENA-py/tree/589f095dab1f31acd3662b1283af7cded2197b08
[0.1.12]: https://github.com/conix-center/ARENA-py/tree/1c66c37a8fb8c37a15650bc26924ae7a44606903
