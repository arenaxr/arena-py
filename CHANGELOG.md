# Changelog

arena-py notable changes. Started 2021-02-19 (version 0.1.12).

## [0.8.0](https://github.com/arenaxr/arena-py/compare/v0.7.0...v0.8.0) (2023-11-01)


### Features

* add grabbing example ([6f3a04a](https://github.com/arenaxr/arena-py/commit/6f3a04ab5f5397e6984b7679c33b99dc9b901ade))
* add grabbing example ([ce9d236](https://github.com/arenaxr/arena-py/commit/ce9d236e0235cc9443aa11da98ac458ec7384bac))


### Bug Fixes

* add dur for anims for delayed_prop task ([fdd09f1](https://github.com/arenaxr/arena-py/commit/fdd09f1ab9bb5953985a9e79818f400fab6a1df8))
* **camera:** publish/read all camera data in data block ([04efd0d](https://github.com/arenaxr/arena-py/commit/04efd0da84df4d820297a91df3a4ffeb06a10620))
* check user in rigs dict before delete ([ea57f0f](https://github.com/arenaxr/arena-py/commit/ea57f0f9d91f873dbd931351790b8956a37d2775))
* **particles:** add support for spe-particles componenet ([005a19b](https://github.com/arenaxr/arena-py/commit/005a19b36c513100f959d47f55e937cb6cc42fb8))
* publish reset rig for new users ([24f1696](https://github.com/arenaxr/arena-py/commit/24f1696810da03f45fd7ffa26fa16dfc08718db1))

## [0.7.0](https://github.com/arenaxr/arena-py/compare/v0.6.0...v0.7.0) (2023-09-05)


### Features

* add support for controllers ([3ee739c](https://github.com/arenaxr/arena-py/commit/3ee739c21fc8123ddb3bed695279d20f27845e19))


### Bug Fixes

* **auth:** add CLI warning for publishing without permmission. Closes [#160](https://github.com/arenaxr/arena-py/issues/160). ([d639609](https://github.com/arenaxr/arena-py/commit/d639609543dd41af373aa9872b5a92716d7892fc))
* **auth:** add test hints for missing browsers ([7187cca](https://github.com/arenaxr/arena-py/commit/7187cca7044d8b22b8309f4496367ba339a4416a))
* **auth:** allow auth flow to print url regardless ([a28d38e](https://github.com/arenaxr/arena-py/commit/a28d38e3059289aa0c8cc76fd405fb53d88ca89c))
* **auth:** improved error messaging when browser undetected ([0f7a4dc](https://github.com/arenaxr/arena-py/commit/0f7a4dc15e4613a46ea5bbbcf115e26002056b6f))
* **auth:** remove deprecated console-only auth flow ([1f4d88f](https://github.com/arenaxr/arena-py/commit/1f4d88f73bbaf88df3bf07185df72952f7ba5569))
* **auth:** resolve errors when saved mqtt token is empty ([d38587f](https://github.com/arenaxr/arena-py/commit/d38587f70a666231d37fdcf474441a981d80a2ee))

## [0.6.0](https://github.com/arenaxr/arena-py/compare/v0.5.7...v0.6.0) (2023-08-31)


### Features

* add initial UI elements ([547fe8d](https://github.com/arenaxr/arena-py/commit/547fe8d84fbfe4c09f4e5b6dd76c90b68afb480b))


### Bug Fixes

* better handle skipped keys in json preprocs ([886e20c](https://github.com/arenaxr/arena-py/commit/886e20cfbca525157b78b1a319d4b26ee2273259))
* calibrator x-axis arrow rotation ([902a64d](https://github.com/arenaxr/arena-py/commit/902a64d5853f0e143ec7ca530db006cb35a92f7e))
* Followup Animations with end state update ([8009a6d](https://github.com/arenaxr/arena-py/commit/8009a6d3077a694bd0d6bf2ede53fb0b16e01077))
* pop delayed_prop_tasks before json_encode ([a4eedcb](https://github.com/arenaxr/arena-py/commit/a4eedcbb0f4a971efc8f92550ccfbcd288bf3896))

## [0.5.7](https://github.com/arenaxr/arena-py/compare/v0.5.6...v0.5.7) (2023-08-03)


### Bug Fixes

* put back default start and end in Line ([5b24a40](https://github.com/arenaxr/arena-py/commit/5b24a40a8342b110421998781caa975b0c983c7e))

## [0.5.6](https://github.com/arenaxr/arena-py/compare/v0.5.5...v0.5.6) (2023-08-03)


### Bug Fixes

* [#142](https://github.com/arenaxr/arena-py/issues/142) ([53d0688](https://github.com/arenaxr/arena-py/commit/53d06887476acb7087f1397055d8b1cd314cbd56))

## [0.5.5](https://github.com/arenaxr/arena-py/compare/v0.5.4...v0.5.5) (2023-08-03)


### Bug Fixes

* color accepts floats, but casts to int; Line start and end implicitly converts to Position ([3684684](https://github.com/arenaxr/arena-py/commit/36846840b5dcc58acb354b57bd94576e37a33393))

## [0.5.4](https://github.com/arenaxr/arena-py/compare/v0.5.3...v0.5.4) (2023-08-01)


### Bug Fixes

* fix github publish action ([74d43ad](https://github.com/arenaxr/arena-py/commit/74d43ad5a5ecfd9db4c8e4236915a8b94122721e))

## [0.5.3](https://github.com/arenaxr/arena-py/compare/v0.5.2...v0.5.3) (2023-08-01)


### Bug Fixes

* fix github publish action ([3927c99](https://github.com/arenaxr/arena-py/commit/3927c9976fb6f82dbd772f6f5090d3d7e9316dc9))

## [0.5.2](https://github.com/arenaxr/arena-py/compare/v0.5.1...v0.5.2) (2023-08-01)


### Bug Fixes

* fix github publish action ([a8b894a](https://github.com/arenaxr/arena-py/commit/a8b894a6b92b1182d6ba5f7feadf764f0fd73e4f))

## [0.5.1](https://github.com/arenaxr/arena-py/compare/v0.5.0...v0.5.1) (2023-08-01)


### Bug Fixes

* add default web_host = arenaxr.org ([aa7ab26](https://github.com/arenaxr/arena-py/commit/aa7ab2619b0a59f4c0a6542ba83a00637d321b15))
* stop pushing to test.pypi.org ([670c33b](https://github.com/arenaxr/arena-py/commit/670c33b65904bc83feed933dac2c02002634656d))
* updated to avoid pypi filename collisions ([bb05487](https://github.com/arenaxr/arena-py/commit/bb0548768c72bc6bce8f3778231e59cb9867b9b9))

## [0.5.0](https://github.com/arenaxr/arena-py/compare/v0.4.5...v0.5.0) (2023-08-01)


### Features

* add interpreter ([237b3ac](https://github.com/arenaxr/arena-py/commit/237b3ac21c85224c95f9d8fcd5fa362f530d5456))
* add interpreter to event loop; improve exit ([f1812f0](https://github.com/arenaxr/arena-py/commit/f1812f05ddc1073a7fb257ddd2ef1f3755a0cf5e))


### Bug Fixes

* datetime serialization ([30d0f45](https://github.com/arenaxr/arena-py/commit/30d0f458e253832e8ddd8da533cb66b9e3f05472))
* get calls; add msg rates ([e592a62](https://github.com/arenaxr/arena-py/commit/e592a6259417c9313931be17af035e3013bb2dc8))
* move interpreter to a thread ([1066565](https://github.com/arenaxr/arena-py/commit/10665656a8efd046ba8fb01c6c8ae6b21f46fca3))
* paho-mqtt update to 1.5.1 still works end_callback ([ff4ec5e](https://github.com/arenaxr/arena-py/commit/ff4ec5e5bae49147d2d1d0b573778c591939ce4d))
* restore end_callback mqtt with paho 1.5.0 ([a32c086](https://github.com/arenaxr/arena-py/commit/a32c0862e58ff6becce3a01f4b849dcbf99ef92f))

## [0.4.5](https://github.com/arenaxr/arena-py/compare/v0.4.2...v0.4.5) (2023-07-05)


### Features

* Reconnect MQTT client after disconnect ([7e2069a](https://github.com/arenaxr/arena-py/commit/7e2069a3513542f86f686390fe1454429d4db342))


### Bug Fixes

* mutable default arg for thickline ([68c5db2](https://github.com/arenaxr/arena-py/commit/68c5db23a5ddd30e47489fd6071de189f1573a15))
* variable typo 'quaternion' ([db8fff8](https://github.com/arenaxr/arena-py/commit/db8fff863985bc229aa82fedc20ff79a620e407f))


### Miscellaneous Chores

* release 0.4.5 ([99b86d7](https://github.com/arenaxr/arena-py/commit/99b86d7619309320fabb452bb5d372241d82971c))

## [0.4.2](https://github.com/arenaxr/arena-py/compare/v0.4.1...v0.4.2) (2023-06-06)

### Bug Fixes

* **calibrate:** merge in user database branch ([#139](https://github.com/arenaxr/arena-py/issues/139)) ([b2d3210](https://github.com/arenaxr/arena-py/commit/b2d3210ecc0836e9a9f211b893ed14a4c519e8af))

* **rotation:** stopped using scipy for euler<->quaternion conversions

## [0.4.1](https://github.com/arenaxr/arena-py/compare/v0.4.0...v0.4.1) (2023-05-26)


### Bug Fixes

* **mqtt:** Users should only define main WEB host, our backend supplies MQTT host ([#137](https://github.com/arenaxr/arena-py/issues/137)) ([4376842](https://github.com/arenaxr/arena-py/commit/43768424c4b48953166967594faee4e747eaff72))

## [0.4.0](https://github.com/arenaxr/arena-py/compare/v0.3.0...v0.4.0) (2023-05-25)


### Features

* add calibrate vr helmet tool ([#133](https://github.com/arenaxr/arena-py/issues/133)) ([0bd1359](https://github.com/arenaxr/arena-py/commit/0bd135904574bb26425a253ed4e67a7c92fa2697))


### Bug Fixes

* add entity primitive ([9531be8](https://github.com/arenaxr/arena-py/commit/9531be849b32938ea694bafe9e8727e5da3268f0))
* **cli:** add debug cmd to cli args ([0206452](https://github.com/arenaxr/arena-py/commit/0206452ba50f8bfcd7b5bf2d0806e89c8d34163a))
* remove all rewriting of hostname ([eabb32d](https://github.com/arenaxr/arena-py/commit/eabb32d237749048294735b36128ebaad510b726))

## [0.3.0](https://github.com/arenaxr/arena-py/compare/v0.2.1...v0.3.0) (2023-04-12)


### Features

* added scene.delete_attributes() to null attribute(s) ([50f8ae6](https://github.com/arenaxr/arena-py/commit/50f8ae6bd2f18556714f95a5bdc924b3ade570a4))
* added VideoControl attribute binding ([9f3bb2b](https://github.com/arenaxr/arena-py/commit/9f3bb2befc771ab9edf092714be1093fd36c9728))


### Bug Fixes

* future-proof more attributes, allowing arbitrary parameters ([c61e551](https://github.com/arenaxr/arena-py/commit/c61e551e7b9700556639fc42d538e4df3db14e8d))

## [0.2.1](https://github.com/arenaxr/arena-py/compare/v0.2.0...v0.2.1) (2023-03-15)


### Bug Fixes

* **mqtt:** use proper UTC timestamp for Zulu ([057e535](https://github.com/arenaxr/arena-py/commit/057e5358e9b11441851b108b4fa7566efa681789))
* remove deleted users from scene.users dict ([d962acd](https://github.com/arenaxr/arena-py/commit/d962acd15a46e13df6b48eb92f6d348c2224ac31))
* **rotation:** fixed euler 2 quat conversion ([41cdc50](https://github.com/arenaxr/arena-py/commit/41cdc5020d2e3dfd27c6935333898d111249222d))


### Documentation

* update a-frame links to 1.4.0 docs ([b3ee05e](https://github.com/arenaxr/arena-py/commit/b3ee05e5a503e0d275937d18a582850c71b80fa6))

## [0.2.0](https://github.com/arenaxr/arena-py/compare/v0.1.46...v0.2.0) (2023-02-02)


### Features

* **mqtt:** always publish quaternions on wire format to avoid persist euler-&gt;quat merges ([4a582d4](https://github.com/arenaxr/arena-py/commit/4a582d4ff8286c91b43594bb1eac24f850e18c00))

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
- Add first draft of arena-py CLI (similar to mosquitto_pub/sub)!
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
