from subprocess import check_output
from geoip import geolite2
from pymongo import MongoClient
from time import sleep
import ipfsApi

ipfs = ipfsApi.Client('127.0.0.1', 5001)

client = MongoClient()

db = client["nodemap"]["ips"]

for line in check_output("ipfs diag net", shell=True).split("\n"):
  if line.strip().startswith("ID"):
    peerid = line.strip().split(" ")[1]
    if peerid:
      print("PEERID: ",peerid)
      try:
        output = ipfs.dht_findpeer(peerid, timeout=1)
        
        for ip in output.split("\n"):
          if ip.strip().startswith("/"):
            data = {"ip":ip.split("/")[2]}
            print(data)
            db.replace_one(data, data, upsert=True)
      except:
        pass
        
ips = map(lambda x:x["ip"], db.find({}))

s = ""
yay = fail = 0
for ip in ips:
  match = geolite2.lookup(ip.strip())
  if match:
    try:
      s += "[%f,%f]," % match.location
      yay += 1
    except:
      fail += 1

with open("index_template.html", "r") as f:
  html = f.read()

html = html.replace("REPLACEME", s) 

with open("index.html", "w+") as f:
  f.write(html)

hsh = ipfs.add("index.html")["Hash"]
print(hsh)
ipfs.name_publish(hsh)
