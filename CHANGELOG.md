# Changelog

arena-py notable changes. Started 2021-02-19 (version 0.1.12).

### Features

## [0.11.1](https://github.com/arenaxr/arena-py/compare/v0.11.0...v0.11.1) (2024-09-23)


### Bug Fixes

* **auth:** fix failed auth when switching browser vs headless ([2d22acb](https://github.com/arenaxr/arena-py/commit/2d22acb06d70b619b37be72ee0c834ae4fe0df67))
* **docstring:** add falsy default values to docstring params ([9d831d8](https://github.com/arenaxr/arena-py/commit/9d831d8cc4f84056b6c37adfb630641a175a596f))

## [0.11.0](https://github.com/arenaxr/arena-py/compare/v0.10.3...v0.11.0) (2024-09-20)


### Features

* **auth:** add google limited input device auth flow ([#195](https://github.com/arenaxr/arena-py/issues/195)) ([7e2bfef](https://github.com/arenaxr/arena-py/commit/7e2bfef8e7bad45d0b9754d7998ab82235ca8860))


### Bug Fixes

* **auth:** fixed signout not removing gauth token ([7d15b3f](https://github.com/arenaxr/arena-py/commit/7d15b3f7e48e6e0538c2488941b984005d182d43))

## [0.10.3](https://github.com/arenaxr/arena-py/compare/v0.10.2...v0.10.3) (2024-09-03)


### Bug Fixes

* typo len check of rot input ([e0af8c5](https://github.com/arenaxr/arena-py/commit/e0af8c56ee0029aba865496ccc1eb24f8eb6d133))

## [0.10.2](https://github.com/arenaxr/arena-py/compare/v0.10.1...v0.10.2) (2024-08-13)


### Bug Fixes

* bump requests dependancy ([e3b8a04](https://github.com/arenaxr/arena-py/commit/e3b8a048356de5256d97e4427bac81c8aa386948))

## [0.10.1](https://github.com/arenaxr/arena-py/compare/v0.10.0...v0.10.1) (2024-08-09)


### Bug Fixes

* add exit() when disconnected ([28944e2](https://github.com/arenaxr/arena-py/commit/28944e28fce168860137e531221a214282fc8761))
* **auth:** log additional error messages during http errors ([bce90b7](https://github.com/arenaxr/arena-py/commit/bce90b7bce28d9694c55839620593b3fb07cdfa8))
* **auth:** remove automatic browser open for 4xx status ([937a867](https://github.com/arenaxr/arena-py/commit/937a867b95c5ac3544148d4728dbcee068ef905e))
* better error handling on malformed tokens ([0dd7a62](https://github.com/arenaxr/arena-py/commit/0dd7a620c93d4e677f9ddc379237df830762e75e))
* **obj-model:** sync with latest schema, add ObjModel ([646baea](https://github.com/arenaxr/arena-py/commit/646baeab5e0bfa89d7ac183e64cc977ef2918087))
* print error msgs on exit ([2200159](https://github.com/arenaxr/arena-py/commit/220015928c71e1172e0b3022f385844bc3188537))
* replace program object from persist ([ca9b71a](https://github.com/arenaxr/arena-py/commit/ca9b71ac7623d537ff8d7d1f4836896fffe04ed5))

## [0.10.0](https://github.com/arenaxr/arena-py/compare/v0.9.6...v0.10.0) (2024-05-06)


### Features

* **urdf:** add urdf model support ([04ebf90](https://github.com/arenaxr/arena-py/commit/04ebf904171399bc2ea638d5058f2015fb6545e0))


### Documentation

* update schema docstrings to latest version ([b792bf2](https://github.com/arenaxr/arena-py/commit/b792bf20c0d0b69178a1d458da817681015ea899))

## [0.9.6](https://github.com/arenaxr/arena-py/compare/v0.9.5...v0.9.6) (2024-04-08)


### Bug Fixes

* bump version from removing pypi tests ([1aa1c88](https://github.com/arenaxr/arena-py/commit/1aa1c8874025769067bdc672268acc9f532c7070))

## [0.9.5](https://github.com/arenaxr/arena-py/compare/v0.9.4...v0.9.5) (2024-04-08)


### Bug Fixes

* bump version ([54f8aaf](https://github.com/arenaxr/arena-py/commit/54f8aafbdb061e95d97efac1b3b0d9266aef8dfa))

## [0.9.4](https://github.com/arenaxr/arena-py/compare/v0.9.3...v0.9.4) (2024-04-03)


### Bug Fixes

* allow arbirary args for Scene(cli_args=) ([ecd2fdd](https://github.com/arenaxr/arena-py/commit/ecd2fddb7bd8ccb4aa2e8c6464ba68f67ef0b996))
* **auth:** display entire json in arena-py-permissions ([65b534a](https://github.com/arenaxr/arena-py/commit/65b534a915974e8b8b3230d44e30fddf9a81d49a))
* property accesses ([75b3fc6](https://github.com/arenaxr/arena-py/commit/75b3fc6e0985d918b080d303ec2e6f6fea6d7497))


### Documentation

* update objects/attributes to latest schema ([325bc49](https://github.com/arenaxr/arena-py/commit/325bc49a1b58dcf631b2e46ae1686ea3cd8defae))

## [0.9.3](https://github.com/arenaxr/arena-py/compare/v0.9.2...v0.9.3) (2024-02-23)


### Bug Fixes

* bug with obj nonetype detected ([#178](https://github.com/arenaxr/arena-py/issues/178)) ([5343baf](https://github.com/arenaxr/arena-py/commit/5343baf57a04796804ce72fd8ef1de13be5a5bbe))

## [0.9.2](https://github.com/arenaxr/arena-py/compare/v0.9.1...v0.9.2) (2024-02-21)


### Bug Fixes

* **program:** prevent crash during telemetry ([ea53f19](https://github.com/arenaxr/arena-py/commit/ea53f1945676eb89ba9730c21ae9d37e142df47a))

## [0.9.1](https://github.com/arenaxr/arena-py/compare/v0.9.0...v0.9.1) (2024-02-21)


### Bug Fixes

* failed animation object access as obj/dict ([1c78cd1](https://github.com/arenaxr/arena-py/commit/1c78cd1c3166047bd37585fa5767d076921caea9))
* telemetry check for type failing in delete ([31916f3](https://github.com/arenaxr/arena-py/commit/31916f3015c28477701d5f8a4f8e17a6601215df))

## [0.9.0](https://github.com/arenaxr/arena-py/compare/v0.8.0...v0.9.0) (2024-02-12)


### Features

* add basic telemetry to scene ([5702fd0](https://github.com/arenaxr/arena-py/commit/5702fd03e7eddeef825b0914a48d6b846873807b))
* add basic telemetry to scene ([f50a399](https://github.com/arenaxr/arena-py/commit/f50a399e6a6e9818d6750f3e6eaa72d680c9b386))
* Add program object and publish program stats ([212383a](https://github.com/arenaxr/arena-py/commit/212383abda45af4bef77333fee9c6245255f67ff))
* central environment vars file and documentation ([7c95f47](https://github.com/arenaxr/arena-py/commit/7c95f479159b2073ac97514f99e5baf24b5d91c1))
* central environment vars file and documentation ([abc1ab7](https://github.com/arenaxr/arena-py/commit/abc1ab776f4695cd6ed89a2bacf918e012ffad50))
* **objects, attributes:** added automated support for full schema with docstrings ([#171](https://github.com/arenaxr/arena-py/issues/171)) ([359181f](https://github.com/arenaxr/arena-py/commit/359181f293fe14ec1536be81ee8d4d2a39b39c3b))
* **objects:** adding examples for new schema objects ([e2081b3](https://github.com/arenaxr/arena-py/commit/e2081b3febca8425718a37c99879a338ccdd37d0))
* send queue length; minor fixes ([186a7e8](https://github.com/arenaxr/arena-py/commit/186a7e89a33d7937b47864c29a0f594b5be178d3))


### Bug Fixes

* better/more tracing and exit handling for telemetry ([07c8e2b](https://github.com/arenaxr/arena-py/commit/07c8e2ba9897fde3e0d23638e08d533c8cf8456f))
* better/more tracing and exit handling for telemetry ([c4eba98](https://github.com/arenaxr/arena-py/commit/c4eba982c8d6dbfad12984b111ed71841e5b704f))
* bump test ([4e27806](https://github.com/arenaxr/arena-py/commit/4e2780615bf875eb2fcda65c13a59d4bb9f18a35))
* merging with current head ([f044a15](https://github.com/arenaxr/arena-py/commit/f044a1581ef1d383fcf2be92fd9297735dd3801f))
* merging with current head (2) ([4fa95b5](https://github.com/arenaxr/arena-py/commit/4fa95b58ee13d646d9a3a0cb46ca77a7f72e7193))
* minor fixes; add documentation ([3d4146c](https://github.com/arenaxr/arena-py/commit/3d4146c8e54d8c031e0052efb087556a5e62097d))
* minor fixes; add documentation ([4e208ac](https://github.com/arenaxr/arena-py/commit/4e208ac016c76a5820f375181ae2b97073fd3db1))
* missing files for small refactor: env_vars to env ([4cf9f7e](https://github.com/arenaxr/arena-py/commit/4cf9f7e8816bfd51e041aefeb637498e4eab7e8b))
* missing files for small refactor: env_vars to env ([aa891ad](https://github.com/arenaxr/arena-py/commit/aa891ada1d7c7b3ca0590ab5fbe95971994a7241))
* move command interpreter setup to scene ([9b285d1](https://github.com/arenaxr/arena-py/commit/9b285d1a2b7b524cd26f69924cc3f223048fd916))
* move command interpreter setup to scene ([9bc081d](https://github.com/arenaxr/arena-py/commit/9bc081dad2e1c30e90ee5f81e77091defa1724ad))
* pin opentelemetry version ([48d1f00](https://github.com/arenaxr/arena-py/commit/48d1f00f0584d253671523c85cb1a3be6e5df6ba))
* program object id ([145d55c](https://github.com/arenaxr/arena-py/commit/145d55cdf3dad4afaff419deef7cbb187bcf887f))
* remove exit hooks ([b8d118b](https://github.com/arenaxr/arena-py/commit/b8d118bb000cb8fb2d466c2b69cd4ffe19d0859e))
* remove exit hooks ([9ba28f5](https://github.com/arenaxr/arena-py/commit/9ba28f5faed6163057d30702eaca1ce409da0d21))
* show public attributes only ([056ff57](https://github.com/arenaxr/arena-py/commit/056ff57672d2a0aef0076b8a533e1f32f57e3ed7))
* show public attributes only ([b162145](https://github.com/arenaxr/arena-py/commit/b1621451c9f239e655eafe12d2727ef9e4c2fdb4))
* small refactor: env_vars to env and ProgramStats to ProgramRunInfo ([f52c157](https://github.com/arenaxr/arena-py/commit/f52c157c4d869326459cc6b52f08ff172efeaf0e))
* small refactor: env_vars to env and ProgramStats to ProgramRunInfo ([47a98a9](https://github.com/arenaxr/arena-py/commit/47a98a91b8c14ca6e2b5a25832599d9b168d1a6e))
* some docs and scene check ([1a12c51](https://github.com/arenaxr/arena-py/commit/1a12c51478ab56ae734e85f152d6712afe6bc383))
* some docs and scene check ([a5ebe5d](https://github.com/arenaxr/arena-py/commit/a5ebe5d753c4efd17b9d2a1269816eca336a222f))
* **text:** don't pre-populate 'text', users may use correct 'value' ([323d2c8](https://github.com/arenaxr/arena-py/commit/323d2c880d9c918270242aec80d7b071c22ad07d))
* use env vars from constants throughout ([01e5404](https://github.com/arenaxr/arena-py/commit/01e5404e573f6d1ff677a073a7afe8ae110e50e7))
* use env vars from constants throughout ([adadfd1](https://github.com/arenaxr/arena-py/commit/adadfd1da45eb5070c8105246150e9f0f8a326e5))
* when no tracing is defined ([52abf13](https://github.com/arenaxr/arena-py/commit/52abf13292248a3777a9aab06319568e46db701e))


### Documentation

* minor fix ([40875da](https://github.com/arenaxr/arena-py/commit/40875da27072ed5aea58be691b9a4c8442a4da40))
* restore py usage notes ([0106936](https://github.com/arenaxr/arena-py/commit/0106936e40e35f863893c56d6ef26e481fe00c4c))

## [0.8.0](https://github.com/arenaxr/arena-py/compare/v0.7.0...v0.8.0) (2023-11-01)

* **BREAKING CHANGE**: All `arena-user` attributes (descriptors of users in the scene) now are published under the
                       `arena-user` key within the `data` block, rather than the top-level or directly under `data`
                       of the of the MQTT message.

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
