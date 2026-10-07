# MICA Motion Studio 01

2026-09-19 최신 범위: 인간형은 플레이어만 제작합니다. `site7_rifle`을 포함한
모든 인간형 몹은 제작·앱 연결에서 제외했으며 예전 재개 패킷으로 복구하지 않습니다.
현재 적은 검증된 드론과 고정 보스이고, 지형물은 사용자 지정 kArchive 자산을 재사용합니다.

새로 만든 독립 캐릭터 모션 실험실입니다. `dist/MICA_Motion_Studio.html`을 브라우저에서 열면 실행됩니다. 이미지, 글꼴, 조작 코드가 HTML에 포함되어 있습니다. 서버와 인터넷 연결은 필요하지 않습니다.

개발 화면은 이 폴더에서 `python serve.py`로 실행한 뒤 `http://127.0.0.1:14821/`에서 엽니다. 다른 캐릭터는 `/?character=캐릭터_id`로 선택합니다. 기존 게임과 이전 제작 파이프라인의 포인터는 변경하지 않았습니다.

## 조작

| 입력 | 동작 |
|---|---|
| WASD / 방향키 | 8방향 이동, 두 키를 함께 누르면 대각선 |
| Shift | 달리기 속도 |
| 마우스 | 이동과 별도로 조준 |
| 좌클릭 / Space | 사격, 누르고 있으면 연사 |
| R | 재장전 |
| 오른쪽 방향 버튼 / ■ | 지속 이동 / 정지 |
| 교전 시작 | 표적의 반격 활성화 |
| 8방향 모션 | 같은 시간의 8개 방향 비교 |
| 프레임 검토 | 큰 원화 확인, 총구 위치 수정 |

대각선은 **W+A 좌상 / W+D 우상 / S+A 좌하 / S+D 우하**입니다. 방향키도 같은 조합으로 동작합니다. 한글 입력 상태와 Shift를 누른 상태에서도 물리 키 위치를 사용합니다. 기본 설정에서는 사격 중에도 새 이동 키를 누르면 진행 방향을 바라보고, 다음 마우스 움직임이 다시 독립 조준을 가져옵니다. 키 반복은 조준을 빼앗지 않습니다. 실제 총구와 조준점을 반영한 하나의 조준 결과를 몸과 탄환이 함께 사용합니다. 무기보다 가까운 곳을 조준해도 탄환만 몸 뒤로 꺾이지 않습니다.

## 이번에 실제로 들어간 것

- MICA 8방향 보행 원화 48장과 정지 사격 자세 8장. 새 Codex ImageGen 원화에서 추출한 총 56프레임입니다.
- 1024×1536 단독 원화와 1536×1024 두 인물 원본을 보존합니다. 두 인물 원본은 각 캐릭터 윤곽을 분리해 총구가 칸 경계에서 잘리지 않도록 처리했습니다.
- 프레임 셀은 768×768, 캐릭터의 기준 높이는 656픽셀입니다. 기본 전투 화면에서는 270픽셀 높이로 표시합니다. WebGL 2에서는 밉맵으로 축소 시 깜빡임을 줄입니다.
- 보행 위상은 실제 이동 거리에 연결됩니다. 정지, 충돌, 방향 전환, 속도 전환과 카메라 추적을 같은 컨트롤러로 처리합니다.
- 방향별 총구, 상체 반동, 탄환 이동, 표적 피격·파괴·재생성, 탄창·재장전, 플레이어 피격이 연결되어 있습니다. 짧은 클릭도 다음 물리 스텝에 한 번 전달합니다.
- Blender에서 프로젝트의 UAL1 동작을 읽어 관절 샘플과 8방향 포즈 가이드를 만들었습니다. 화면에 보이는 MICA는 ImageGen 원화입니다. Tripo와 VRoid의 외형을 MICA로 바꿨다고 주장하지 않습니다.

## 구현 범위와 남은 품질 차이

이 패키지는 **조작 가능한 독립 시제품**입니다. 양산 품질을 자동 보장하는 도구로 판정하지 않았습니다.

현재 달리기는 보행 원화의 재생 주기와 이동 속도를 바꿉니다. 독립적인 달리기 원화는 아직 없습니다. 옆걸음은 조준 방향의 보행을 사용하고, 후진은 위상을 거꾸로 재생합니다. 8×8 이동·조준 입력을 지원하지만 64개의 별도 신체 동작을 그렸다는 뜻은 아닙니다. 재장전은 게임 상태와 작은 무기 기울임으로 표현하며 탄창을 교환하는 손동작 클립은 없습니다.

각 방향의 6프레임은 전부 실제 원화이지만 얼굴·소총·파우치 형태에 프레임 간 편차가 남아 있고, 일부 옆·뒤 방향의 좌우 발 구분도 추가 보완 대상입니다. 확대 화면과 `qa/mica_8dir_walk.gif`에서 직접 비교할 수 있습니다. 이 문제를 광학 흐름이나 분절된 다리 변형으로 감추는 경로는 사용하지 않습니다.

## 새 캐릭터 제작·수정 및 Luna 인계

2026-09-13 최신 원화 규칙: 신규/교체 원본은 실제 RGBA PNG, 배경 알파 0,
가시 영역 알파 1~255, 불투명한 내부를 요구합니다(2026-09-28 사용자 지시로 알파 255 기본 허용). 초록 배경 생성·그린 재시도는
중단했습니다. `source_alpha_policy.py --source 실제원본.png`와 intake/review가
반환 원본의 채널과 알파를 검사하며, 알파를 강제로 바꾸거나 키잉한 결과로
네이티브 투명 생성을 대신하지 않습니다. 숫자 PASS 이후에도 양쪽 매트에서
원화 품질을 확인합니다. 기존 승인 원화·과거 그린 원본과 검증 근거는 보존됩니다.
ImageGen에 전달하는 외형 원본과 포즈 가이드는 이 SABLE 저장소 안의 경로만
허용합니다. `source_alpha_policy.require_project_reference`와 handoff 검사가
다른 프로젝트, Codex 관리 스테이징, 클립보드 및 잠긴 구형 도구 경로를 차단합니다.

사용자가 명시적으로 허용한 경우에만 native-alpha 실패 원본 하나를
`web_alpha_bridge.py`로 격리해 기존 GPT 웹 대화에 투명 변환을 요청할 수
있습니다. 브리지는 원본을 키잉·크롭·수정하지 않으며, 웹에서 돌아온 파일도
실제 RGBA 알파 검사를 통과하기 전에는 intake·승인·런타임 연결을 하지 않습니다.

2026-09-13 보행 실패 차단: [전체 주기 검토 절차](../.agents/skills/sable-character-studio/references/cycle-review.md)가 추가됐습니다.
`status`는 소스 완비(`sourcesReady`), 주기 검토, 활성 빌드 가능 여부와 런타임 거절을 구분합니다.
`prepare-cycle`로 E 한 주기 증거를 만들고 실제 관측으로 `review-cycle`을 통과한 뒤 다른 방향으로 확대합니다.
각 방향 주기 승인 없이 compiler 직접 호출로 활성 아틀라스를 교체할 수 없습니다.
최종 승인에는 `prepare-runtime-review`의 영상 시간대별 관측 파일을 `--observations`로 전달해야 합니다.
ROOK의 사용자 거절 빌드는 역사적 HOLD로 보존됩니다. 2026-09-13 Astra가 실제 원화·주기·런타임 영상을 다시 검토한 새 빌드 `334814808cdfadc0…`는 별도 MVP 전달 승인을 받았으며, 현재 앱에도 연결됐습니다. 정확한 현재 상태는 `qa/rook/astra_repair_20260913/RESULT_KO.md`, `dist/rook.delivery.json` 및 저장소 루트 `AGENTS.md`의 현재 앱 연결 기록을 확인합니다. 이 승인을 과거 거절 빌드나 독립 질주 원화, 실행하지 않은 Luna 재현 결과로 확대하지 않습니다.

현재 프로젝트 공통 절차는 저장소 루트의 [sable-character-studio 스킬](../.agents/skills/sable-character-studio/SKILL.md)입니다. [제작 명령](../.agents/skills/sable-character-studio/references/authoring.md)과 [브라우저 검증](../.agents/skills/sable-character-studio/references/browser-check.md)에 실제 실행 순서를 정리했습니다. 이전 하네스는 사용하지 않습니다.

새 캐릭터는 원화 참조와 캐릭터 이름을 받은 뒤 시작합니다. `new_character.py`가 레시피와 필요한 슬롯을 만들고, `character_workflow.py status --character ID`가 현재 누락·미검토·변경된 슬롯 및 다음 작업을 알려줍니다. 기본 보행 48장과 대기 8장이 필요하며, `--run-art`를 지정한 경우에만 별도 달리기 48장을 추가합니다.

2026-09-12부터 `character_workflow.py handoff --character ID`로 실제 다음 수정 슬롯과 입력 해시가 담긴 재개 패킷을 만듭니다. 출력된 파일을 `verify-handoff --packet PATH`로 확인한 뒤 사용하며, 원화·코드·검토가 바뀌면 다시 생성합니다. 알려진 `repair` 슬롯이 우선입니다. [개선 사항 재사용 절차](../.agents/skills/sable-character-studio/references/reuse-improvements.md)에 공용 무손실 패킹, R3 근거 검증 및 실패를 합격으로 바꾸지 않는 검사 명령을 정리했습니다. 패킷은 Luna 실행이나 캐릭터 완성 기록이 아닙니다.

먼저 E 대기와 양쪽 접지 보행 원화를 실제로 확인한 뒤 나머지를 만듭니다. 실제 ImageGen 반환 메타데이터를 보존하고 `intake_frame.py --tool-response`로 가져옵니다. 각 슬롯은 실제 원본을 보고 `review-source`로 기록합니다. 이 검사는 새로운 원화나 바뀐 참조에 과거 승인을 재사용하지 못하도록 합니다. 실패 파일은 보존됩니다.

모든 요청 슬롯이 준비되면 다음 명령으로 빌드·패키징합니다. 아래 ID는 실제 요청받은 캐릭터로 바꾸며, 설치된 환경은 읽기 전용으로 사용합니다. TEMP/TMP는 이 실험실 아래에 둡니다.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' character_workflow.py build --character ID
& 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' package_standalone.py --character ID
```

아틀라스 빌드는 후보 폴더에서 끝낸 후에만 해당 캐릭터의 개발 아틀라스로 교체합니다. 중간 실패와 부분 빌드는 기존 버전을 건드리지 않습니다. 새 단독 프레임 캐릭터의 초상화도 자신의 컴파일된 전면 프레임에서 만듭니다.

결과는 `dist/ID_Motion_Studio.html` 및 `public/standalone/id.html`, 보고서는 `dist/id.package.json`에 저장됩니다. 다른 캐릭터를 만들었다고 현재 `standalone.html`을 바꾸지 않습니다. 그 공통 미리보기의 교체가 요청된 경우에만 `--activate-preview`를 붙입니다.

브라우저의 `/standalone/id.html`에서 실시간 조작을 확인하고 `public/qa/combat-checks.js`의 기존 17개 이동 사격과 급회전 16개 시나리오를 실행합니다. 그 실제 보고서로 검증합니다. [조준 지연 계약](../.agents/skills/sable-character-studio/references/aim-response.md)은 입력 직후·첫 화면·첫 발사 가능 시점의 최신 조준을 확인하며, 보행이나 연사력 변경 및 이미 발사된 탄환의 유도 전환을 금지합니다.

```powershell
& 'C:\AI_ENVS\pair_pipeline_env\Scripts\python.exe' character_workflow.py verify-runtime --character ID --browser-report 'qa/ID_combat_browser.json' --locomotion-report 'qa/ID_locomotion_browser.json'
```

검사 결과의 캐릭터·소스·런타임·검사 코드가 현재 패키지와 다르면 다시 검사해야 합니다. 새 캐릭터의 최종 전달에는 별도의 실제 1080p 시각 검토 기록과 `deliver` 확인이 필요합니다. 현재 MICA의 과거 쌍 원화 자료는 새 개별 승인 이력으로 꾸며 쓰지 않습니다. 입력·사격 코드만 고치는 작업에는 기존 원화를 다시 만들지 않습니다.

[실제 준비 상태와 한계](qa/WORKFLOW_READINESS_2026-09-10.md)에 검사 범위를 구분했습니다. 실제 Luna 신규 캐릭터 생성은 아직 수행하지 않았으며, 루틴과 검사 체계가 그 결과를 대신하지 않습니다.

## 파일 안내

| 파일 | 역할 |
|---|---|
| `characters/mica.json` | MICA 크기·속도·무기·총구 보정 레시피 |
| `build_guides.py` | Blender UAL 관절과 가이드 내보내기 |
| `reference/ual_guides/motion_tracks.json` | 실제로 추출한 관절 샘플 |
| `art/`, `derived/` | 원본과 분리한 캐릭터 이미지·출처 |
| `build_character.py`, `build_atlas.py` | RGBA 분리, 기준점 배치, 무손실 아틀라스 |
| `public/keyboard-input.js` | 한글/영문 공통 키 입력, 대각선 조합, 키보드·마우스 방향 우선순위 |
| `public/combat-aim.js` | 몸 방향과 탄환에 공통으로 적용하는 조준각 |
| `character_workflow.py` | 소스 슬롯·검토·빌드·실행 검사·전달 |
| `public/qa/combat-checks.js` | 실제 마우스 버튼을 누른 이동 사격 회귀 검사 |
| `public/simulation.js` | 프레임률과 렌더러에 독립적인 조작 로직 |
| `public/atlas-renderer.js` | 원화 표시와 총구에 공통으로 적용하는 반동 |
| `public/studio.js` | 같은 조작 로직을 쓰는 전투·방향 비교·검토 UI |
| `validate_character.py` | 누락, 중복 픽셀, 잘림, 알파, 출처, 총구의 기술 검사 |
| `package_standalone.py` | 서버 없는 한 파일 HTML 패키징 |
| `qa/` | 실제 검사 결과와 원화·실행 증거 |
| `.agents/skills/character-motion-studio/SKILL.md` | 다음 작업자가 읽을 새 절차 |

초기 실험의 `public/app.js`, `public/motion.js`, `public/renderer.js`, `prepare_character.py`와 `experiments/`는 최종 HTML에서 사용하지 않습니다. 삭제하지 않고 실패한 접근의 참고 자료로 보존했습니다. 새 프로젝트 스킬은 성공한 Motion Studio 경로를 안내합니다. 과거 하네스는 재사용하지 않으며, 실제 Luna 캐릭터 생성 재현은 아직 실행하지 않았습니다.
