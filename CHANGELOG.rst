Changelog
=========

1.0.2
-----

- Get the list of authors form pagure to query datanommer `#69 <https://github.com/fedora-infra/fedbadges/pull/69>`_

1.0.1
-----

 - Bug Fix: Make sure the fedmsg is iterable in the rules matches function `5e3476c <https://github.com/fedora-infra/fedbadges/commit/5e3476cebd3204c58089141a8ea872c0eb692849>`_


1.0.0
-----

 - Handle authors from pagure messages `#67 <https://github.com/fedora-infra/fedbadges/pull/67>`_
 - Remove the pkgdb criteria `#66 <https://github.com/fedora-infra/fedbadges/pull/66>`_
 - Add cico.pipeline to run tests in CentOS CI `#63 <https://github.com/fedora-infra/fedbadges/pull/63>`_
 - Add support for tox runner `#62 <https://github.com/fedora-infra/fedbadges/pull/62>`_

0.5.3
-----

- Force lowercase when comparing package names with pkgdb `#47 <https://github.com/fedora-infra/fedbadges/pull/47>`_
- A diagram for how fedbadges relates to the other badges.fp.o pieces. `#48 <https://github.com/fedora-infra/fedbadges/pull/48>`_
- Ignore service users (e.g. mbs/mbs.fedoraproject.org) `#55 <https://github.com/fedora-infra/fedbadges/pull/55>`_
- Use open() rather than file() `#56 <https://github.com/fedora-infra/fedbadges/pull/56>`_
- Add openid2fas resolution `#59 <https://github.com/fedora-infra/fedbadges/pull/59>`_

0.5.2
-----

- Set the consumer to consume all topics. `e24b892f7 <https://github.com/fedora-infra/fedbadges/commit/e24b892f7a6d4887b7f2052053e2fe5330f8f7ff>`_
- Merge pull request #45 from fedora-infra/feature/liberal-topic `5236b6e4e <https://github.com/fedora-infra/fedbadges/commit/5236b6e4e347d0c6f98484db890d063addb4bb3e>`_
- Don't award badges to bodhi or taskotron.. `c81f57ecd <https://github.com/fedora-infra/fedbadges/commit/c81f57ecd4c0d5db3b395f0db9dde99806344df9>`_

0.5.1
-----

- Add missing import. `302431e64 <https://github.com/fedora-infra/fedbadges/commit/302431e64bf425e246b69cfa945ec6ca7a1a274b>`_
- Demote this log statement. `4a835748c <https://github.com/fedora-infra/fedbadges/commit/4a835748cf7b9341d374c28a821b4c35f06bd431>`_
- Use threading.local to separate sessions. `d98a1ca6d <https://github.com/fedora-infra/fedbadges/commit/d98a1ca6d0db938a2168e3b93f94512ab90aeaab>`_
- PEP8. `6c8f89d61 <https://github.com/fedora-infra/fedbadges/commit/6c8f89d619827a5f18fa6355fd0b52b4eac8566a>`_
- PEP8. `602c6abb2 <https://github.com/fedora-infra/fedbadges/commit/602c6abb28e56c95828671f9700d642cd69a2e26>`_
- Merge pull request #41 from fedora-infra/feature/race-conditions `0baa4599c <https://github.com/fedora-infra/fedbadges/commit/0baa4599c61469dc0d925131d517fba50edd6c80>`_
- How did this work before...? `80eeeda53 <https://github.com/fedora-infra/fedbadges/commit/80eeeda53e515a0f8cb064ef2f18b9744195b150>`_
- Icky. `8de7b563d <https://github.com/fedora-infra/fedbadges/commit/8de7b563da374110d04f09b0b264230d900320f9>`_
- Suppress integrity errors. `4b69382af <https://github.com/fedora-infra/fedbadges/commit/4b69382af4494092f7e4764ba0fd8915f30d6bc8>`_
- Merge pull request #42 from fedora-infra/feature/suppress-integrity-errors `f72d8d07b <https://github.com/fedora-infra/fedbadges/commit/f72d8d07bfd1998a4db99904560ddb821d0d371a>`_
- Remove unused imports. `dc0691e92 <https://github.com/fedora-infra/fedbadges/commit/dc0691e9290c61167ddc582e0dfbd45fc06acd2b>`_
- Turbo Mode `169142cb1 <https://github.com/fedora-infra/fedbadges/commit/169142cb1bc29d756219a472721a3a79751301f5>`_
- Merge pull request #43 from fedora-infra/feature/turbo-mode `529fbdd27 <https://github.com/fedora-infra/fedbadges/commit/529fbdd271c6ce50d43ddb2a9395f592e9c33992>`_
- Remove unused reference to nick2fas. `2a70f25b3 <https://github.com/fedora-infra/fedbadges/commit/2a70f25b3b774550719ee95335f6c487d29f337e>`_
- Add a new email2fas flag modeled off the existing nick2fas flag. `49941717b <https://github.com/fedora-infra/fedbadges/commit/49941717b71a861a1661ab317c2a67f8d635beff>`_
- Update test that changed since fedmsg_meta changed. `5e2a2305d <https://github.com/fedora-infra/fedbadges/commit/5e2a2305d4569ff30d64982859d3ef8fec1a13be>`_
- Merge pull request #44 from fedora-infra/feature/email2fas `d922631b7 <https://github.com/fedora-infra/fedbadges/commit/d922631b7155b28b52249bebcf765fe307a39dc3>`_

0.5.0
-----

- Apparently its supposed to work this way. `308a1031d <https://github.com/fedora-infra/fedbadges/commit/308a1031d6ed32678810f42bfe9db916bd6250d1>`_
- Delete old pkgdb1 code. `37ebfa746 <https://github.com/fedora-infra/fedbadges/commit/37ebfa746c22887325680273159bf3eac4b1c524>`_
- Don't let pkgdb2 errors turn into false positives. `afbb41efe <https://github.com/fedora-infra/fedbadges/commit/afbb41efe2aa82f06de15f4920b2769d0fe44ffe>`_
- Merge pull request #38 from fedora-infra/feature/pkgdb2-fixes-mark-ii `2abbedcd0 <https://github.com/fedora-infra/fedbadges/commit/2abbedcd0c88360b56e044c42f4b17c77991cbef>`_
- Allow a configurable FAS url for staging.. `dcfd724ba <https://github.com/fedora-infra/fedbadges/commit/dcfd724baeec07f6ac686817fb1b40209741e091>`_
- Merge pull request #39 from fedora-infra/feature/configurable-fas-url `c7f6275c1 <https://github.com/fedora-infra/fedbadges/commit/c7f6275c138319148f06fa3df75b481ed28230a9>`_
- Enhance logging around the main loop. `d36ca095b <https://github.com/fedora-infra/fedbadges/commit/d36ca095b2c36895366d105b782fa0a3d6e6aea6>`_
- Rely on fedmsg-provided queue. `0c278f068 <https://github.com/fedora-infra/fedbadges/commit/0c278f0684c195391a44562c5687e15d9e1be0d0>`_
- Merge pull request #40 from fedora-infra/feature/fedmsg-queueing `c6a771451 <https://github.com/fedora-infra/fedbadges/commit/c6a771451a8c8da58cc88cf637e33c3db1af0e71>`_

0.4.3
-----

- Limit badges to only FAS usernames. `a14fd7826 <https://github.com/fedora-infra/fedbadges/commit/a14fd78269845cbaa497bb6c2bd5d2100d065491>`_
- Merge pull request #36 from fedora-infra/feature/limit-to-fas `2ae084050 <https://github.com/fedora-infra/fedbadges/commit/2ae084050b8eec77f51378b735f1e44c093c595d>`_
- Add an old forgotten test file for pkgdb stuff. `3870e951a <https://github.com/fedora-infra/fedbadges/commit/3870e951aca71a0b8c82a1adb023083db76002b7>`_
- pkgdb2 fixes like we did for fmn. `88beb2f17 <https://github.com/fedora-infra/fedbadges/commit/88beb2f1751f2569f6852bd82b9834b4349770a0>`_
- continue `9c21bd099 <https://github.com/fedora-infra/fedbadges/commit/9c21bd0997c749ef1c777996a610cc204dd36c6c>`_
- Merge pull request #37 from fedora-infra/feature/pkgdb2-fixes `6edfa17c0 <https://github.com/fedora-infra/fedbadges/commit/6edfa17c03fa4b73685d0703d1e180fc05ac1e34>`_

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

