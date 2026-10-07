/* Reassemble verified, original Godot bytes below the hosting per-file limit. */
(() => {
  'use strict';
  const originalFetch = window.fetch.bind(window);
  const manifest = originalFetch('chunks.json').then(response => {
    if (!response.ok) throw new Error('Game download manifest unavailable');
    return response.json();
  });
  window.fetch = async (resource, options) => {
    const url = new URL(resource instanceof Request ? resource.url : resource, location.href);
    const name = url.pathname.split('/').pop();
    if (url.origin !== location.origin || !['index.wasm', 'index.pck'].includes(name)) {
      return originalFetch(resource, options);
    }
    const entry = (await manifest)[name];
    let i = 0;
    const stream = new ReadableStream({
      async pull(controller) {
        if (i === entry.chunks.length) { controller.close(); return; }
        const chunk = entry.chunks[i++];
        try {
          const response = await originalFetch(new URL(chunk.url, location.href), options);
          if (!response.ok) throw new Error(`Game download failed: ${response.status}`);
          const bytes = await response.arrayBuffer();
          const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))]
            .map(value => value.toString(16).padStart(2,'0')).join('');
          if (bytes.byteLength !== chunk.bytes || digest !== chunk.sha256) throw new Error('Game data failed integrity check');
          controller.enqueue(new Uint8Array(bytes));
        } catch (error) { controller.error(error); }
      }
    });
    return new Response(stream, {headers:{
      'Content-Type':name.endsWith('.wasm') ? 'application/wasm' : 'application/octet-stream',
      'Content-Length':String(entry.bytes)
    }});
  };
})();
