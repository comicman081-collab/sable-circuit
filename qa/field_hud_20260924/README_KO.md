# 목업 기반 전투 HUD — 2026-09-24

사용자 요청: "내가 만들고 싶던 게임 목업이미지야... 비슷하게 구현해봐. 작업은 계속
진행하면서 추가해". 목업 이미지: 세션 첨부(프로젝트 파일 아님).

## 목업과의 대응
| 목업 | 구현 |
|---|---|
| 좌상단 `CH01 BLACKOUT AT SITE-7` + 기울어진 입체 미니맵, `+`/`-`/`M` | 작전명 헤더, 실제 바닥 윤곽을 기울여 두께를 준 미니맵(현재 방 강조, 분대·적 점, 목표 마름모). 기본은 분대 주변 확대, `M` 전체/확대 전환, `+`/`-` 배율(키·클릭). |
| `OBJECTIVES` 주목표(주황 마름모) + 하위 목표 | 현재 목표 + 작전별 선택 방 2개(회수 시 녹색) |
| 우상단 자원 아이콘 줄 + `TAB` | 톱니(회수 부품)·보라 육각(신호 조각)·파란 마름모(정보 샘플)·금색(연구 자원) + TAB(조작 안내 열기) |
| 하단 좌측 분대 카드(번호·초상화·이름·HP·10칸 바·무기) | 동일 구성, 조작 중 카드 청록 테두리·발광 |
| 하단 중앙 `ENERGY` 바 `100/100` | 동일(가득 차면 금색) |
| 하단 우측 무기 아이콘·탄약·무기명·탄창 버튼, 스킬 `Q`/`E`/`R` | 무기 아이콘·탄약/탄창·무기명·장전 버튼(클릭 시 장전, R키). 스킬 칸은 게임 규칙상 Q/E/X(R은 장전)로 유지, 쿨다운 음영. |
| 캐릭터가 화면에서 차지하는 크기 | 기본 카메라 배율 1.46 → 1.22(분대 약 23% 높이), 보스 1.02 → 0.86(기존 비율 유지) |
| 깔끔한 상단 | 조작 안내를 작은 반투명 한 줄로, MANUAL/TOUCH 버튼 소형화, 전투 무전은 내용 길이에 맞춰 늘어나는 상자 |

게임 규칙 차이: 목업의 `R` 스킬 칸은 이 게임에서 장전 키라 `X`(궁극기)로 두었다.
탄약은 이 게임에 예비탄 개념이 없어 `/탄창 크기`로 표시한다.

## 파일
- `scripts/ui/story_stage_hud.gd` 재작성(공개 API·디버그 계약 유지)
- 신규 `scripts/ui/hud_widgets.gd`(자원 아이콘·키 배지·분할 바·탄창 아이콘)
- `scripts/ui/tactical_minimap.gd` 재작성(기울어진 입체 미니맵, 배율)
- `scripts/ui/demo_controls.gd`: 상단 안내·버튼 소형화, TAB=조작 안내
- `scripts/missions/squad_camera_presentation.gd`: 배율 1.22 / 보스 0.86
- 신규 `tests/render/field_hud_capture.gd`(1080p 캡처)

## 검증
PASS: m9_operator_skill_synergy(HUD 스킬 계약), rook_motion_lab_app(1895, 초상화),
m5_font, demo_integration_check(26), site7_cover_ai_check(46), site7_battle_flow,
site7_campaign_progression(94), motion_lab_character_runtime, field_hud_capture.
m7_authored_visual_smoke: 보스 배율 차이 검사는 0.86 조정 후 해결. 남은 3개(보스 카메라
포커스)와 m2_story_flow 1개는 이번 작업 전부터 실패하던 항목(수정 전 코드에서도 동일).
1080p 캡처 7장 `visual_evidence_check.json` 컨테이너 PASS — 아트 승인 아님.
