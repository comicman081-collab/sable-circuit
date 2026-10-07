# 확장 항목 3 — 보스 정보의 장비화 (2026-10-06)

범위: **3A–3E만**. 시작 HEAD `453d20cb`(항목 3 제작 지시 공개), 쓰기 코드 기준 `381ef0fb`. `AGENTS.md`와 지시서 전체, 특히 5절·9.13절을 읽고 9.13.7 순서로 진행했다. 항목 4·5·1D는 시작하지 않았다. 수치는 사용자가 검토할 **잠정 권장값**이다.

## 1. 커밋과 바뀐 파일

| 순서 | 로컬 커밋 | 내용 |
|---|---|---|
| 1 | `4d0a63f2` | 기존 schema 5 쓰기 코드로 만든 `save_v5.json`만 단독 반입 |
| 2 | `fb8a5ca8` | 표본 키 8개, 새 보스 갈래, 분석 5행, 저장 6, 공급·마이그레이션 검사 |
| 3 | `4ab13d7a` | 모듈 5개 효과·debug 필드·실제 액터 검사. 효과 수치는 이 커밋 하나에 모았다 |
| 4 | `c83ddf6c` | 무기 2개, 새 해금 두 줄, 프로필 사본 배관, 코드 VFX 두 가문, 무기 검사 |
| 5 | `d6094211` | 분석 쪽 나누기, 연산자별 한 칸 모듈 순환, 8키 표시, 지오메트리·캡처 검사 |
| 6 | 기록 커밋 | 이 README와 아래 증거. 해시는 `git log -1 --format=%H -- qa/expansion_item3_20261006/README_KO.md`로 확인 |

모든 커밋은 경로를 지정했다. 작업 트리의 남의 파일을 스테이징하지 않았고 원격 작업은 하지 않았다.

| 그룹 | 파일 / 역할 |
|---|---|
| 표본 권위 | `scripts/core/intel_samples.gd` + UID: 8키, 약어, 초기화·정제·합계, 적→키 매핑 |
| 저장·실제 흐름 | `scripts/core/campaign_progression.gd`, `scripts/missions/story_stage_01.gd`: 초기·확보·손실 표본, 저장 6, 해금 추가 |
| 데이터 | `data/progression/intel_discoveries.json`, `data/progression/weapons.json`: 분석 5행과 무기 2행만 추가 |
| 모듈 | `scripts/combat/operator_skill_controller.gd`: 시전마다 현재 한 칸을 읽는 시간·거리 효과, 누적 없음 |
| 무기·VFX | `scripts/actors/operator_actor.gd`, `scripts/combat/prototype_projectile.gd`, `scripts/vfx/combat_muzzle_vfx.gd`, `combat_hit_vfx.gd`: 사본의 가문 두 필드만 교체, Painter 경유 |
| UI | `scripts/ui/base_lobby.gd`, `story_stage_hud.gd`, `mission_results.gd`: 3+3+2 분석 쪽, 3/3/2 모듈 선택, 8키 표시 |
| 기존 시험 확대 | `run_contract_save_smoke.gd`, `m10_persistence_smoke.gd`, `m13_weapon_base_migration_smoke.gd`, `m13_weapon_loadout_smoke.gd`, `combat_vfx_overhaul_smoke.gd` |
| 새 시험 | `intel_supply_smoke.gd`, `module_expansion_smoke.gd`, `weapon_expansion_smoke.gd`, `lab_geometry_smoke.gd`, `expansion_item3_capture.gd`, `weapon_envelope.gd`와 각각 UID |
| 고정물·러너 | `tests/fixtures/run_contract/save_v5.json`; 러너 quick 4개와 full 전용 캡처 1개 추가(56 quick + 32 full 전용 = 88) |

`assets`, `art_src`, `motion_lab_v1`, 미션·스토리 데이터, 보스 코드·패턴·원화, `upgrades.json`, 계약·GameFlow, `vfx_painter.gd` 변경 **0**. 승인된 작전 10 파일 **17/17 바이트 불변**([검증 로그](records/art_hashes.log)). [범위 확인](records/scope_audit.json). 기존 분석 3행과 무기 6행은 JSON 행 전체가 같고, `_sync_weapon_unlocks`의 기존 세 줄 뒤에 두 줄만 더했다. 기존 세 모듈 갈고리·효과는 그대로다.

### schema 5 고정물의 출처

쓰기 코드의 Git blob은 `381ef0fb`와 시작 HEAD 모두 `cbd6062f094bea3629e04a5b1648cf6b48985190`이었다. **번호를 올리기 전에** 기존 v4 고정물을 불러 `CampaignProgression._save()`로 v5를 썼다. 3키·분석 하나·모듈 하나·무기고 1레벨, snapshot 전체와 run serial/거래 중복 방지 목록의 무손실 readback을 확인했다. [실행 코드](records/write_v5_fixture.gd), [로그](records/write_v5_fixture.log). 이는 과거 writer용 증거이므로 현재 schema 6으로 다시 생성하지 않는다.

`save_v5.json` SHA-256: `0531c6e4d64c99479105954001f9c2fe7c4d0c868bfd72f2b8339d56310e8002`.

## 2. 시험과 대조

Godot 4.7.1, 모든 저장·출력은 D: 프로젝트 안. 각 러너 시작과 QA 반입 전 `Get-CimInstance Win32_Process`로 기존 `run_regression_suite.py`가 없음을 확인했다. 동시에 두 러너를 띄우지 않았고 러너 중에는 QA를 쓰지 않았다.

### 중간 검증

| 명령의 `--only` 목록 | stamp / 결과 | 검사 수 |
|---|---|---|
| `upgrade_economy,m10_base_ui,m10_persistence,contract_save,intel_supply` | `20261006_001504_custom` **5/5 PASS** | 225 / 10 / 27 / 169 / 83 |
| `m9_skill,module_expansion,m10_intel` | `20261006_001849_custom` **3/3 PASS** | 44 / 86 / 39 |
| `contract_save,weapon_expansion,combat_vfx,m13_migration,m13_campaign,m13_loadout` | `20261006_002254_custom` **6/6 PASS** | 175 / 122 / 195 / 9 / 16 / 53 |
| `upgrade_economy,m10_base_ui,lab_geometry` | `20261006_003046_custom` **FAIL, 2/3 PASS** | 225 / 10 / 3694 |
| `lab_geometry,lab_capture_geometry` | `20261006_003607_custom` **2/2 PASS** | 3694 / 2 |

중간 실패를 숨기지 않는다. 직접 UI 진단은 첫 헤더 노드 경로 오류와 페이지 버튼/첫 분석 행 겹침을 잡았고 둘 다 수정했다. 위 러너 FAIL의 마지막 원인은 입장 tween 뒤 패널 높이 `202.0002px`와 정수 `202px`의 exact equality였다. **새 시험에만** 0.001px 부동소수 허용을 두었다. 패널 1224×202, 화면 안·비겹침·전체 글자 계산 조건은 유지했다. [실패 요약](records/ui_before_SUMMARY_KO.md), [수정 후 요약](records/ui_after_SUMMARY_KO.md).

### 최종 검증

명령 `python tools/maintenance/run_regression_suite.py --suite quick` **1회**, stamp `20261006_003832_quick`: **56/56 PASS**, 494초, 커밋 `d609421199072d533abf0366225ae36d2f414471`, 시작 dirty=0. [요약](records/quick_SUMMARY_KO.md), [전체 결과 JSON](records/quick_summary.json). 기존 QA 변경0/삭제0/추가0.

| 러너 id | 결과 | 검사 수 | 시간 s |
|---|---|---:|---:|
| combat_density | PASS | 67 | 18.0 |
| cover_navigation | PASS | 43 | 17.4 |
| floor_segment | PASS | 23 | 35.5 |
| combat_query_fastpath | PASS | 34 | 9.8 |
| player_cover | PASS | 5 | 6.6 |
| cover_alpha_clip | PASS | 5 | 1.4 |
| cover_texture | PASS | 17 | 2.0 |
| battle_flow | PASS | — | 7.8 |
| combat_entry | PASS | — | 6.4 |
| drone_app | PASS | 171 | 1.8 |
| anchor_app | PASS | 271 | 1.4 |
| campaign_data | PASS | 292 | 0.4 |
| upgrade_economy | PASS | 225 | 1.4 |
| boss_registry | PASS | 163 | 12.2 |
| boss_pattern | PASS | 978 | 2.6 |
| boss_duel | PASS | 2184 | 55.5 |
| boss_room_fairness | PASS | 21 | 15.6 |
| robot_roster | PASS | 302 | 7.4 |
| enemy_facing | PASS | 224 | 2.4 |
| machine_source | PASS | 436 | 2.0 |
| emission_owner | PASS | 1293 | 4.0 |
| m2_story | PASS | 27 | 4.6 |
| m9_skill | PASS | 44 | 4.0 |
| m10_base_ui | PASS | 10 | 0.8 |
| m10_persistence | PASS | 27 | 0.6 |
| run_contract | PASS | 34 | 5.0 |
| contract_offers | PASS | 26950 | 1.6 |
| contract_ui | PASS | 484 | 7.4 |
| redline | PASS | 78 | 4.2 |
| contract_save | PASS | 175 | 0.6 |
| intel_supply | PASS | 83 | 1.6 |
| module_expansion | PASS | 86 | 2.8 |
| weapon_expansion | PASS | 122 | 2.6 |
| lab_geometry | PASS | 3694 | 4.4 |
| m12_revive | PASS | 25 | 3.8 |
| play_log | PASS | 25 | 5.0 |
| hit_hurt_vfx | PASS | 47 | 2.4 |
| combat_vfx | PASS | 195 | 2.4 |
| elite_affix | PASS | 71 | 4.2 |
| elite_expansion | PASS | 438 | 6.4 |
| zone_hazard | PASS | 366 | 46.5 |
| hazard_expansion | PASS | 438 | 22.7 |
| firing_lane | PASS | 325 | 22.6 |
| platform_carry | PASS | 6 | 5.2 |
| contact_carry | PASS | 27 | 14.0 |
| world_layout | PASS | — | 13.4 |
| mood_light | PASS | — | 58.5 |
| walk_registration | PASS | — | 1.2 |
| plate_axis | PASS | 2 | 2.6 |
| variety_placement | PASS | 10 | 1.6 |
| seam_waiver | PASS | 10 | 2.0 |
| mood_contact | PASS | 13 | 2.6 |
| deploy_warmer | PASS | 83 | 6.0 |
| m13_migration | PASS | 9 | 0.6 |
| m13_campaign | PASS | 16 | 0.4 |
| m13_runtime | PASS | 18 | 4.0 |

이 러너가 끝난 뒤 명령 `python tools/maintenance/run_regression_suite.py --only m10_intel,m13_loadout,campaign`, stamp `20261006_004731_custom`: **3/3 PASS**, 42초, 같은 커밋과 dirty=0. [요약](records/full_only_SUMMARY_KO.md), [JSON](records/full_only_summary.json). QA guard도 변경0/삭제0/추가0.

| 러너 id | 결과 | 검사 수 | 시간 s |
|---|---|---:|---:|
| m10_intel | PASS | 39 | 4.0 |
| m13_loadout | PASS | 53 | 4.2 |
| campaign | PASS | 235 | 20.4 |

C-11 기존 검사 수: boss_registry163, boss_pattern978, boss_duel2184, boss_room_fairness21, robot_roster302 모두 동일 PASS.

`upgrade_economy`, `m10_base_ui`, `m10_intel`, `campaign`, C-11 보스 시험의 소스는 시작 HEAD와 같다. 경제·보스 한계와 검사 수를 낮추지 않았다. 기존 검사는 지우지 않고 카탈로그·키·고정물 순회만 넓혔다.

### 사본 대조

프로젝트 `.cache/diag/expansion_item3_20261006/`에서 원본 게임 코드를 바꾸지 않고 하위 클래스/시험 사본을 실행했다. parse 오류가 아닌 실제 실패 검사와 exit 1을 확인했다. [대조 실행기](tools/)와 [측정·로그](controls/).

| 사본 변형 | 실제 결과 |
|---|---|
| 일반 `BOSS` 갈래를 새 보스보다 먼저 둠 | `intel_supply` 21검사 실패, exit 1 |
| ORIGIN 키를 공통 표에서 제거 | `intel_supply` 8검사 실패, exit 1 |
| SPORE FILTER 갈고리 비활성화 | `module_expansion` 1검사 실패 |
| FROST LENS 갈고리 비활성화 | 1검사 실패 |
| RAIL SPOOL 두 갈고리 비활성화 | 2검사 실패 |
| ECHO RELAY 갈고리 비활성화 | 1검사 실패 |
| NULL ANCHOR 갈고리 비활성화 | 1검사 실패 |
| RAIL CARBINE의 실제 투사체 피해만 0 | `weapon_expansion` 4검사 실패, 실제 충돌 피해 검사 포함 |
| NULL BREACHER의 실제 투사체 피해만 0 | 같은 4검사 실패, exit 1 |

모듈 양성 검사: 실제 Q/E/X 시전 → 효과 값·debug authority 일치, 두 번 적용해도 한 번, 해제 후 원래 Dictionary, A→기존 B 전환에서 A authority 없음, `MODULE_LOCKED`·`MODULE_INCOMPATIBLE`, 세 연산자 모두 한 문자열 슬롯. 이미 켜진 스킬 버프는 정상 시간 만료에 따르며 로드아웃 변경은 기지 동작이다. 시험은 각각 새 시전으로 측정한다.

무기 양성 검사: 실제 탄 소모·펠릿·총구 중복 제거·투사체 수치·적 충돌 피해·자기 피격 가문, 원본 프로필 불변, 소리 불변, ASTER 그림 투사체 미사용, 기본 무기로 돌아오면 프로필 전체 동일. [무기 측정](records/weapon_expansion.json), [모듈 측정](records/module_expansion.json).

## 3. 상수 표

권장 수치를 바꾼 것은 없다. 새 이름·상수와 기존 기대값 확대를 함께 적는다.

| 파일 / 이름 | 이전 → 이후 | 이유 |
|---|---|---|
| `campaign_progression.gd` `SAVE_SCHEMA_VERSION` | 5 → 6 | 표본·분석 확장 저장 |
| `intel_samples.gd` `KEYS` / 두 기존 `INTEL_KEYS` alias | SECURITY, ABERRANT, ANCHOR → 기존 3 + AERATOR, CRYO, GANTRY, ARCHIVE, ORIGIN | 권위 한 곳, alias로 사용 |
| 같은 파일 `SHORT` | 기존 SEC/ABR/ANC → SEC/ABR/ANC/AER/CRY/GAN/ARC/ORG | 8키 표시 |
| `run_contract_save_smoke.gd` 형식/고정물/행·키 | 5 / v3,v4 / 3키·분석3·무기6 → 6 / v3,v4,v5 / 8키·분석8·무기8 | 옛 행 전체와 상태를 엄격 비교, 새 내용 잠김·0, 나머지 키 전체 equality 유지 |
| `m10_persistence_smoke.gd` 빈 intel | 3키 → 8키 모두 0 | 무손실 옛 저장 |
| `m13_weapon_base_migration_smoke.gd`, `m13_weapon_loadout_smoke.gd` 카탈로그 수 | 6 → 8 | 기존 검사 확대 |
| `m13_weapon_loadout_smoke.gd` 신규 봉투 | 없음 → burst≤100, sustained≤78, 호환 연산자 기존 최고 sustained 이하 | 제안 상한 계산 추가(53검사) |
| `combat_vfx_overhaul_smoke.gd` projectile/hit 표 | 기존 표 → PRJ/HIT_WEAPON_RAIL/NULL 추가 | 기존 예산·중복 제거 유지(189→195검사) |
| `operator_skill_controller.gd` ROOK Bulwark | 5 → 6s, SPORE FILTER 때만 | +1s |
| 같은 파일 ASTER Prism | 4 → 3.2s cooldown, FROST LENS 때만 | -20% |
| 같은 파일 ASTER Vector Dash | 150 → 200px, cooldown 5 → 4s, RAIL SPOOL 때만 | +50px / -20% |
| 같은 파일 MICA Relay Step | 4 → 6s squad guard, ECHO RELAY 때만 | +2s |
| 같은 파일 ROOK Scatter Cycle | cycle/guard 5 → 6.5s, NULL ANCHOR 때만 | +1.5s |
| 같은 파일 `debug_contract` | 기존 필드 + 6개 시간·거리 필드 | 실제 시전과 같은 갈고리 사용 |
| `combat_muzzle_vfx.gd` `LIFE` | 기존 불변 + WEAPON_RAIL 0.09 / WEAPON_NULL 0.12s | 새 코드 가문 |
| `combat_hit_vfx.gd` `FAMILIES` | 기존 불변 + RAIL life .42, radius58, energy .85, style .6, palette b9f7ff/62d9ef; NULL .48/68/.9/1.4, ffd8ed/d68eb5 | 흰 청록 쌍선 / 흰 분홍 세 갈래 |
| `prototype_projectile.gd` `TRAIL_LENGTH` | 기존 불변 + RAIL105 / NULL44px | 별도 코드 몸체 |
| `base_lobby.gd` panel | Rect2(28,500,1224,202) 불변 | 고정 연구소 경계 |
| 같은 파일 분석 쪽 | 3행 고정 → 쪽당3행, 총3쪽(3+3+2) | 옛 첫 3개 순서 불변, 쪽 미저장 |
| 같은 파일 분석/모듈 box·행 간격 | y66/h126/42px → y70/h122/41px | 31px 실제 페이지 버튼과 첫 행 비겹침 |
| 같은 파일 샘플 label | 폭520/13px → 폭570/최대12px, 약어8개 | 모든 표본 수 표시 |
| 같은 파일 헤더/상태/설명 | 헤더 폭788/max13, 상태382/max12, 제목284/max12, 설명306/max10(최소8), 모듈240/max12 | 전체 글꼴 크기로 fit, 설명 생략표 없음 |
| 같은 파일 page controls | 없음 → x600/648/694,y38, 버튼42×24(실제 최소 높이31), <·> / 1–3쪽 | 새 쪽 조작 |
| 같은 파일 module cycle | 기존 각1종 → ASTER3 / ROOK3 / MICA2, EQUIP→NEXT MOD→UNEQUIP | 연산자당 한 칸·빈 문자열 해제 불변 |
| `story_stage_hud.gd` intel box | x858,w398 → x616,w640; font11 불변 | 오른쪽 경계1256 유지, 옛 글 뒤 새 표본 추가 |
| `mission_results.gd` body/epilogue | body font15→14; epilogue y400,h96→y416,h82 | 확보·기지 8키를 두 줄로 보여 겹침 방지 |
| `lab_geometry_smoke.gd` 신규 패널 검사 | exact equality → 거리<0.001px | Godot tween 잔여0.0002px, 논리 경계 변경 없음 |
| 러너 | 52quick/31full → 56quick/32full | 새 quick4개 + headless 캡처1개(120s, --out) |

새 VFX 도형만 추가했다(쌍 가속기 총구 최대50px, 3갈래 총구 최대30px; 새 projectile와 hit 도형). 기존 가문 수치·두 triangle-array 호출의 Painter·tri 예산 불변. 새로운 검사 허용치(모듈 비교 0.001, 글꼴 산출0.01px)는 수치 반올림만 처리하며 기존 감사 기준을 고치지 않는다.

## 4. 데이터 변경과 경제

기존 분석 세 행·무기 여섯 행은 **완전 동일**. 미션·적 체력·보스·계약·업그레이드 가격은 변경하지 않았다.

| 신규 분석 | 표본 비용 / 연구비 | 모듈 / 연산자 | 추가 무기 |
|---|---|---|---|
| ANL_AERATOR_SPORE_PROFILE | AERATOR1 / 140 | SPORE FILTER / ROOK | — |
| ANL_CRYO_COMPRESSOR_MODEL | CRYO1 / 160 | FROST LENS / ASTER | — |
| ANL_GANTRY_RAIL_MODEL | GANTRY1 / 180 | RAIL SPOOL / ASTER | RAIL CARBINE |
| ANL_ARCHIVE_ECHO_MODEL | ARCHIVE1 / 200 | ECHO RELAY / MICA | — |
| ANL_ORIGIN_NULL_MODEL | ORIGIN1 / 220 | NULL ANCHOR / ROOK | NULL BREACHER |

새 다섯 보스는 **처음 쓰러뜨릴 때** 자기 키 1개, enemy_id당 런 한 번이다. 작전1–5 보스는 ANCHOR 그대로. SECURITY/ABERRANT 로봇 갈래도 그대로이고 계약/REDLINE/선택 계약은 표본을 곱하지 않는다. 전멸은 8키 모두 잃고 합계에 센다. 기존 저장 모듈 모양은 `{operator_id: module_id 문자열}` 그대로다.

| 값 | RAIL CARBINE (`WPN_DMR_RAIL_01`) | NULL BREACHER (`WPN_SHOTGUN_NULL_01`) |
|---|---:|---:|
| 호환 | ASTER / MICA | ROOK |
| damage×pellets | 22×1 | 16×3 |
| fire interval / magazine / ammo per trigger | .38s / 12 / 1 | .50s / 5 / 1 |
| reload | 1.40s | 1.90s |
| projectile speed / life | 1320 / .90s | 900 / .62s |
| spread / engagement range | 0 / 660px | .04rad / 340px |
| burst / sustained DPS | 57.8947 / 44.2953 | 96.0000 / 54.5455 |
| 비교 역할 | 더 긴 사거리·빠른 탄속 대신 낮은 지속 DPS | 더 높은 순간 화력·사거리 대신 작은 탄창·낮은 지속 DPS |

`burst = damage×pellets / interval`, `sustained = damage×pellets×(magazine/ammo) / ((magazine/ammo)×interval+reload)`. 기존 최고 sustained ASTER67.8 / ROOK62.7 / MICA61.2 이하. 기존 가문 토큰을 새 id/profile에 넣지 않았다. 새 무기는 손에 든 그림과 두 소리 프로필을 그대로 쓴다.

연구비 추가 합 **900 ≤ 952**. 소비처 연구 5,180→**6,080**, authored income4,088 대비 **1.4873배**(기존 .9–1.5 대역). salvage36/56=.6429, fragments18/28=.6429 불변. ×2 클램프와 LEGACY 첫3레벨 가격 불변. `upgrade_economy`는 수정 없이 225검사 PASS, 가격을 다시 조절할 필요가 없었다.

## 5. 네이티브 캡처

명령: `Godot --path . --log-file .cache/diag/expansion_item3_20261006/native_engine.log -s res://tests/render/expansion_item3_capture.gd -- --out=res://.cache/diag/expansion_item3_20261006/native`.

실제 1920×1080 viewport의 PNG 7장, resize 없음, native 검사16 PASS. headless 러너는 PNG를 만든 것으로 세지 않고 fixture metadata/실제 trigger의 2검사만 수행한다. [캡처 설명·원래 해시](captures/capture_report.json). fixture stock과 멈춘 게임 장면이다. 두 VFX 화면은 실제 발사 후 **탄 비행·피격 위치를 배치한 기술 합성**이며 실제 충돌이나 사람 플레이 캡처가 아니다(충돌은 별도 액터 시험으로 확인).

| PNG 경로 / 장면 | SHA-256 |
|---|---|
| [lab_page1.png](captures/lab_page1.png) — 기존 분석 3개 첫 쪽 | `44ffe63c5ca0fd38f5ce5930aac636add69294fefd8e33de95c196969834007f` |
| [lab_page3.png](captures/lab_page3.png) — 새 분석 마지막 쪽 | `239164b728975153f253fb29abaa7c7d9b7bdc8798bb8f60d10b62044091f97d` |
| [lab_module_cycle.png](captures/lab_module_cycle.png) — 실제 모듈 순환 뒤 | `6a5c19f07f7296af71e4f29a41b1db98d6e09ae7d4927ce2dc98a05bf7342deb` |
| [field_intel8.png](captures/field_intel8.png) — 8키 cargo HUD | `680dbf1c94f31a5ad11311072202d27b27b41cdd13349ad3ab1e0d3f952101d3` |
| [vfx_wpn_dmr_rail_01.png](captures/vfx_wpn_dmr_rail_01.png) — RAIL 코드 VFX 고정 장면 | `6a406af0b278730b3219c17265194ee28cb718ac280584969ddd9636246c5765` |
| [vfx_wpn_shotgun_null_01.png](captures/vfx_wpn_shotgun_null_01.png) — NULL 코드 VFX 고정 장면 | `5ec7386985cdd2d4cc6cb8dcea78e245c0297e4dd5514b8d5da224f01aced37f` |
| [results_intel8.png](captures/results_intel8.png) — 8키 확보·기지 결과 | `5df7572da2bb796841c1dcb097d8af06e3c873d95a54324076a15c9e947733f3` |

검증 명령: `python tools/art_pipeline/validate_visual_evidence_1080p.py <위 PNG 7장> --require-dynamic-capture --output qa/expansion_item3_20261006/records/visual_validation.json`. **7/7 PASS**([JSON](records/visual_validation.json)). 이는 이미지 해상도·decode 컨테이너 검사이며 품질/그림 승인이 아니다. 직접 확인에서도 모든 분석 제목·비용·효과와 모듈명이 읽히고, 마지막 쪽·버튼·HUD·결과 글이 잘리거나 겹치지 않았다. 로봇/연산자 그림은 착색하지 않았다.

## 6. FPS

FPS 측정·같은 세션 회전 A/B는 **실행하지 않았다**. FPS 유지나 향상을 주장하지 않는다. 기존 Painter를 그대로 쓰고 각 효과의 삼각형 수·가문·자기 해제·중복 제거를 시험했다. 성능 수치가 필요한 검수는 Claude의 같은 세션 회전 A/B로 남는다.

## 7. 알려진 한계와 정리

- 모듈·무기·연구비는 9.13 권장값이며 사람 플레이를 거치지 않은 제안이다. 효과 수치 커밋 `4ab13d7a`, 무기 수치 커밋 `c83ddf6c`로 나눴다. 유지/수정 결정은 사용자에게 있다.
- **전체 full은 실행하지 않았다.** 요청대로 전체 스위트는 별도 검수로 남기고, 실제 플레이·균형 검수도 남아 있다. 직전 항목 검수에서 알려진 작전6·10 봇 WIPED 위험은 이번에 봇 한 판을 새로 돌려 비교하지 않았고 완화하지 않았다.
- 기존 러너 밖 `tools/validate_m10_intel_contract.py`는 기준선부터 FAIL인 도구(9.13.4)라 수정·실행하지 않았다. 이를 PASS로 세지 않는다.
- 첫 직접 import 진단에서 기존 `fps_bgm_06_sniper_ridge.wav`의 비RIFF 헤더 오류를 관찰했다. 음악·원화는 고치지 않았다. 이후 정식 러너 import와 지정 시험의 실제 결과는 위 표와 같다. 기존 기계 PNG 직접 로드 경고도 별도로 보존했다.
- 논리 1280×720의 글꼴 지오메트리와 네이티브 1080p 화면을 검사했으나 다른 DPI/언어/창 크기의 전체 시각 검수를 대신하지 않는다.
- 플레이어 저장/설정은 시험에서 쓰지 않았다. 모든 `CampaignProgression` 저장 시험은 `--out` 프로젝트 경로, GameFlow UI 시험은 `persist_campaign=false`를 썼다.
- 증거 사본의 SHA를 확인한 뒤 현재 작업의 중복 캡처·대조 실행 사본과 일회성 편집 초안 105개(18.9 MiB)를 지정된 `.cache` 폴더에서 삭제했다. 최종 PNG·측정·소스·로그는 이 QA 폴더에 남긴다. 실제 삭제 범위와 해시는 [정리 기록](records/cleanup_manifest.json)에 기록했으며 다른 세션 자료·원본 자산·옛 항목 자료는 포함하지 않는다.

## 8. 승인 범위

**이 기록은 그림·플레이·균형 승인이 아니다.** 항목 3 구현을 보고하고 멈춘다. Claude의 검수 뒤 사용자 지시 전에는 항목 4·5·1D를 시작하지 않는다.
