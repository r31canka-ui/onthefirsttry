import numpy as np, json, sys, soundfile as sf
x, sr = sf.read(sys.argv[1]); x = x if x.ndim==1 else x.mean(1)
hop = int(0.01*sr); n=len(x)//hop
e = np.sqrt((x[:n*hop].reshape(n,hop)**2).mean(1))
db = 20*np.log10(e+1e-9)
thr = float(sys.argv[3]) if len(sys.argv)>3 else -32
sp = db > thr
segs=[]; i=0
while i<n:
    if sp[i]:
        j=i
        while j<n and sp[j]: j+=1
        segs.append([i,j]); i=j
    else: i+=1
m=[]
for s in segs:
    if m and s[0]-m[-1][1] < 15: m[-1][1]=s[1]
    else: m.append(s)
m=[s for s in m if s[1]-s[0]>=12]
out=[[round(max(0,a/100-0.05),2), round(b/100+0.08,2)] for a,b in m]
json.dump(out, open(sys.argv[2],'w')); print(len(out), 'segments', 'thr', thr)
for a,b in out: print(a,b, round(b-a,2))
