#!/bin/sh
set -eu
python3 - "$CERTBOT_DOMAIN" "$CERTBOT_VALIDATION" <<'PY'
import json,sys,urllib.request
host='_acme-challenge.'+sys.argv[1]+'.'
data=json.dumps({'host':host,'value':sys.argv[2]}).encode()
req=urllib.request.Request('http://challtestsrv:8055/set-txt',data=data,headers={'Content-Type':'application/json'})
print(urllib.request.urlopen(req).read().decode())
PY
