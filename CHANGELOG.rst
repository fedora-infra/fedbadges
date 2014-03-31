Changelog
=========

0.4.2
-----

- Add some more verbosity to the fedbadges pkgdb caching logs. `617b3901a <https://github.com/fedora-infra/fedbadges/commit/617b3901a62db2b670d856fe5e68951bb1ff4622>`_
- Some rules are expecting this to be in scope when they are compiled. `b7964226b <https://github.com/fedora-infra/fedbadges/commit/b7964226b8692fea58b0ec0b5d172155621749d7>`_
- Handle None from the recipient_key. `40976161f <https://github.com/fedora-infra/fedbadges/commit/40976161fbcb59e3755cff0f26b662828d9b9a56>`_
- Merge pull request #35 from fedora-infra/feature/handle-None `891b5a454 <https://github.com/fedora-infra/fedbadges/commit/891b5a4546f8941a592717274e135a98aeb3921e>`_

0.4.1
-----

- fedbadges.rules is expecting this to be user, not username. `8dd27fa7a <https://github.com/fedora-infra/fedbadges/commit/8dd27fa7a4b528e95b31c4ae3bdc5ae6f1e3045c>`_
- Use a large tg pagination value to really get all of the user's packages. `dea5f0cb7 <https://github.com/fedora-infra/fedbadges/commit/dea5f0cb7b88ce560c34e6959b5d4ee757e59e0a>`_
- Datagrepper is expecting a lowercase "t" here. `347f23475 <https://github.com/fedora-infra/fedbadges/commit/347f23475c3ac15a29eda7af54a392fb35fcc3c2>`_
- Merge pull request #34 from fedora-infra/feature/datagrepper-link-correction `b723ad079 <https://github.com/fedora-infra/fedbadges/commit/b723ad079e060f56590c24ccc87aabe1c7a7ae7b>`_
- Merge pull request #32 from fedora-infra/feature/signature-mismatch `1d3a14039 <https://github.com/fedora-infra/fedbadges/commit/1d3a140395b6373d697b9ef8bd0b4f6fd315547f>`_
- pkgdb2 pagination. `12d65d69a <https://github.com/fedora-infra/fedbadges/commit/12d65d69a7cfaab27fe64602a550a1fd12e0e6f9>`_
- *sigh*, unrelated pep8. `7f2be375d <https://github.com/fedora-infra/fedbadges/commit/7f2be375da47e0b3bc35bad99a6e9227d7d11f8e>`_
- Actually use "page" here, duh. `677c13994 <https://github.com/fedora-infra/fedbadges/commit/677c139949f3f79941688ec922a02a5e9a246240>`_
- Simpler. `a6208075c <https://github.com/fedora-infra/fedbadges/commit/a6208075c2e3b80e1762165857eb8598c6bd25fc>`_
- Simply simpler. `9c0e5349b <https://github.com/fedora-infra/fedbadges/commit/9c0e5349b50bd3a8b7cdcdfb84af633ee42719db>`_
- ..and.. `0d2e1ed20 <https://github.com/fedora-infra/fedbadges/commit/0d2e1ed209ff085bdb6b828abd28403edfa40516>`_
- Merge pull request #33 from fedora-infra/feature/tg-pagination `0709c0297 <https://github.com/fedora-infra/fedbadges/commit/0709c0297cc796a484e46134d81fde4383411ca8>`_

0.4.0
-----

- Allow ints in there. `c355c71da <https://github.com/fedora-infra/fedbadges/commit/c355c71dab5b3aafbc2ef5419b7cd437d791e0d9>`_
- Merge pull request #26 from fedora-infra/feature/allow-ints `bb832c302 <https://github.com/fedora-infra/fedbadges/commit/bb832c302d6f5258fe8ca206c28b84d28728292f>`_
- Typofix. `017244d27 <https://github.com/fedora-infra/fedbadges/commit/017244d27fb4e231be40076c85c4ea776dffd38f>`_
- Add some explanation to the top of the README. `d21a528d3 <https://github.com/fedora-infra/fedbadges/commit/d21a528d3713a7846619af867943417cfcb11ebd>`_
- Add failing tests for using formatting in the criteria operation. `dcfe26971 <https://github.com/fedora-infra/fedbadges/commit/dcfe269717f9df18a5822d8b25390f22e73e219d>`_
- Fix tests by allowing formatting in criteria operations. `7bc69e9ae <https://github.com/fedora-infra/fedbadges/commit/7bc69e9ae31acca9bba372e0970f252df05e3fc1>`_
- Reorganize things and add doc strings to clarify whats going on here. `abf57005e <https://github.com/fedora-infra/fedbadges/commit/abf57005ec68602dcc8fdb666a66732201e4fe47>`_
- Merge pull request #27 from fedora-infra/feature/formattable-operations `d22581c6a <https://github.com/fedora-infra/fedbadges/commit/d22581c6a9fe3b5c0a98c07d5b41acaba1b156db>`_
- Add a negation operator. `6e857bb2f <https://github.com/fedora-infra/fedbadges/commit/6e857bb2fc48294eb85e4508e2bf85c907ceece2>`_
- Add a pkgdb criteria checker. `c84fb8c76 <https://github.com/fedora-infra/fedbadges/commit/c84fb8c76b40e8a122e040e43415c2cc554820bd>`_
- PEP8. `e1580a92b <https://github.com/fedora-infra/fedbadges/commit/e1580a92b394dd86ef10bde324d09a626d1f1c73>`_
- Consolidate pkgdb api urls. `4b557bf64 <https://github.com/fedora-infra/fedbadges/commit/4b557bf643016ab536e636fa060959aa03e118db>`_
- Merge pull request #29 from fedora-infra/feature/pkgdb `8320d7127 <https://github.com/fedora-infra/fedbadges/commit/8320d7127b6249335af0fa960fb283bbfa7df0a5>`_
- Replace internally-used sets with frozensets.  Fixes #25. `e3f225fca <https://github.com/fedora-infra/fedbadges/commit/e3f225fca6af33b999ea6820efce8ba9fc438ec7>`_
- Merge pull request #30 from fedora-infra/feature/frozensets `7bc96b1a5 <https://github.com/fedora-infra/fedbadges/commit/7bc96b1a5d24b72e4f7441d3d13b88bcf21bec4e>`_
- Store a link back to the triggering event. `774079532 <https://github.com/fedora-infra/fedbadges/commit/77407953200ab206e057f11a5eb5750bb8006d9a>`_
- Merge pull request #31 from fedora-infra/feature/store-a-link `f711d7886 <https://github.com/fedora-infra/fedbadges/commit/f711d7886d124f7070ead93b204638bbcaef47bf>`_

0.3.0
-----

- make recipient_nick2fas an allowed config value. `e93b00295 <https://github.com/fedora-infra/fedbadges/commit/e93b00295adb6b2c80de357b08d61aaa67eb8ca1>`_
- Grab tags from yaml if they exist and throw them in the db. `70c00692a <https://github.com/fedora-infra/fedbadges/commit/70c00692ae5967cdc50c0cd3a90d32c3f080c06a>`_
- Fix spelling error in readme. `cfd77ad13 <https://github.com/fedora-infra/fedbadges/commit/cfd77ad13a3f7131b0a140c72b281ff241644c7c>`_
- Correctly deal with counting paginated results from datanommer. `f3df5c9bc <https://github.com/fedora-infra/fedbadges/commit/f3df5c9bc1110dc602ebfbceec4a82aadbe2947e>`_
- Ignore anyone who is an ip address. `d5c401e45 <https://github.com/fedora-infra/fedbadges/commit/d5c401e45f6befa1258594aca13fb1ec97ae7515>`_
- Fix that syntax error. `be7a826b2 <https://github.com/fedora-infra/fedbadges/commit/be7a826b28e4518fa9f7b21fb66a666944778e5f>`_
- PEP8. `e08a60d06 <https://github.com/fedora-infra/fedbadges/commit/e08a60d060a99c41d316448b749c1f7940e6fa7f>`_
- Import the regex module for use by rule lambdas. `b301ed364 <https://github.com/fedora-infra/fedbadges/commit/b301ed364d7af068c35a8ac363d69f275a7a4cf3>`_
- Update test mock now that tahrir-api has changed. `926268871 <https://github.com/fedora-infra/fedbadges/commit/9262688710346a8bbaf1a79484d94d64668bd5a9>`_
- Improve mocked datanommer results for the tests. `dafe6abfd <https://github.com/fedora-infra/fedbadges/commit/dafe6abfd74745b52fe5902b86dded979069b107>`_
- Improve test mocks to account for Person.opt_out. `f3ef596b1 <https://github.com/fedora-infra/fedbadges/commit/f3ef596b1a6d7cd774f08c4f33831f5cb5b1acb2>`_
- More improved mocking.  This gets the test suite running again. `f3288a9ed <https://github.com/fedora-infra/fedbadges/commit/f3288a9ed565ad0052968c0c4fb51a61cc4759d3>`_
- Allow lambda expressions in the datanommer-criteria "operation". `f636733fc <https://github.com/fedora-infra/fedbadges/commit/f636733fc47559a588ca13aec469b160715cf86b>`_
- Use the modern link to the live badge rules. `67bd15bdf <https://github.com/fedora-infra/fedbadges/commit/67bd15bdf7b915905df30dae37c1fdc6e59815e6>`_
- Allow criteria definitions to overload these query arguments too. `4ebcd3caf <https://github.com/fedora-infra/fedbadges/commit/4ebcd3caf3b78025f92b3e6f10942bb1809e59c6>`_
- Publish a fedmsg message when a user's rank changes. `af624bfda <https://github.com/fedora-infra/fedbadges/commit/af624bfda68e74745f2677b9709680b34de676d1>`_
- Oh, and tahrir-api will emit this message for us too using our notification_callback. `6a0aec465 <https://github.com/fedora-infra/fedbadges/commit/6a0aec465df10c98a97b8ae06b9c7b2e353fb7cd>`_
- Remove explicit fedmsg initialization.  It is unnecessary. `932d28bb3 <https://github.com/fedora-infra/fedbadges/commit/932d28bb325b441bb85662b8685ee33e562b5399>`_
- Move notification_callback from a method to a function in fedbadges.utils. `aa8f6878a <https://github.com/fedora-infra/fedbadges/commit/aa8f6878a00de4b55df3abc9f9704580e8b03523>`_
- Merge pull request #22 from fedora-infra/feature/lambads-in-criteria `30433cfeb <https://github.com/fedora-infra/fedbadges/commit/30433cfeb60404d55760244e1e18e1002634332f>`_
- Merge pull request #23 from fedora-infra/feature/publish-message-on-rank-change `f9070dbad <https://github.com/fedora-infra/fedbadges/commit/f9070dbade0fdc6a6408ce5640436feca1a28ef5>`_

0.2.4
-----

- More careful with transactions for el6. `454dba7bc <https://github.com/fedora-infra/fedbadges/commit/454dba7bc86297f7c024e409e2a7ef76d0203e66>`_
- Save the badge_id in the badge dict. `68801daf2 <https://github.com/fedora-infra/fedbadges/commit/68801daf252a58da6f94fad39dbbdb1b5e49ab8a>`_
- Machinery for using nick2fas. `079bc3024 <https://github.com/fedora-infra/fedbadges/commit/079bc30243c86a98b2ffbb118c7c33ebdb4880ce>`_
- Use nick2fas correctly. `5af5e3373 <https://github.com/fedora-infra/fedbadges/commit/5af5e3373da37a0b8006c824178709c127295e54>`_
- Merge branch 'feature/using-nick2fas' into develop `58bfd48ef <https://github.com/fedora-infra/fedbadges/commit/58bfd48ef1eb88088267a1359acebec73f86c93f>`_
- Exclude persons who opt-out.  For fedora-infra/tahrir#112. `7a31a8afe <https://github.com/fedora-infra/fedbadges/commit/7a31a8afe0c1f3da453599a360f7f885c031bd67>`_

0.2.3
-----

- In the future, add_badge will always return a smart id. `1fcd7a5eb <https://github.com/fedora-infra/fedbadges/commit/1fcd7a5ebf19c1c1f4d0e011b25ac20687768ec4>`_

0.2.2
-----

- Include requirements in the next release. `8ce3baad1 <https://github.com/fedora-infra/fedbadges/commit/8ce3baad1550331e25d641e2ac6c1213d5c484da>`_
- How did that get in there? `21d4323cc <https://github.com/fedora-infra/fedbadges/commit/21d4323cc202c12156ddc9ea51fdad7204df944d>`_
- Make BadgeRules accept the actual issuer_id. `f771bb5c9 <https://github.com/fedora-infra/fedbadges/commit/f771bb5c988b900dd940505e8eb8cc7db22179ea>`_
- Pass the whole badge dict along with the fedmsg message. `5719a556a <https://github.com/fedora-infra/fedbadges/commit/5719a556a3594db36f8c2f47915bef6b56754689>`_
- Link to the ansible repo. `c87c25925 <https://github.com/fedora-infra/fedbadges/commit/c87c25925d59c60b6e797bec7a60d0f4e3a5b462>`_
- Merge pull request #9 from fedora-infra/feature/link-to-badge-repo `97cb530f8 <https://github.com/fedora-infra/fedbadges/commit/97cb530f890bf521cb13e3b2c4dbbab6ca1b19e4>`_
- Merge pull request #7 from fedora-infra/feature/issuer-ambiguity `a1c6568c1 <https://github.com/fedora-infra/fedbadges/commit/a1c6568c1ab15f507c84f99c05e05d5bc2fd7264>`_
- Merge pull request #8 from fedora-infra/feature/more-info-in-messages `ceeea73ae <https://github.com/fedora-infra/fedbadges/commit/ceeea73ae5d6e44f1a3f5c12a14e426f91ac6b81>`_
- Allow topic and otherwise comparisons to use "endswith". `c8e66962c <https://github.com/fedora-infra/fedbadges/commit/c8e66962c0bfe3bbc90481967e607930dd91a1e4>`_
- Initialize fedmsg early. `c854d72c6 <https://github.com/fedora-infra/fedbadges/commit/c854d72c6df2b8dcd267190282b9e9bdf7b54570>`_
- Pass along the tahrir user_id so we can construct URLs from it elsewhere. `c9f648148 <https://github.com/fedora-infra/fedbadges/commit/c9f6481488fa001440585a9750a0b4709834370e>`_
- Merge pull request #10 from fedora-infra/feature/endswith-comparisons `141ead243 <https://github.com/fedora-infra/fedbadges/commit/141ead243de4a9c16e70fac1fcf8d109b27554c5>`_
- Merge pull request #11 from fedora-infra/feature/init-fedmsg-early `6a027e6fb <https://github.com/fedora-infra/fedbadges/commit/6a027e6fb35700ab8ce5aeacdb89dc2d60b7286a>`_
- Merge pull request #12 from fedora-infra/feature/still-more-fedmsg-info `75c2b3dc1 <https://github.com/fedora-infra/fedbadges/commit/75c2b3dc1b7e257f74ca9635f0b7268823e8f671>`_
- This is the right way to do this. `1d7d33639 <https://github.com/fedora-infra/fedbadges/commit/1d7d3363948f396a5925a216966bc72fe16a2023>`_
- Patch out fedmsg.init so tests are idempotent. `fe3d098d9 <https://github.com/fedora-infra/fedbadges/commit/fe3d098d9af2f860a04c29c0510ecd98594e45c7>`_
- Add failing test for dotted substitutions. `e509c4058 <https://github.com/fedora-infra/fedbadges/commit/e509c405800577b21992a479aca72cb9c7e82b63>`_
- Clarify that it is "recipient" not "recipient_key". `5082c3075 <https://github.com/fedora-infra/fedbadges/commit/5082c3075ece958b7c32ede3861c09107e40338f>`_
- Enforce possible arguments to BadgeRule. `1774dd555 <https://github.com/fedora-infra/fedbadges/commit/1774dd555350e680430e2b752c578326c7bbf3b3>`_
- Use older formatting so we can use dotted lookups directly. `155cc28bd <https://github.com/fedora-infra/fedbadges/commit/155cc28bdc560b55a6288c097837b4145715c69d>`_
- Lowercase subsitutions.  Workaround for wiki username. `4dd16600b <https://github.com/fedora-infra/fedbadges/commit/4dd16600b6a7d443b9d8ff84e4995b326555114a>`_
- Use twisted's callLater to mitigate potential race conditions. `14c9f9a7d <https://github.com/fedora-infra/fedbadges/commit/14c9f9a7dac61495795c3157fead9932d118f3ec>`_
- .get_person doesn't work the way I thought it did. `7cbcb49c2 <https://github.com/fedora-infra/fedbadges/commit/7cbcb49c2901f9e628b832b235ddfb031f2b7b50>`_
- Typofix. `e99b6619b <https://github.com/fedora-infra/fedbadges/commit/e99b6619b944c1987976c4c1344ab98cc997c2b6>`_
- Remove redundant clause in the docs. `a6a6e377e <https://github.com/fedora-infra/fedbadges/commit/a6a6e377e73073c14489c82eb1bb84e9c5b734f3>`_
- Make badge matching fail more gracefully. `553a00647 <https://github.com/fedora-infra/fedbadges/commit/553a00647dc0c37766db7b04c50cebf310315a8c>`_
- Add an example yaml file from our realdeal badges repo to the tests. `1cbbf7fad <https://github.com/fedora-infra/fedbadges/commit/1cbbf7fadce22ee5fc8670c225b78194e94598a1>`_
- Move MockHub out into a test utils module. `821b78ef2 <https://github.com/fedora-infra/fedbadges/commit/821b78ef29b6d961cc290fec8d8e248d65bead96>`_
- Add failing test for complicated tagger trigger. `f09523a4a <https://github.com/fedora-infra/fedbadges/commit/f09523a4ac79091f759feab4cab6b3476c291ab9>`_
- Add a parent relationship to the badgerule tree. `5f3c0416e <https://github.com/fedora-infra/fedbadges/commit/5f3c0416e5ae266935b97a380fd984cb0194590e>`_
- Add and test a graceful decorator. `691c8285b <https://github.com/fedora-infra/fedbadges/commit/691c8285b5b199d69a7325e7006a3725c47f6e5d>`_
- Add a positive test for the complicated tagger trigger. `9a057db4d <https://github.com/fedora-infra/fedbadges/commit/9a057db4d40f63ebfc9dc40c557331693f1ac14d>`_
- PEP8. `679dd0011 <https://github.com/fedora-infra/fedbadges/commit/679dd001180640b255a3cc15c0daa9bada12f607>`_
- Stop using __builtins__ directly. `1813c1d54 <https://github.com/fedora-infra/fedbadges/commit/1813c1d54161fb09d35a59966c4a60be67c83cd5>`_
- Support numeric substitutions with type in tact. `a570a43a1 <https://github.com/fedora-infra/fedbadges/commit/a570a43a1562720c2d96d57115bf09ad7c66104c>`_
- Make sure that nested subs work like that too. `dfe313140 <https://github.com/fedora-infra/fedbadges/commit/dfe313140de85ae74cb64e403020af29627f136e>`_
- Expand the way subsitutions are constructed. `74314be3d <https://github.com/fedora-infra/fedbadges/commit/74314be3db6c6041728bee6ca66e051ff5c92fa7>`_
- Further fix and test for nested recipient_key. `df2ee10f1 <https://github.com/fedora-infra/fedbadges/commit/df2ee10f181aeda81ad55a8eaae74ed648a995d6>`_
- Use transactions and update to the latest tahrir-api. `2b1e55d13 <https://github.com/fedora-infra/fedbadges/commit/2b1e55d13005c15c38b782be99af2d7a3f6334e6>`_

0.2.1
-----

