# 그림 승인 기록 — 게임이 그리는 그림 251장 (2026-10-07)

작성 2026-10-07 · 작성자 Claude · 승인 시점의 게임 커밋 `8218ee76`

## 결론: 사용자가 "그림은 승인할께"라고 답했고, 그 범위를 게임이 그리는 PNG·WebP 251장으로 묶었다

2026-10-06 밤 보고에서 나는 게임을 나눠 줘도 되는 수준인지 묻는 질문에 "닫힌 시험은 되고 공개는 아직"이라고 답하며, 그 이유의 하나로 "기록된 그림 승인은 작전 10뿐"이라는 점을 들었다. 사용자는 2026-10-07에 방 규칙 배치를 받아들이고 Windows 앱은 아직 만들지 않겠다고 한 뒤 "그림은 승인할께 우선 여기까지 만하고 깃허브에 배포해줘"라고 답했다. 범위를 목록으로 지정하지는 않았다. 그래서 "게임이 그리는 그림 전부"로 읽고, 승인 시점의 바이트를 SHA-256으로 묶었다. 사용자의 뜻이 더 좁거나 달랐다면 이 기록을 고친다.

이 승인은 그림에 대한 것이다. 균형·플레이·소리·효과의 승인이 아니다.

## 묶인 것 (`approved_art.json`, 251장, 약 350 MiB)

| 종류 | 장수 | 내용 |
|---|---|---|
| 판 | 150 | 작전 1–10 각 15장(방 6, 선택 방 2, 연결 7), `assets/environments/site7_v2/stageNN/*/*_GAME.png` |
| 보스 | 10 | ANCHOR · RELAY SENTINEL · RESONANCE REMNANT · FORGE WARDEN · CARRIER · AERATOR TOWER · CRYO COMPRESSOR · SIGNAL GANTRY · INDEX SPIRE · ORIGIN CORE (`assets/enemies/…`) |
| 일반 로봇 | 34 | BULWARK 8 · CINDER RAM 8 · PRISM SKIMMER 8 · RECON DRONE 8 · NULL PYLON 1 · VESPER MORTAR 1 |
| 대원 | 51 | ASTER · MICA · ROOK의 모션 스튜디오 아틀라스, 각 17 (`motion_lab_v1/public/assets/atlas/…`) |
| 소품·로비 | 5 | 엄폐물 4종(barrier · cabinet · crate · generator)과 기지 로비 판 `S02_07` |
| 투사체 | 1 | ASTER 코일 투사체 |

범위는 `git ls-files`가 보여 주는 `assets/`와 `motion_lab_v1/public/assets/atlas/`의 `.png`·`.webp` 전부다(게임이 실제로 읽는 폴더와 같다). 파일마다 경로 · SHA-256 · 바이트 수 · 크기 · 모드를 적었다.

## 묶이지 않은 것

- 균형과 플레이. 열 개 작전을 사람이 해 본 기록이 없다(`playtest_logs/`가 비어 있다).
- 소리 · 음악 · 도입 영상.
- 코드로 그린 효과(타격 · 총구 불꽃 · 폭발 · 장판 · 정예 고리 · 분위기 빛 · 심연 배경).
- `assets/` 아래의 SVG 아이콘과 쓰지 않는 SVG 자리표시(은퇴한 인간형 적 세 종 포함).
- 게임이 그리지 않는 원본·작업 그림: `art_src/`, `motion_lab_v1/art`·`reference`·`derived`·`cinematics`, 모션 스튜디오 웹 앱(`motion_lab_v1/public`의 `atlas` 밖), `qa/`의 증거 이미지.
- 승인 뒤에 추가되거나 바뀐 그림. 그것은 사용자가 보지 못한 새 그림이다.

## 작전 10의 이전 승인과의 관계

`qa/site7_op10_art_approval_20261002/`의 17개 파일 가운데 런타임 16개는 이 목록 안에 같은 해시로 들어 있다. 17번째인 ORIGIN CORE 원본 마스터(`motion_lab_v1/art/site7_enemies_raw/origin_core_master.png`)는 런타임 파일과 바이트가 같고 이 목록의 범위(런타임 폴더) 밖이라 그 기록이 계속 덮는다. 그 기록은 그대로 둔다.

## 확인하는 법

```
python qa/art_approval_20261007/tools/verify_hashes.py
```

승인된 파일이 모두 있고 해시가 같으면 종료 코드 0, 하나라도 없거나 바뀌었으면 1이다. 바뀐 것은 게임 오류가 아니라 사용자가 보지 못한 새 그림이다(재생성 · 재노출 · 편집). 승인 목록에 없는 새 그림은 `NEW`로 나열하며, 그림을 추가했다고 실패하지는 않는다. 이 도구는 파일을 읽기만 한다.

## 이 기록이 하지 않는 것

그림이 마음에 든다는 판단을 대신하지 않는다. 사용자의 말을 바이트에 묶어 두는 기록일 뿐이며, 이후 어느 그림이든 다시 만들거나 고치면 그 파일은 다시 승인을 받아야 한다.
