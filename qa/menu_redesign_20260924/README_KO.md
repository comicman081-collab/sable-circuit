# 타이틀·메뉴 화면 리디자인 — 2026-09-24

사용자 요청: "타이틀부터 메뉴 화면이 너무 구리니 웅장하고 멋지게".

## 원칙
새 원화나 로컬 생성 모델은 쓰지 않음. 이미 프로젝트에 있는 승인 에셋만 사용하고,
그 위에 연출(그레이딩, 광원, 먼지, 타이포, 애니메이션)만 코드로 얹음.
- 배경: 기존 Site-7 방 배경(타이틀 = `stage03/anchor_remnant`, 좌우 반전)
- 라인업: Motion Studio 아이들 프레임(ASTER S / ROOK SE / MICA SW), 픽셀 무수정
- 초상화: 기존 `portrait_asset` + `portrait_region`

## 화면
- 타이틀: 대형 글로우 로고, 번호형 메인 메뉴(시작/빠른 출격/기지/훈련),
  오퍼레이터 라인업(림 라이트·스캔·호흡·백라이트), 캠페인 진행도, 훈련 패널 분리,
  켄 번스 이동 + 마우스 패럴랙스, 등장 연출, 필름 그레인, HUD 프레임.
- 기지: 배경·유리 패널·섹션 헤더, 오퍼레이터 색상 카드, 선택 작전 배경 이미지,
  강조된 브리핑 버튼. 테스트 훅(`MissionSelector`, `WeaponCycle_*`,
  `Portrait_*`, ANALYZE/EQUIP 텍스트, 시그널) 유지.
- 브리핑: 작전 배경, 방 유형 태그가 붙은 경로 타임라인, 화자 초상화 + 타자기
  효과 통신, 진행 표시, 발광하는 출격 버튼.
- 디브리핑: 결과별 색조, 확보 자원 카운트업 타일, 세로 결과 스탬프.
- 공용 테마(`demo_theme.gd`): 챔퍼 모서리 버튼·포커스 글로우·다이얼로그·
  드롭다운·툴팁. 크기/여백은 기존과 같아 게임 내 일시정지 패널도 그대로 맞음.

## 새 파일
`scripts/ui/menu_fx.gd`, `menu_backdrop.gd`, `menu_atmosphere.gd`,
`cinematic_menu_button.gd`, `operator_lineup.gd`,
`tests/render/menu_redesign_capture.gd`.
웹 빌드는 `tools/environment/build_sites_demo.py`가 타이틀용 원본 아이들
아틀라스 3장을 팩에 포함(약 0.6MB).

## 증거
`01_title.png` ~ `07_pause_manual.png`: 네이티브 1920×1080 캡처
(`menu_redesign_capture.gd`, 14 checks PASS). `visual_evidence_check.json`은
컨테이너/디코딩 PASS일 뿐 아트 승인이 아님. 사람 플레이테스트 아님.

## 회귀
PASS: m2 흐름의 메뉴 구간, m10_base_ui_action, m13_weapon_base_migration,
site7_battle_flow, site7_campaign_progression(94), rook_motion_lab_app(1895),
demo_integration_check(26). 로컬 웹 빌드에서 타이틀 → 브리핑 → 출격 확인.
