# Changelog

## [2.6.0](https://github.com/sudoleg/YouTubeGPT/compare/v2.5.0...v2.6.0) (2025-02-27)


### Features

* **export:** ref [#267](https://github.com/sudoleg/YouTubeGPT/issues/267), add custom export functionality for answers related to specific video ([4ff407e](https://github.com/sudoleg/YouTubeGPT/commit/4ff407e5a6cd3cd47d4226ce65f87e0daa5e0150))
* **library:** [#267](https://github.com/sudoleg/YouTubeGPT/issues/267), enable downloading of library entries as markdown files ([2b0883e](https://github.com/sudoleg/YouTubeGPT/commit/2b0883e3007c0419cab8c912d2d8a421742f43a0))
* ref [#267](https://github.com/sudoleg/YouTubeGPT/issues/267), enable export of all library entries for a specific channel/video ([5eb97c9](https://github.com/sudoleg/YouTubeGPT/commit/5eb97c99a6fc5fce2dbf86d45103c109a1ac9d33))


### Bug Fixes

* **ui:** unmatched f-string ([08921a0](https://github.com/sudoleg/YouTubeGPT/commit/08921a04408dd77711be1d93c105804ef898747a))

## [2.5.0](https://github.com/sudoleg/YouTubeGPT/compare/v2.4.0...v2.5.0) (2024-11-03)


### Features

* **library:** enable filtering of answers by video ([ecd30e5](https://github.com/sudoleg/YouTubeGPT/commit/ecd30e5244b9fb7e9eabf3c256d96a8625bf356f))
* **library:** enable filtering of summaries by channel ([e00f81e](https://github.com/sudoleg/YouTubeGPT/commit/e00f81eabe3ef13956f50997a9cd2ce0dce59dbf))


### Bug Fixes

* **summary:** invalid method call ([d2ea52d](https://github.com/sudoleg/YouTubeGPT/commit/d2ea52db381d775ac5b48daff09669009bac4301))


### Performance Improvements

* remove redundant method usages ([ee8e163](https://github.com/sudoleg/YouTubeGPT/commit/ee8e1637f8def15bc4aae28ccf78b1934991b586))

## [2.4.0](https://github.com/sudoleg/YouTubeGPT/compare/v2.3.1...v2.4.0) (2024-11-01)


### Features

* add library feature, closes [#145](https://github.com/sudoleg/YouTubeGPT/issues/145) ([e6ec639](https://github.com/sudoleg/YouTubeGPT/commit/e6ec6396545cba98ba00cec34486f0fd816a962a))

## [2.3.1](https://github.com/sudoleg/YouTubeGPT/compare/v2.3.0...v2.3.1) (2024-09-05)


### Performance Improvements

* introduce an env var to store models available to a user ([df85861](https://github.com/sudoleg/YouTubeGPT/commit/df858613650a78f52b40c114de729b34b39be40a))

## [2.3.0](https://github.com/sudoleg/YouTubeGPT/compare/v2.2.1...v2.3.0) (2024-09-04)


### Features

* enable (advanced) transcription using whisper ([1d679f7](https://github.com/sudoleg/YouTubeGPT/commit/1d679f7fd17064fbd659fafda5813ce58abd7724))

## [2.2.1](https://github.com/sudoleg/YouTubeGPT/compare/v2.2.0...v2.2.1) (2024-08-13)


### Bug Fixes

* **helpers:** provide default value for model param in func for token counting ([af395ba](https://github.com/sudoleg/YouTubeGPT/commit/af395baabcc416eb0fa20748bedfb16113c2962d))

## [2.2.0](https://github.com/sudoleg/ytai/compare/v2.1.0...v2.2.0) (2024-07-20)


### Features

* add gpt4o-mini, closes [#86](https://github.com/sudoleg/ytai/issues/86) ([558bd3c](https://github.com/sudoleg/ytai/commit/558bd3c05bd46d60bd351b012d838236de87a6d5))
* display only the models that are available to the user ([c02c245](https://github.com/sudoleg/ytai/commit/c02c245b67b4c976fc8d01b793fda00f58963354))

## [2.1.0](https://github.com/sudoleg/ytai/compare/v2.0.0...v2.1.0) (2024-06-30)


### Features

* **chat:** add options for embedding models, closes [#67](https://github.com/sudoleg/ytai/issues/67) ([657729e](https://github.com/sudoleg/ytai/commit/657729e07797eeae7c15061fda08a7126e0fe637))


### Bug Fixes

* ensure that the users query is embedded using the same model as the transcript ([cbe81b8](https://github.com/sudoleg/ytai/commit/cbe81b8e65448781e5fd1b54ed17275027931dd6))
