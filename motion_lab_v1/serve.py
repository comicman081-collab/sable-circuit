"""Run the standalone Motion Studio; no old pipeline or global configuration."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse,re,json,socket

class Server(ThreadingHTTPServer):
    allow_reuse_address=False
    def server_bind(self):
        if hasattr(socket,'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        super().server_bind()

class Handler(SimpleHTTPRequestHandler):
    # The defaults serve the live local preview.  Candidate QA can set these
    # roots to an isolated project-local packet without touching public/ or qa/.
    web_root=Path(__file__).parent/'public'
    qa_root=Path(__file__).parent/'qa'
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(self.web_root),**kw)
    def end_headers(self):
        self.send_header('Cache-Control','no-cache')
        super().end_headers()
    def do_POST(self):
        # Browser QA captures are written only into this lab's qa folder.
        match=re.fullmatch(r'/__qa/([a-z0-9_-]+\.(?:png|json|webm))',self.path)
        length=int(self.headers.get('Content-Length','0'))
        if not match or not 0<length<16000000:
            self.send_error(400);return
        data=self.rfile.read(length)
        if match[1].endswith('.png') and not data.startswith(b'\x89PNG\r\n\x1a\n'):
            self.send_error(400);return
        if match[1].endswith('.webm') and not data.startswith(b'\x1a\x45\xdf\xa3'):
            self.send_error(400);return
        if match[1].endswith('.json'):
            try:json.loads(data)
            except ValueError:self.send_error(400);return
        directory=Path(self.qa_root).resolve();directory.mkdir(parents=True,exist_ok=True)
        (directory/match[1]).write_bytes(data)
        self.send_response(201);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"saved":true}')

if __name__=='__main__':
    lab=Path(__file__).resolve().parent
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=14821);p.add_argument('--root',default=str(lab/'public'),help='Project-local web root (default: public)');p.add_argument('--qa-root',default=str(lab/'qa'),help='Project-local QA output root (default: qa)');a=p.parse_args()
    web_root=Path(a.root).resolve();qa_root=Path(a.qa_root).resolve()
    if not web_root.is_relative_to(lab) or not qa_root.is_relative_to(lab):raise SystemExit('Web and QA roots must stay under motion_lab_v1')
    if not web_root.is_dir():raise SystemExit(f'Missing web root: {web_root}')
    Handler.web_root=web_root;Handler.qa_root=qa_root
    print(f'Motion Studio: http://127.0.0.1:{a.port}',flush=True)
    Server(('127.0.0.1',a.port),Handler).serve_forever()
