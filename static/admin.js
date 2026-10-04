'use strict';
const qs=s=>document.querySelector(s);
const staffCopy=JSON.parse(document.body.dataset.ui||'{}');
const tr=text=>staffCopy[text]||text;
if(qs('#mux-form'))qs('#mux-form').onsubmit=async e=>{e.preventDefault();const form=e.target,status=form.querySelector('.form-status'),btn=form.querySelector('button'),file=qs('#video-file').files[0];if(!file)return;if(file.size>Number(form.dataset.maxBytes||1073741824)){status.textContent=tr('Fichye sa a depase limit chajman an.');return}btn.disabled=true;try{status.textContent=tr('Prepare chajman an…');const r=await fetch('/admin/videos/upload',{method:'POST',headers:{Accept:'application/json'},body:new FormData(form)});const d=await r.json();if(!r.ok)throw Error(d.detail||'Chajman echwe.');if(file.size>d.max_bytes)throw Error('Fichye sa a depase limit chajman an.');status.textContent=tr('Ap voye videyo a nan Mux…');const upload=await fetch(d.url,{method:'PUT',body:file});if(!upload.ok)throw Error('Chajman echwe. Eseye ankò.');status.textContent=tr('Chajman fini. Mux ap trete videyo a. Rechaje paj la pou wè estati a.')}catch(e){status.textContent=tr(e.message)}finally{btn.disabled=false}};
if(qs('#load-revisions'))qs('#load-revisions').onclick=async()=>{const btn=qs('#load-revisions'),box=qs('#revision-list');try{const r=await fetch('/api/revisions/'+btn.dataset.id);if(!r.ok)throw Error('Ou pa gen aksè.');const data=await r.json();box.replaceChildren();if(!data.length)box.textContent=tr('Pa gen vèsyon anvan.');data.forEach(rev=>{const row=document.createElement('div'),text=document.createElement('small'),restore=document.createElement('button');text.textContent=rev.created_at.slice(0,16)+' ';restore.type='button';restore.className='text-button';restore.textContent=tr('Restore nan draft');restore.onclick=async()=>{if(!confirm(tr('Restore vèsyon sa a nan draft?')))return;const f=new FormData();f.set('id',rev.id);f.set('csrf_token',btn.dataset.csrf);const r=await fetch('/admin/revisions/restore',{method:'POST',headers:{Accept:'application/json'},body:f});if(r.ok)location.href=r.url;else alert(tr('Aksè admin obligatwa.'));};row.append(text,restore);box.append(row)})}catch(e){box.textContent=tr(e.message)}};
if(qs('#media-form'))qs('#media-form').onsubmit=async e=>{e.preventDefault();const f=e.target,file=qs('#media-file').files[0],status=f.querySelector('.form-status'),btn=f.querySelector('button');if(!file)return;if(file.size>10*1024*1024){status.textContent=tr('10 MB maksimòm.');return}btn.disabled=true;try{const data=new FormData(f);data.set('content_type',file.type);const r=await fetch('/admin/media/upload-url',{method:'POST',headers:{Accept:'application/json'},body:data});const d=await r.json();if(!r.ok)throw Error(d.detail);const res=await fetch(d.url,{method:'PUT',headers:d.headers,body:file});if(!res.ok)throw Error('Storage pa aksepte foto a. Verifye CORS.');status.textContent=tr('Ap verifye foto a…');const verify=new FormData();verify.set('id',d.id);verify.set('csrf_token',f.elements.csrf_token.value);const checked=await fetch('/admin/media/verify',{method:'POST',headers:{Accept:'application/json'},body:verify});const v=await checked.json();if(!checked.ok)throw Error(v.detail||'Verifikasyon echwe.');status.textContent=tr('Foto verifye. URL pou CMS: ')+v.url;}catch(e){status.textContent=tr(e.message)}finally{btn.disabled=false}};

[...document.querySelectorAll('.media-verify-form')].forEach(form=>form.onsubmit=async e=>{e.preventDefault();const status=form.querySelector('.form-status'),btn=form.querySelector('button');btn.disabled=true;try{const r=await fetch(form.action,{method:'POST',headers:{Accept:'application/json'},body:new FormData(form)});const d=await r.json();if(!r.ok)throw Error(d.detail||'Verifikasyon echwe.');location.reload()}catch(e){status.textContent=tr(e.message);btn.disabled=false}});

// Keep the staff preference separate from the public site's language.
if(qs('#admin-language'))qs('#admin-language').onchange=event=>{
 const locale=event.target.value;
 document.cookie='geovyora_admin_locale='+encodeURIComponent(locale)+';path=/;max-age=31536000;SameSite=Lax'+(location.protocol==='https:'?';Secure':'');
 const url=new URL(location.href);url.searchParams.delete('lang');location.href=url.href;
};
async function uploadEditorPhoto(file,form){
 if(file.size>10*1024*1024)throw Error('10 MB maksimòm.');
 const data=new FormData();data.set('csrf_token',form.elements.csrf_token.value);data.set('content_type',file.type);
 const response=await fetch('/admin/media/upload-url',{method:'POST',headers:{Accept:'application/json'},body:data});const result=await response.json();if(!response.ok)throw Error(result.detail||'Chajman echwe.');
 const uploaded=await fetch(result.url,{method:'PUT',headers:result.headers,body:file});if(!uploaded.ok)throw Error('Storage pa aksepte foto a. Verifye CORS.');
 const check=new FormData();check.set('id',result.id);check.set('csrf_token',form.elements.csrf_token.value);
 const verified=await fetch('/admin/media/verify',{method:'POST',headers:{Accept:'application/json'},body:check});const record=await verified.json();if(!verified.ok)throw Error(record.detail||'Verifikasyon echwe.');return record.url;
}
function busy(form,delta){const count=Math.max(0,Number(form.dataset.uploadCount||0)+delta);form.dataset.uploadCount=String(count);form.dataset.uploading=count?'1':'0'}
function insertBody(form,text){const field=form.elements.body;if(!field)return;const start=field.selectionStart,end=field.selectionEnd;field.setRangeText('\n\n'+text+'\n\n',start,end,'end');field.dispatchEvent(new Event('input',{bubbles:true}));field.focus()}
[...document.querySelectorAll('.editor-image-picker')].forEach(picker=>{
 const form=picker.closest('form'),file=picker.querySelector('.editor-image-file'),button=picker.querySelector('.editor-image-upload'),status=picker.querySelector('.editor-image-status'),preview=picker.querySelector('.editor-image-preview');
 function choose(url){form.elements.image.value=url;preview.hidden=!url;if(url)preview.src=url;form.elements.image.dispatchEvent(new Event('input',{bubbles:true}))}
 async function upload(){if(!file.files[0])return;button.disabled=true;file.disabled=true;busy(form,1);status.textContent=tr('Prepare chajman an…');try{choose(await uploadEditorPhoto(file.files[0],form));status.textContent=tr('Foto chaje avèk siksè.')}catch(error){status.textContent=tr(error.message)}finally{button.disabled=false;file.disabled=false;busy(form,-1);file.value=''}}
 button.onclick=upload;file.onchange=upload;picker.querySelector('.editor-image-library').onchange=event=>{if(event.target.value)choose(event.target.value)};
 const insert=picker.querySelector('.editor-image-insert');if(insert)insert.onclick=()=>{const url=form.elements.image.value;if(!url){status.textContent=tr('Chaje yon foto anvan.');return}insertBody(form,'![]('+url+')');status.textContent=tr('Foto a ajoute nan atik la.')};
 form.addEventListener('submit',event=>{if(form.dataset.uploading==='1'){event.preventDefault();status.textContent=tr('Prepare chajman an…')}});
});
[...document.querySelectorAll('.editor-video-picker')].forEach(picker=>{
 const form=picker.closest('form');picker.querySelector('.editor-video-insert').onclick=()=>{const slug=picker.querySelector('.editor-video-library').value;if(!slug)return;insertBody(form,'[video:'+slug+']');picker.querySelector('.editor-video-status').textContent=tr('Videyo a ajoute nan atik la.')};
});

[...document.querySelectorAll('.editor-video-picker')].forEach(picker=>{
 const form=picker.closest('form'),file=picker.querySelector('.editor-video-file'),button=picker.querySelector('.editor-video-upload'),status=picker.querySelector('.editor-video-status');
 async function upload(){const selected=file.files[0];if(!selected)return;if(form.elements.title.value.trim().length<3){status.textContent=tr('Ekri tit atik la anvan.');return}if(selected.size>Number(picker.dataset.maxBytes)){status.textContent=tr('Fichye sa a depase limit chajman an.');return}
  button.disabled=true;file.disabled=true;busy(form,1);status.textContent=tr('Prepare chajman an…');
  try{const data=new FormData();data.set('csrf_token',form.elements.csrf_token.value);data.set('title',form.elements.title.value);data.set('locale',form.elements.locale.value);const response=await fetch('/admin/videos/upload',{method:'POST',headers:{Accept:'application/json'},body:data});const result=await response.json();if(!response.ok)throw Error(result.detail||'Chajman echwe.');if(selected.size>result.max_bytes)throw Error('Fichye sa a depase limit chajman an.');status.textContent=tr('Ap voye videyo a nan Mux…');const uploaded=await fetch(result.url,{method:'PUT',body:selected});if(!uploaded.ok)throw Error('Chajman echwe. Eseye ankò.');insertBody(form,'[video:'+result.slug+']');status.textContent=tr('Videyo a chaje epi ajoute nan atik la. Mux ap trete li.');}
  catch(error){status.textContent=tr(error.message)}finally{button.disabled=false;file.disabled=false;busy(form,-1);file.value=''}
 }
 button.onclick=upload;
});
