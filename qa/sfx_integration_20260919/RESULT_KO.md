# R04 전투 SFX 앱 연결 — 2026-09-19

상태: 로컬 앱 연결 및 기술 검증 완료. 원격 배포 없음. 사람의 청감 승인이나 전체 에셋/MVP 완료를 의미하지 않음.

## 반영

- 사용자 제공 R04 ZIP의 SHA-256, CRC, 120개 기본 WAV 및 3개 소스 파일 해시를 확인하고 원본 전체를 프로젝트 안에 보존했다.
- 기본/스테레오 대안 132개 중 12개 이벤트 역할 × 2종 = 24개를 선별했다. 선택 근거와 원본/파생 파일 해시는 `selected_bank_manifest.json`에 기록했다. 청감 입력 도구가 지원되지 않아 들었다고 주장하지 않으며, 기술 상태·주파수 특성·역할 적합성으로 선별했다. 미선택 음원은 삭제하지 않았다.
- ASTER/ROOK/MICA, 적 발사, 피격, 보스 바닥/십자 공격 및 사망에 연결했다. 발사 수·대미지·보행·조준·캐릭터 배율은 변경하지 않았다.
- ROOK 산탄과 보스 부채꼴은 발사체마다 중복 발사음을 내지 않는다. 서로 다른 공격자는 같은 프레임에도 재생 가능하다.
- 최대 20보이스, 일반음 16보이스 제한과 중요 폭발음 우선순위, 0.8초 일반음 덕킹, 별도 전투 버스 리미터를 적용했다. 원음의 피치/길이/루프는 변경하지 않았다.
- 잔향은 공격자 삭제 후에도 해당 전투 씬이 보존하며, 실제 GameFlow의 전투→타이틀 전환에서는 제거된다. 보스 사망음은 사망 경계에서 한 번만 재생된다.
- Michel Baradari 폭발음 CC BY 3.0 출처·라이선스·수정 고지 및 CC0 출처를 타이틀 `SOUND CREDITS`와 `assets/audio/combat_r04/CREDITS.txt`에 넣었다. 원문 라이선스는 인앱 브라우저로 확인했다.

## 실제 검증

- `combat_sfx_r04_smoke.gd`: PASS, 187검사. 선택 PCM 바이트/채널, 기존 프로필 전체 연결, 실제 캐릭터 발사, 변형 교대, 재장전 중 무음, 보스 팬 중복 억제, 경고/피해 경계, 사망 1회, 꼬리 보존, 보이스 제한, 실제 화면 전환과 크레딧 포함.
- `site7_emission_owner_smoke.gd`: PASS, 339검사. 기존 30/60/120Hz 적 발사체 생성 회귀.
- `site7_battle_flow_smoke.gd`: PASS. 스테이지 1~3, 연습전 전환·초기화·타이틀 복귀·보상 상태 유지.
- 공유 Actor 발사 경계 변경 후 추가 회귀: `site7_drone_app_smoke.gd` 170개, `site7_anchor_app_smoke.gd` 271개, `site7_machine_source_smoke.gd` 436개, `rook_motion_lab_app_smoke.gd` 1,895개 모두 PASS. `motion_lab_character_runtime_smoke.gd`도 PASS. 검사별 원본 로그를 같은 폴더에 보존했다.
- 실제 앱 보스 연습전: 정상 AI/대미지, 입력 주입, 발사체 90개. 10초 엔진 출력 녹음에 세 캐릭터 발사·피격·보스 바닥/십자 공격음이 포함됐다. 사망음은 이 10초 플레이에서 발생하지 않았으며 별도 실제 사망 경계 smoke로 검증했다.
- 녹음 PCM: 48kHz 스테레오, peak −7.998dBFS, 4배 보간 추정 true peak −7.940dBFS, 클리핑 샘플 0, 실제 최대 16보이스. 후반 작업으로 SFX를 덧붙이지 않았다. `mix_validation.json` 참고.
- `battle_sfx_0030/0240/0540.png`: 네이티브 1920×1080, 컨테이너 검증 PASS. 미술 승인 아님.
- MovieWriter의 `battle_native.avi`는 엔진 기본 1280×720 영상에 실제 48kHz 소리를 기록한 **음성 추출용 중간물**이며, 1080p 영상 증거나 완성 영상으로 제출하지 않는다. 1080p 정지 캡처는 별도 실제 viewport 원본이다.

## 재현

1. `tools/audio/intake_sfx_r04.py`: 원본 검증 및 PCM 진단.
2. `tools/audio/build_combat_sfx_bank.py`: 프로젝트 QA의 PCM16 중간물 및 런타임 레지스트리 준비.
3. `tools/audio/import_selected_sfx.gd`: Godot로 선택한 24 WAV만 `.res` 직렬화.
4. 빌더를 다시 실행해 최종 `.res` 해시 기록; smoke/회귀 재실행.

런타임에는 약 7.3MB의 선택된 AudioStreamWAV `.res`만 들어간다. WAV 중간물과 전체 ZIP/오디션은 QA/원본 폴더에 두고 `.gdignore`로 엔진의 불필요한 전체 가져오기를 피했다. 레지스트리가 `.res`를 명시적으로 preload하므로 패키지 종속성에 포함된다. 전체 저장소 editor import는 방대한 과거 에셋 스캔으로 중단하고 선택 파일만 직렬화했다. 진단에서는 `--audio-driver Dummy`를 명시해 장치 초기화 지연 없이 검증했으며, 런타임 사용자 오디오 장치 설정은 변경하지 않았다.

게임 상태를 바꾸지 않는 실제 믹스 미리듣기: `sable_combat_r04_actual_mix_10s.mp3` / 무손실 PCM `.wav`.
