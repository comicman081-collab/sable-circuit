"""Narrow, fail-closed SITE-7 authoring scope. Not an artistic approval gate."""
import json
from pathlib import Path

POLICY = Path(__file__).resolve().parent.parent / 'data/art_profiles/site7_enemy_body_plan.json'

def require_biped_authoring(character):
    # Playable characters and generic isolated test fixtures are not enemy IDs.
    if not character.startswith('site7_'):
        return
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    if policy['humanoid_enemy_limit'] != 0 or policy.get('humanoid_character_id') is not None:
        raise ValueError('ROBOT_ONLY_ENEMY: policy must forbid all humanoid enemy production')
    raise ValueError('ROBOT_ONLY_ENEMY: All humanoid enemies, including site7_rifle, were retired by the user on 2026-09-19. Human gait authoring is for playable characters only; no generation, repair or resume for '+character)
