from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'app.js'
s=p.read_text(encoding='utf8')
s=s.replace('button.onmousedown=event=>{event.preventDefault();','button.onclick=event=>{event.preventDefault();')
s=s.replace("if(event.key==='Escape')close()", "if(event.key==='Escape')close();if(event.key==='Enter'){event.preventDefault();input.parentElement?.querySelector('.pokemon-picker-results button')?.click()}")
s=s.replace('profile:clean.profile}))))', 'profile:clean.profile,journey:clean.journey}))))')
s=s.replace('<h1>Save &amp; Sync</h1>', '<h1>Save &amp; Sync</h1>')
s=s.replace('Keep a JSON backup of your caught Pokémon without using cloud sync.', 'Back up your caught Pokémon, teams, sidequests, Strata progress and field notes in one file.')
s=s.replace('<article class="save-panel"><span class="eyebrow">ENCRYPTED CLOUD SYNC', '<article class="save-panel" ${configured?\'\':\'hidden\'}><span class="eyebrow">ENCRYPTED CLOUD SYNC')
p.write_text(s,encoding='utf8')
