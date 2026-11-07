import csv, io, json, datetime, urllib.request, pathlib
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; WeeklyMarketDashboard/1.0)","Accept":"application/json,text/csv,*/*"})
 with urllib.request.urlopen(req,timeout=35) as f:return f.read().decode("utf-8-sig")
today=datetime.datetime.now(datetime.timezone.utc).date()
start=today-datetime.timedelta(days=380)
fg=json.loads(get("https://feargreedflow.com/api/fear-greed"))
fear={}
for d,v in zip(fg["dates"],fg["values"]):
 try:
  if v is not None:fear[d]=float(v)
 except (ValueError,TypeError):pass
raw=get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd="+start.isoformat())
sp={}
for r in csv.DictReader(io.StringIO(raw)):
 try:
  d=r.get("observation_date") or r.get("DATE") or r.get("date")
  sp[d]=float(r["SP500"])
 except (ValueError,TypeError,KeyError):pass
groups={}
for d in sorted(set(fear)&set(sp)):
 day=datetime.date.fromisoformat(d)
 if day<today-datetime.timedelta(days=365) or day>today or day.weekday()>4:continue
 monday=(day-datetime.timedelta(days=day.weekday())).isoformat()
 groups.setdefault(monday,[]).append((fear[d],sp[d]))
weeks=[{"date":d,"fear":round(sum(x for x,y in v)/len(v),3),"sp":round(sum(y for x,y in v)/len(v),3),"n":len(v)} for d,v in sorted(groups.items())]
if len(weeks)<35:raise RuntimeError("Insufficient matched weekly observations: "+str(len(weeks)))
output={"updated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"sources":{"fear":"https://feargreedflow.com/api/fear-greed","sp500":"https://fred.stlouisfed.org/series/SP500"},"weeks":weeks}
pathlib.Path("data.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Saved",len(weeks),"weeks")
