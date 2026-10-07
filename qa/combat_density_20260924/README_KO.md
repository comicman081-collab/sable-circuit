# 전투 밀도 · 전투 사운드 개선 (2026-09-24)

사용자 요청: "몹이 한 번에 3마리 정도만 나온다 → 늘려라 / 발사·피격·타격음을 더 웅장하고 자연스럽게."

이 폴더는 기술 검증 기록입니다. 사람 플레이테스트, 밸런스 최종 승인, 청각·시각 승인,
배포 승인이 아닙니다.

## 1. 적 밀도

| 항목 | 이전 | 현재 |
|---|---|---|
| 작전 1 총 적 수 | 6 | 21 |
| 작전 2–5 총 적 수 | 7–10 | 각 21 |
| 일반/정예 방 동시 교전 | 최대 3 | 1파 4기 → 2기 이하 남으면 증원 3기 (최대 5기 동시) |
| 보스 방 | 보스 단독 | 보스 + 호위 2 → 1기 남으면 증원 2기 × 2회 |

- 적 종류는 작전별 도입 순서를 따릅니다: 1 드론/BULWARK, 2 +CINDER(RAM), 3 +VESPER(MORTAR),
  4 +PRISM, 5 +NULL PYLON. 인간형 적은 없습니다.
- 스폰 위치: `Site7Battlefield._build_spawn_points()`가 방 바닥에서 최원점 샘플링으로 최대
  10개 슬롯을 만듭니다. 분대 스폰에서 250px 이상, 엄폐물에서 44px 이상 떨어지고, 실제 경로
  계획으로 분대까지 도달 가능한 슬롯만 사용합니다(`site7_traversal_audit_smoke`).
- 증원: 방 데이터의 `reinforce_at`. 남은 적 수가 그 이하가 되면 1.4초 뒤 다음 파가 들어옵니다.

### 많아져도 공정하게 — 이번 회차 추가

- **공격 토큰** (`site7_enemy_tactics.gd`, `MAX_CONCURRENT_ATTACKERS = 3`): 경고(WINDUP)·사격·돌진을
  동시에 커밋할 수 있는 로봇은 보스를 포함해 최대 3기입니다. 나머지는 자기 레인을 유지하며
  기동합니다. 화면에는 5–7기가 움직이지만, 경고가 한꺼번에 쏟아지지는 않습니다. 이미 알린 경고와 탄도 고정 규칙은 그대로입니다.
- **군집 분리** (`enemy_actor.gd`, 반경 140px, 최대 80px/s): 드론·PRISM·BULWARK·CINDER가
  하나의 실루엣으로 겹치지 않게 서로 밀어냅니다. 고정 포대(MORTAR/PYLON/보스)와 경고·사격·돌진
  중인 로봇은 밀지 않습니다.
- **선회 방향 교대** (`story_stage_01.gd`): 이전에는 선회 방향을 적 종류 ID 해시로 정해서, 같은 종류끼리 모두 같은 방향으로 돌며 겹쳤습니다. 이제 스폰 순서대로 시계/반시계를 번갈아 배정합니다.
- 작전 5 보스 방 완화: 마지막 증원의 NULL PYLON(엄폐 무시 재머)을 드론으로 바꾸고,
  호위 PRISM HP를 170에서 150으로 낮췄습니다. 테스트 봇이 CARRIER를 103 HP 남기고 전멸한 뒤 조정했습니다.
  PYLON은 R04 정예 방에 2기 그대로 있습니다.

## 2. 전투 사운드

- 25개 큐, 94개 변형(`assets/audio/combat_r04/*.res`, 약 11MB, 48kHz PCM16). 큐마다 2–4개 변형을 두고,
  셔플 백 방식이라 같은 샘플이 연속으로 나오지 않습니다.
- 재생마다 큐별 피치 범위 안에서 흔들고, 우선순위 90 미만은 ±1dB 게인 지터를 줍니다.
- 위치 기반 재생: `AudioStreamPlayer2D`(최대 2600px, 감쇠 1.35, 패닝 0.65).
- 과밀 방지: 같은 발사원·같은 큐의 한 프레임 중복 억제, 피격/타격/재장전 쿨다운, 큐당 5보이스,
  전체 24(일반)/32(고우선) 보이스.
- 전투 버스 체인: EQ6(저역 +2.5/+1.5dB, 고역 −1dB, 무게감) → 컴프레서(−16dB, 3:1, 여러 총성을 한 전투음으로 묶음)
  → 짧은 홀 리버브(room 0.58, wet 0.14, 공간감·꼬리) → 리미터(−1.5dB 실링).
- 보스 경고/파괴음이 나오는 0.8초 동안 나머지 효과음을 5dB 낮춥니다(덕킹).
- 새로 연결한 레이어:
  - 대원 피격: 피격음(impact_body)에 캐릭터별 피격 음성(aster/rook/mica_hurt)을 겹칩니다.
  - 캐릭터별 재장전음.
  - 엄폐물 피탄: 도탄(30%) 또는 콘크리트 타격음.
  - 방패/장갑 경감: shield_hit.
  - 보스 경고: boss_charge.
  - 적 파괴: 일반 로봇은 armor_break, 보스는 boss_destroy. 이전에는 FORGE/CARRIER 보스가 소리 없이 파괴됐습니다.
- 출처: 사용자가 제공한 R04 SFX 팩과 앱 내 CC BY 3.0 폭발음 크레딧. 로컬 생성·합성 음원은 없습니다.

## 3. 검증

### 전 작전 기술 플레이스루 (`operation_0N/full_operation.json`)

테스트 봇이 실제 물리, 무기 쿨다운, 탄환 충돌, 임무 상호작용을 사용하고 치트는 쓰지 않습니다.
스킬·회피·엄폐는 쓰지 않습니다.

| 회차 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 1차 (토큰 이전) | 봇 정지 → 실패 | PASS | PASS | 보스 방 전멸 | PASS |
| 2차 (토큰·분리·봇 수정) | PASS | PASS | PASS | PASS | 보스 방 전멸 (CARRIER 103 HP) |
| 3차 (작전 5 완화) | – | – | – | – | PASS × 2 |

최종 저장본 5개는 모두 `EXTRACTED`, 적 21/21 처치, 게임 시간 약 127–148초입니다.

1차 작전 1 정지의 원인은 테스트 봇이었습니다. 봇은 조종 대원을 `debug_drive`로 움직이는데,
그 대원이 쓰러졌다가 부활하면 이 플래그가 남아서 예전 입력을 계속 재생했습니다
(ASTER가 (9342,130)에서 멈춤). 같은 위치에서 경로 계획을 따로 확인해 보니 정상이었습니다.
봇이 조종하지 않는 대원의 `debug_drive`를 해제하도록 고쳤습니다.

### 신규/수정 테스트

- `tests/smoke/combat_density_smoke.gd` (신규) → `density_contract.json`: 작전별 동시 교전 수,
  실제 스폰 경로로 7기 동시 배치, 동시 공격 3기 이하, 토큰 공유(2기 이상 동시 공격 프레임 존재),
  14초 동안 공격 37회, 기동 로봇 겹침 비율 0.3%. 이 픽스처는 적의 규율만 재기 위해 대원 HP를 높였습니다.
- `site7_battle_flow_smoke.gd`, `demo_combat_entry_regression.gd`: 옛 적 수(3기/보스 1기)가 하드코딩되어 있었습니다.
  이제 임무 데이터에서 기대값을 읽습니다.
- `demo_combat_entry_regression.gd`: 직전까지 추종 대원으로 사격하던 대원은 조종 전환 직후
  실제 무기 쿨다운이 남아 있습니다. 그래서 트리거를 한 발사 간격 동안 유지하도록 했습니다.
- `site7_full_operation_smoke.gd`: 위의 봇 `debug_drive` 해제.
- `combat_sfx_r04_smoke.gd`, `demo_integration_check.gd`: `--out=` 인자 지원을 추가했습니다(기본 경로는 그대로).

- 공격 토큰은 물리 처리 중인 로봇만 셉니다. 처음 버전은 픽스처에서 정지시킨 로봇이 WINDUP 상태로
  토큰을 계속 쥐고 있어서 `enemy_cover_navigation_regression`의 슬롯 3이 실패했습니다.
  정지 중이거나 삭제 대기인 로봇은 쏠 수 없으므로 토큰을 갖지 않게 고친 뒤 PASS했습니다.

### 회귀 결과 (최종 코드, headless)

| 테스트 | 결과 |
|---|---|
| combat_density_smoke (신규) | PASS 37 |
| site7_full_operation_smoke 1–5 | 5/5 EXTRACTED (위 표) |
| site7_traversal_audit_smoke | PASS 1253 |
| enemy_cover_navigation_regression (작전 1–5) | PASS |
| site7_cover_ai_check | PASS_TECHNICAL_ONLY 46 |
| cover_navigation_smoke | PASS 15 |
| site7_player_cover_collision_smoke | PASS 5 |
| site7_world_route_navigation_smoke | PASS 49 |
| site7_battle_flow_smoke | PASS |
| demo_combat_entry_regression | PASS 32 (`combat_entry_regression.json`) |
| combat_sfx_r04_smoke | PASS 558 (`regressions/combat_sfx_runtime_smoke.json`) |
| demo_integration_check | PASS 26 (`regressions/demo_integration/`) |
| site7_drone_app_smoke / site7_anchor_app_smoke | PASS 171 / 271 |
| m2_story_flow / m7_authored_visual / campaign_progression 94 / rook_motion_lab_app 1895 | PASS |

알려진 기존 실패: `site7_emission_owner_smoke`는 퇴역한 인간형 적(RIFLE/SHIELD/ABERRANT)을 스폰하려다
null 오류로 멈춥니다. 이번 변경과는 무관하며, 로봇 로스터로 옮기는 별도 작업으로 분리했습니다.

## 4. 과거 증거 파일 덮어쓰기 (알림)

출력 경로가 고정된 테스트를 `--out` 없이 다시 실행해서, 추적되지 않던 과거 파일 3개를 덮어썼습니다.

- `qa/music_integration_20260920/combat_regression.json`: 원본(2026-09-20, 20개 체크 PASS. 같은 폴더의
  `IMPLEMENTATION_REVIEW.md`에 기록됨)은 복구할 수 없습니다. 파일 안에 덮어쓰기 사실을 적어 두었고,
  현재 결과는 `combat_entry_regression.json`에 있습니다.
- `qa/sfx_integration_20260919/runtime_smoke.json`, `qa/demo_20260920/integration_headless.json`: 같은 날
  더 이른 시각(11:50, 11:11)에 같은 테스트의 PASS 결과로 덮어썼습니다. 원본 바이트는 없습니다.

## 5. 실제 게임 사운드 전투 영상 (1080p, 10초)

`tools/environment/record_stage_battle_with_audio.py`로 녹화했습니다(`SABLE_CAPTURE_FULL_WAVES=1`).
캡처 스크립트의 새 옵트인 옵션으로, 프리뷰에서도 방의 증원 파를 캠페인과 똑같이 붙입니다.

| 클립 | 프레임 | 오디오 peak / RMS | 동시 적 | 화면 안 동시 적 | 재생된 효과음 / 최대 보이스 |
|---|---|---|---|---|---|
| `video_124149/stage1/stage1_combat_10s_sound_1080p.mp4` | 600 | 0.503 / 0.038 | 4 | 2 | 285 / 19 |
| `video_124149/stage5/stage5_combat_10s_sound_1080p.mp4` | 600 | 0.427 / 0.043 | 5 (증원 도착) | 4 | 268 / 17 |

- 네이티브 1920×1080, 60fps, Godot AudioServer 스테레오 믹스(추가 사운드트랙 없음).
  `validate_1080p.json` 컨테이너·동적 캡처 게이트 PASS. 이 결과는 해상도와 디코딩만 보증하고 품질은 보증하지 않습니다.
- `video_120744/`는 공격 토큰·군집 분리 이전 녹화입니다. 이전 상태 비교용으로 남겨 두었습니다.
  이전 프레임에서는 드론 두 기가 겹쳐 보였고, 현재 `stage1/frame_0030.png`에서는 떨어져 있습니다.
- 10초 창은 첫 교전 방 초반만 담습니다. 작전 1 클립에서는 증원 조건(남은 적 2기 이하)이 창 안에서
  충족되지 않아 동시 적이 4기입니다.
