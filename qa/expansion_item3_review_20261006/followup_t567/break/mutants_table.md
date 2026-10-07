| 변형 | 종료 코드 | 결과 | 실패 / 검사 | 스크립트 오류 | 첫 실패 검사 |
|---|---|---|---|---|---|
| `control` | 0 | PASS | 0 / 5,089 | 0 | — |
| `hud_box_old_position` | 1 | FAIL | 1 / 5,089 | 0 | HUD intel box stays clear of the transmission panel |
| `hud_box_too_narrow` | 0 | PASS | 0 / 5,089 | 0 | — |
| `lobby_samples_abbreviations` | 1 | FAIL | 9 / 5,089 | 0 | lobby includes the full name SECURITY |
| `lobby_no_second_line` | 1 | FAIL | 11 / 4,020 | 0 | CHR_PROTO_01 lists its unlocked modules without pressing anything |
| `lobby_bracket_first_not_equipped` | 1 | FAIL | 8 / 5,089 | 0 | CHR_PROTO_01 listing brackets FROST LENS |
| `lobby_never_brackets` | 1 | FAIL | 16 / 5,089 | 0 | CHR_PROTO_01 listing marks only the equipped module |
| `lobby_listing_font_9` | 1 | FAIL | 42 / 5,089 | 0 | page2 ModuleChoices_CHR_PROTO_01 font size 9 stays readable (>= 10) |
| `lobby_listing_overlaps_first_line` | 1 | FAIL | 42 / 5,089 | 0 | page2 nonoverlap ModuleLabel_CHR_PROTO_01 / ModuleChoices_CHR_PROTO_01 |
| `lobby_listing_runs_into_button` | 1 | FAIL | 42 / 5,089 | 0 | page2 nonoverlap ModuleChoices_CHR_PROTO_01 / ModuleCycle_CHR_PROTO_01 |
