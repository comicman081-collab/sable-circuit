extends RefCounted
## Output location for tests: the `--out=<res path>` user argument, else the test's own default.
## The regression runner passes --out so runs never write into dated QA record folders.

static func path(default_path: String) -> String:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--out="):
            return arg.trim_prefix("--out=")
    return default_path
