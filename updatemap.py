from subprocess import check_output
from geoip import geolite2
from pymongo import MongoClient

client = MongoClient()

db = client["nodemap"]["ips"]

for line in check_output("ipfs diag net", shell=True).split("\n"):
  if line.strip().startswith("ID"):
    peerid = line.strip().split(" ")[1]
    output = check_output("ipfs dht findpeer %s" % peerid, shell=True)
    for ip in output.split("\n"):
      if ip.strip().startswith("/"):
        data = {"ip":ip.split("/")[2]}
        db.replace_one(data, data, upsert=True)

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

hsh = check_output("ipfs add index.html", shell=True).split(" ")[1]
print(hsh)
check_output("ipfs name publish %s" % hsh, shell=True)
