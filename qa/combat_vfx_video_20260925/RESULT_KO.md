# 피격 이펙트 이식 후 실제 소리 포함 전투 영상 — 2026-09-25 (WP-4)

`tools/environment/record_stage_battle_with_audio.py`로 녹화했다
(`SABLE_CAPTURE_ROOT=qa/combat_vfx_video_20260925`, `SABLE_CAPTURE_MISSIONS=1`).
대상 커밋은 dfad7621b(피격 이펙트·반응·흔들림)와 d7b14008c(엄폐물 텍스처 축소)이다.

- `video_112346/stage1/stage1_combat_10s_sound_1080p.mp4`
  - 작전 1(MIS_CH01_01), 1920×1080, 60fps, 600프레임, 10.0초.
  - 오디오는 Godot AudioServer 실제 믹스다. RMS 0.0388, 피크 0.558.
  - SHA-256 bdb1c6c2fd125e9b6b64f14f24d07217bc8aad5c38d2d658d219a8409f870975
  - 입력은 스크립트로 넣었다(Input.parse_input_event). 적 AI와 피해 계산은 게임 그대로다. 고정 60fps 렌더라서 실시간 성능 측정이 아니다.
- 정지 프레임:
  - `frame_0030.png` 034daea3dc7a7bb35a76fe3cea4b4b2c216fd779d477d47e4a33a37bdbaf2462
  - `frame_0300.png` 06febbaa907e4efd84491679ebbbe115cf9eeae0bc7373441461e4348b3a4ed8
    봉쇄 교차로에서 BULWARK 정면 장갑에 맞은 탄이 BLOCKED 표시와 함께 사격 방향 반대쪽으로 튄다.
  - `frame_0540.png` 6bbeeb6b45b34c962ae2688b871344be1635c7a46dc0a02fd68bea01c19ea765
- 기록 파일: `capture.json`, `encode.json`, `manifest.json`(의존 파일 해시), `godot.log`, `process.log`. 두 로그 모두 SCRIPT ERROR가 없다.
- mp4 영상은 로컬에만 둔다(09-24 정리 지시에 따라 검증 녹화는 git에 넣지 않는다. `.gitignore` 참고). 위 SHA-256으로 대조한다.
- 중간 산출물 `native_mix.avi`(84 MB)와 `native_readback.mkv`(460 MB)는 `.cache/session/vfx_video_intermediates/`로 옮겼다.
- `validate_visual_evidence_1080p.py --require-dynamic-capture` → `visual_evidence_1080p.json`: gate PASS, dynamic_capture_gate PASS. 이는 컨테이너와 디코딩만 확인한 것이고 화질이나 아트 승인이 아니다.
