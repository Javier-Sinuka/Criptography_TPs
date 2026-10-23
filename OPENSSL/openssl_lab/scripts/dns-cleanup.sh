#!/bin/sh
set -eu
python3 - "$CERTBOT_DOMAIN" <<'PY'
import json,sys,urllib.request
host='_acme-challenge.'+sys.argv[1]+'.'
data=json.dumps({'host':host}).encode()
req=urllib.request.Request('http://challtestsrv:8055/clear-txt',data=data,headers={'Content-Type':'application/json'})
print(urllib.request.urlopen(req).read().decode())
PY
