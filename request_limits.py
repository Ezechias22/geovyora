"""Bound requests including chunked uploads; reject before parsing oversized bodies."""
from fastapi import HTTPException
from fastapi.responses import JSONResponse
class RequestSizeLimit:
    def __init__(self,app):self.app=app
    async def __call__(self,scope,receive,send):
        if scope['type']!='http':return await self.app(scope,receive,send)
        path=scope.get('path','');limit=12*1024*1024 if path=='/api/submissions/upload' else 2*1024*1024 if path=='/api/webhooks/mux' else 1024*1024 if path.startswith('/admin/') else 64*1024
        headers=dict(scope.get('headers',[]))
        try:length=int(headers.get(b'content-length',b'0'))
        except ValueError:length=limit+1
        if length<0 or length>limit:return await JSONResponse({'detail':'Demann lan depase limit la.'},status_code=413)(scope,receive,send)
        consumed=0
        async def bounded_receive():
            nonlocal consumed
            event=await receive()
            if event['type']=='http.request':
                consumed+=len(event.get('body',b''))
                if consumed>limit:raise HTTPException(413,'Demann lan depase limit la.')
            return event
        await self.app(scope,bounded_receive,send)
