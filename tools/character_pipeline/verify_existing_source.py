"""Run the full existing-art authority check in the project Python runtime.

Blender's bundled Python lacks Pillow; its owned parent/child can call this
read-only verifier instead of silently skipping source-pixel validation.
"""
import argparse
import json
import source_art_intake

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    print(json.dumps(source_art_intake.authority(args.receipt), ensure_ascii=True))
