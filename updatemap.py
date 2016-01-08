from subprocess import check_output
from geoip import geolite2
from pymongo import MongoClient
import ipfsApi

ipfs = ipfsApi.Client()

client = MongoClient()
db = client["nodemap"]["ips"]

for line in check_output("ipfs diag net", shell=True).split("\n"):
  line = line.strip()
  if line.startswith("ID"):
    peerid = line.split(" ")[1]
    if peerid:
      try:
        output = ipfs.dht_findpeer(peerid, timeout=5)
        
        for ip in output.split("\n"):
          if ip.strip().startswith("/"):
            data = {"ip":ip.split("/")[2].strip()}
            db.replace_one(data, data, upsert=True)
      except:
        pass
        
ips = [x["ip"] for x in db.find({})]

s = ""
for ip in ips:
  match = geolite2.lookup(ip)
  if match:
    try:
      s += "[%f,%f]," % match.location
    except:
      pass

with open("index_template.html", "r") as f:
  html = f.read()

html = html.replace("REPLACEME", s) 

with open("index.html", "w+") as f:
  f.write(html)

hsh = ipfs.add("index.html")["Hash"]
ipfs.name_publish(hsh)
