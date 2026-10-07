# SFX intake status — 2026-09-19

Status: LOCAL_APP_INTEGRATED / TECHNICAL_CHECKS_PASS. Final scope and limitations: `RESULT_KO.md`. Subjective human listening approval and remote deployment are not claimed.

The user supplied `C:/Users/AAA/Downloads/SABLE_CIRCUIT_SFX_R04_COLOSSAL_120.zip` on 2026-09-19. Its 48,220,837-byte archive SHA-256 matches the reported value below; CRC, all 120 base asset hashes and the three source-grain hashes were independently verified. The complete source package is preserved in `art_src/audio/chatgpt_sfx_r04_20260919/` and excluded from engine import. All 132 base/stereo alternatives passed the recorded deterministic PCM checks. Twenty-four WAV variants across twelve event roles are selected in `selected_bank_manifest.json`; no human listening approval is claimed. Licenses were inspected in the in-app browser, not delegated to the user. The historical transfer diagnosis below is retained for provenance, not a current blocker.

User requested selection and integration of good firing/explosion sounds already produced in the ChatGPT web conversation titled `세이블 서킷 전투영상 examples`:

https://chatgpt.com/c/6aa80466-5ae4-83e9-a5cf-9ff09bd6c422

The conversation was initially found in an existing Edge tab. After the user's explicit correction, all further browser work used a visible in-app browser tab opened to that exact conversation. No other chat was substituted.

## Source identified

Latest package: `SABLE_CIRCUIT_SFX_R04_COLOSSAL_120.zip`.
The web response reports 48,220,837 bytes, 120 base WAV files plus 12 stereo boss alternatives, event mapping, credits and validation records.
SHA-256: `c8758f1f030923a63dd01c10e50889307c72fbdf12606bc73acad2b5e7ed54eb` (now locally verified).

The original download button did not respond. A scoped message in the same conversation requested reattachment of the retained R04 ZIP without any new sound generation, redesign or recompression. ChatGPT reported finding the original and attached it again with the above name/hash. That reattachment is currently visible in the in-app tab.

## Transfer diagnosis

- In-app UI shows the download-start notification and its download event fires, but no local ZIP was produced in the checked Downloads, Codex attachment/staging or browser-use staging locations.
- The browser's ordinary download-link response reports success, file ID `file_00000000d03c82068d8a8135b5dc4fb7` and a signed content URL. No credentials/cookies were read or exported.
- A direct inbound transfer of that observed signed URL returned `File stream access denied`; no ZIP was created.
- The in-app client's actual download attempt reports `net::ERR_BLOCKED_BY_CLIENT` through its documented network diagnostic interface.
- The supported browser API provides no file-save method on its download object; pageAssets rejects this ZIP/other asset kind. Attempting to set a project-local download destination through raw CDP was explicitly unsupported and did not change browser settings. No security controls were disabled.

Historical next step, now completed: receive the retained ZIP and verify its hash, safe paths and CRC. No mixed preview was substituted for separate WAV effects.

## Integration points inspected (no runtime changes yet)

- `scripts/audio/procedural_combat_sfx.gd` currently synthesizes temporary profile-specific tones on every call.
- `scripts/combat/combat_feedback.gd` owns player/enemy firing and projectile hit sound calls. Preserve the existing IDs in playable/enemy art profiles.
- `scripts/combat/site7_enemy_tactics.gd` has actual projectile emission calls and boss fan attacks. Coalesce simultaneous fan sounds; do not change attack counts, aim or gameplay.
- `scripts/combat/site7_attack_warning.gd` changes `fired` at the actual damage event. Explosion playback belongs there, not at a timestamp copied from a rendered video or the start of the warning.
- Death/collapse sounds need an exactly-once death boundary and scene-owned playback that can preserve a tail after the actor disappears without leaking beyond scene exit.
- Use bounded polyphony, modest gain/headroom, avoid repeated identical variants, and verify decoding, no clipping, event timing, scene cleanup and actual audible selection. Do not replace character art/movement, app scale or existing unrelated work.
- R04 web description identifies explosion source as Michel Baradari, `2 High Quality Explosions`, CC BY 3.0, with required attribution/modification notice. Read actual packaged credits and verify authoritative licensing before shipping; this summary is not the license gate.
