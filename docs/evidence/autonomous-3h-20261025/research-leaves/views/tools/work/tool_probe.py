import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output');a=p.parse_args()
data=Path(a.input).read_bytes()
if a.output:
 print(json.dumps({'status':'BLOCKED','reason':'managed read-only capability','write_supported':False,'source_sha256':hashlib.sha256(data).hexdigest()}));raise SystemExit(3)
print(json.dumps({'status':'PASS','read_supported':True,'source_sha256':hashlib.sha256(data).hexdigest(),'bytes_read':len(data)}))
