# Changelog

ARENA-py notable changes. Started 2021-19-2.

## [0.1.19] - 2021-2-3
### Added
- `on_msg_callback` receives __all__ messages, including duplicates from other callbacks.
- Object children now have the class variable `object_type` which is the name of the object_type for the class.

### Changed
- Library calls `get_persisted_objs` on connect to cache persisted objects.
- Object instances now all have `clickable` property which checks if the Object is clickable.
- Improved event loop using more advanced asyncio for mqtt client loop and message processing.

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
- Bug fix with turning dictionaries into Material attributes.

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

[0.1.18]: https://github.com/conix-center/ARENA-py/tree/120b675928e7c8f215f3910e4157890944d0b2e8
[0.1.17]: https://github.com/conix-center/ARENA-py/tree/0a7897c89bd4a08c03c0c626601e4686cacc368c
[0.1.16]: https://github.com/conix-center/ARENA-py/tree/8e42dac35a9de7a6b610a1b6663606d1adf1a17e
[0.1.15]: https://github.com/conix-center/ARENA-py/tree/e8182f476ebdb9c2878e16cefea9671a6f5c49f6
[0.1.14]: https://github.com/conix-center/ARENA-py/tree/d4c2d6627f38bd05264dd2a2da3f852648e5ee39
[0.1.13]: https://github.com/conix-center/ARENA-py/tree/589f095dab1f31acd3662b1283af7cded2197b08
[0.1.12]: https://github.com/conix-center/ARENA-py/tree/1c66c37a8fb8c37a15650bc26924ae7a44606903
