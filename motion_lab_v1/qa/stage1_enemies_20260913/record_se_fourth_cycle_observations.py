"""Persist main-agent observations already made on this exact fourth SE kit.

Does not grant source/cycle approval; the separate workflow must validate it.
"""
import hashlib
import json
from pathlib import Path

lab = Path(__file__).resolve().parents[2]
kit = lab / 'qa/site7_rifle/gait/f6ea0a697b022450_e3405323'
packet = json.loads((kit / 'cycle-observations.json').read_text(encoding='utf-8'))
draft = json.loads((kit / 'se_landmarks_observed_draft.json').read_text(encoding='utf-8'))
expected = ['81f9195d21d7ac3624a16b7d8c0ad248f6cf7b46b015441085f0f467905bcb23',
            'e186478b036ecdcf630493d597472f44134bbc45786fbadac02f24dc6a3d1bd9',
            '3a7dc59adc9c0fedc9920fdcd1ae2740251e82075a333e6a7c6ec8f2592f980e',
            'bfa49762a99176c7dac1c218ccf2974b4d7b882e7e216cfbaae74a816343af08',
            '1a7b133d11a6d6ca628eed239233c6effd5d6a9c003c26ba701343f5c6b9aacc',
            '17ae79dbeba283c35809ad84181dd2dbfbc62ceb0b6f8ec49a6e98bd35c06989']
for row, digest in zip(packet['inputs']['sources'], expected, strict=True):
    assert row['sha256'] == digest
    assert hashlib.sha256((lab / row['path']).read_bytes()).hexdigest() == digest
packet.update(decision='approved', reviewer='Codex main - actual 1x playback, sequential native decoding and six native cell overlays observed 2026-09-13')
for field in ('legMarkers', 'frames', 'landmarkBasis'):
    packet[field] = draft[field]
packet['landmarkBasis'] += (' Phase2 far knee is substantially occluded by the near knee; its marker follows the visible far-leg costume boundary at that overlap. It is not a separately exposed kneecap or an independently measured anatomical joint.')
observations = {
    'oppositeContacts': ([.039, .669, 1.269, 1.839],
        'Frame0 far unholstered left leg leads and near holstered right leg trails; frame3 reverses these roles with the same right holster still attached to the forward near thigh. Two distinct boots and two limb chains are visible, not the rejected extra third shin/foot.'),
    'passingAndSwing': ([.239, .439, .839, 1.039],
        'Near right boot folds behind at frame1 and passes under the body at frame2; far left boot folds behind at frame4 and advances with its bent knee at frame5. Frame2 legs overlap in this projection: the far knee is occluded, but its outer thigh/lower-shin edge and separate planted boot continue behind the nearer lifted boot. The marker is a surface proxy, not an invented visible bone center.'),
    'loopSeam': ([1.139, 1.269, 2.268, 2.339],
        'The final far-left passing step returns to far-left leading contact; near right support transitions back to a trailing foot. The repeated loop exchanges support rather than freezing a pair of legs. There is a visible six-snapshot cadence, not continuous interpolation.'),
    'footSliding': ([.039, .239, .439, .669, .839, 1.039],
        'Each support foot progresses rearward relative to the pelvis while the other boot lifts and returns. Ground-relative holds still show short slip between six authored snapshots; this is acceptable as the cautious armored NPC source cycle, not zero-slip IK or final game approval. The eventual app phase must use actual constrained displacement at the calibrated stride, not a free-running timer.'),
    'bodyContinuity': ([.439, .669, .839, 1.039, 1.839],
        'Hood, torso, holster, waist and both legs remain whole-body source art. Native panels show the repaired phase3 has no extra thigh red stripe and phases3/4 retain the compact red/silver kneecap design. Occluded rear knees are not counted as extra legs. Small shoulder and armor-outline variation remains; no detached upper/lower seam or green rectangular background is present.'),
    'weaponContinuity': ([.039, .439, .669, .938, 1.039],
        'The same short thick bullpup stays shouldered with both hands connected and its muzzle facing down-right throughout the SE cycle. Small source perspective/length changes remain, but there is no lowered carry pose or unrelated long rifle replacing it. Runtime emission must use the current authored muzzle and sector before each shot.')
}
packet['observations'] = {key: {'decision':'pass', 'seconds':times, 'notes':notes}
                          for key, (times, notes) in observations.items()}
video = lab / 'qa/stage1_enemies_20260913/cycle_capture/site7_rifle_se_live_1789298674195.webm'
digest = hashlib.sha256(video.read_bytes()).hexdigest()
assert digest == '5d917b322ccec6a4989101d490ea896a7fec9fe960e611125e9b1673dd4cb8d2'
packet['additionalObservedEvidence'] = {
    'video': video.relative_to(lab).as_posix(), 'videoSHA256': digest,
    'native': [1920,1080], 'decodedFrames':105, 'normalPlaybackRate':1,
    'scope':'Native canvas source-cycle capture, not a native1080 browser viewport or game controller; actual1x UI playback plus sequential native decoded panels inspected',
    'limitations':['Six discrete authored phases with short hold-frame slip, not anatomical foot locking',
                   'Surface/occlusion continuity proxies do not expose hidden joint centers',
                   'No separate sprint/strafe art, app activation, GPT visual approval or Luna reproduction']}
destination = kit / 'cycle-observations_reviewed.json'
with destination.open('x', encoding='utf-8') as stream:
    json.dump(packet, stream, ensure_ascii=False, indent=2)
print(destination)
