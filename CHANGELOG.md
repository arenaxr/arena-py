# Changelog

ARENA-py notable changes. Started 2021-19-2.

## [0.1.14] - 2021-24-2
### Added
- Allow user defined username and passwords with env vars ARENA_USERNAME, ARENA_PASSWORD. Need to
specify both to bypass auth.
- scene callbacks (on_msg, new_obj, delete_obj, etc.) have an Object instance as an argument rather than dict.
- get_persisted_obj returns an Object.

## [0.1.13] - 2021-19-2
### Added
- Support for scene landmarks with the `scene.add_landmark` method.

### Changed
- Bug fix with `scene.new_obj_callback` which didn't work well with code that updated `scene.users`.

## [0.1.12] - 2021-19-2
### Added
- Support for user callbacks (`user_join_callback`, `user_left_callback`).
- Use these callbacks to handle when a user joins and leaves, respectively.
- `scene.users` will give now you a dictionary of users, mapping object_ids to `Camera` objects.
- Add Changelog.md to keep track of changes.

### Changed
- `Arena` class renamed to `Scene`, but using `Arena` is still allowed. Updated examples to reflect this.
- Tiny bug fix with `update_objects`.

[0.1.13]: https://github.com/conix-center/ARENA-py/tree/589f095dab1f31acd3662b1283af7cded2197b08
[0.1.12]: https://github.com/conix-center/ARENA-py/tree/1c66c37a8fb8c37a15650bc26924ae7a44606903
