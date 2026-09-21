// Publish runtime files only, excluding source snapshots and local working files.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
const root=process.cwd(),dest=path.join(root,'_site');
fs.mkdirSync(dest,{recursive:true});
for(const name of ['index.html','app.js','companion.js','styles.css','refinements.css','adventure.css','sync-config.js','sw.js','site.webmanifest','.nojekyll'])fs.copyFileSync(path.join(root,name),path.join(dest,name));
fs.cpSync(path.join(root,'assets'),path.join(dest,'assets'),{recursive:true});
for(const dir of ['data','config']){
  fs.mkdirSync(path.join(dest,dir),{recursive:true});
  for(const file of fs.readdirSync(path.join(root,dir)).filter(f=>f.endsWith('.js')))fs.copyFileSync(path.join(root,dir,file),path.join(dest,dir,file));
}
const sw=fs.readFileSync(path.join(root,'sw.js'),'utf8');
const urls=vm.runInNewContext(sw.slice(0,sw.indexOf('self.addEventListener'))+'FILES');
for(const url of urls){
  const target=path.resolve(dest,url.split('?')[0]);
  if(!target.startsWith(dest+path.sep)&&target!==dest)throw Error('Out-of-scope cache URL');
  if(!fs.existsSync(target))throw Error('Missing cached asset: '+url);
}
console.log(`Pages runtime prepared; ${urls.length} cached URLs verified. No ROM or working sources included.`);
