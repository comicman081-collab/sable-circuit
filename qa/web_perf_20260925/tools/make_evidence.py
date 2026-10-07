"""Write the wasm function-naming evidence (static analysis of the shipped, name-less wasm).

usage: python make_evidence.py <godot.wasm> <index.js> <out.json>
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wasm_names import Wasm, import_names  # noqa: E402

NAMES = {
    2238: ('GDScriptFunction::call (GDScript VM)', 'gdscript_vm.cpp messages (stack overflow, await, "is" on freed instance), 154-entry opcode br_table, 56.6 KB body'),
    43559: ('GDScript::callp (static function call)', '"Can\'t call non-static function", gdscript.cpp; calls f2238'),
    21616: ('main loop callback (os_web main_loop_callback)', 'display size update, canvas resize, fs sync, calls f18792'),
    18792: ('Main::iteration', '"debug/settings/stdout/print_fps", "Project FPS: %d"'),
    65213: ('SceneTree::physics_process', '"physics_frame", "_process_picking"'),
    65205: ('SceneTree::process', '"process_frame", "_flush_scene_change"'),
    67320: ('RasterizerCanvasGLES3::canvas_render_items', '"2D Batch UBO", "2D Lights UBO", GL buffer calls'),
    67307: ('RasterizerCanvasGLES3::request_polygon', '"request_polygon", "Polygon 2D vertex buffer"; glGenVertexArrays/glGenBuffers/glBufferData'),
    67306: ('RasterizerCanvasGLES3::free_polygon', '"free_polygon"; glDeleteBuffers/glDeleteVertexArrays'),
    19098: ('RendererCanvasCull::canvas_item_add_polygon', '"canvas_item_add_polygon", "Invalid polygon data, triangulation failed."'),
    3148: ('CanvasItem::draw_polygon', '"draw_polygon", scene/main/canvas_item.cpp'),
    19109: ('RendererCanvasCull::canvas_item_add_polyline', '"canvas_item_add_polyline"'),
    24112: ('CanvasItem::draw_polyline', '"draw_polyline", scene/main/canvas_item.cpp'),
    9311: ('RendererCanvasCull::canvas_item_add_ellipse', '"canvas_item_add_ellipse"'),
    24122: ('CanvasItem::draw_ellipse (draw_circle)', '"draw_ellipse", scene/main/canvas_item.cpp'),
    65926: ('CanvasItem::_redraw_callback', '"_draw"; reached from the MessageQueue flush (f3022) via f788/f662'),
    67327: ('RasterizerGLES3 initialisation', '"RasterizerGLES3", shader cache setup; the only caller of glGetIntegerv/glGetFloatv/glGetInteger64v'),
}


def main():
    wasm_path, js_path, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    data = open(wasm_path, 'rb').read()
    wasm = Wasm(data)
    imports = import_names(open(js_path, encoding='utf8').read())
    rows = []
    for index, (name, why) in NAMES.items():
        consts, calls, indirect, br_table, size = wasm.decode(index)
        strings = []
        for value in consts:
            text = wasm.cstr(value)
            if text and text not in strings:
                strings.append(text)
        gl = sorted({imports.get(wasm.imports[c][1], wasm.imports[c][1]) for c in calls if c < wasm.nimp})
        rows.append({'wasm_function': f'wasm-function[{index}]', 'identified_as': name, 'basis': why,
                     'body_bytes': size, 'max_br_table': br_table, 'strings_sample': strings[:8], 'imported_callees': gl[:16]})
    report = {
        'wasm_sha256': hashlib.sha256(data).hexdigest(), 'wasm_bytes': len(data),
        'method': 'The shipped index.wasm has no name section. Function bodies were decoded; i32.const operands were '
                  'resolved to C strings in the data segments (error-macro file/function names, signal and '
                  'setting names), imported callees were named through the JS glue wasmImports map, and '
                  'direct-call edges were followed.',
        'functions': rows,
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('wrote', out, len(rows))


if __name__ == '__main__':
    main()
