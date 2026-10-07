(() => {
  'use strict';
  const context = document.modelContext;
  if (!context?.registerTool) return;
  const lifecycle = new AbortController();
  const tool = {
    name:'get_demo_status',
    title:'Read SABLE CIRCUIT demo status',
    description:'Read whether the demo is downloading, ready to play, or failed, and its keyboard controls. Does not change gameplay or saved progress.',
    inputSchema:{type:'object',properties:{},additionalProperties:false},
    annotations:{readOnlyHint:true,untrustedContentHint:false},
    execute(input) {
      if (!input || typeof input !== 'object' || Array.isArray(input) || Object.keys(input).length) throw new Error('Expected an empty object');
      const notice = document.querySelector('#status-notice');
      const error = notice?.textContent?.trim();
      const progress = document.querySelector('#status-progress');
      return {state:error?'error':document.querySelector('#status')?'loading':'ready',
        error:error||null,downloadFraction:progress?.max?progress.value/progress.max:null,
        controls:'WASD/arrows move; Shift run; mouse aim; left-click fire; R reload; Space evade; 1–3 operator; Q/E/X skills; F interact/revive; C extract; H/Esc controls; touch toggle inside battle',
        persistence:'Device-local browser save; training does not award resources'};
    }
  };
  try { Promise.resolve(context.registerTool(tool,{signal:lifecycle.signal})).catch(console.warn); }
  catch(error) { console.warn(error); }
  window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});
})();
