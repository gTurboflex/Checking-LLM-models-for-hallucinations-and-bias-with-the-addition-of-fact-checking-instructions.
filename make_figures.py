"""Generate figures only from analysis.json; never substitute pilot numbers."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run_experiment import ROOT,MODELS

def main():
    data=json.loads((ROOT/'results/analysis.json').read_text(encoding='utf-8'))
    metrics={(r['model'],r['condition']):r for r in data['metrics']}
    names=['Qwen 1.7B','Qwen 4B','Qwen 8B*','Gemma E2B','Beam cloud*','Gemma 31B cloud*']
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(8.5,4.4),layout='constrained')
    x=np.arange(6)
    for c,offset,color,label in [('B',-.15,'#596b80','B  Leading prompt'),('D',.15,'#20958d','D  Leading + instruction')]:
        y=[];lo=[];hi=[]
        for m in MODELS:
            r=metrics[m,c];v=r['s_rate']
            y.append(np.nan if v is None else v*100)
            lo.append(0 if v is None else max(0,(v-r['s_ci'][0])*100))
            hi.append(0 if v is None else max(0,(r['s_ci'][1]-v)*100))
        ax.errorbar(x+offset,y,yerr=[lo,hi],fmt='o',capsize=4,color=color,label=label)
    ax.set(xticks=x,xticklabels=names,ylabel='False-premise agreement (%)',ylim=(-3,103))
    ax.tick_params(axis='x',rotation=15);ax.grid(axis='y',alpha=.2);ax.legend(frameon=False)
    fig.savefig(out/'figure1_agreement.png',dpi=220);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.5,4.4),layout='constrained')
    arr=np.array([[100*metrics[m,c]['H']/metrics[m,c]['labelled_n'] if metrics[m,c]['labelled_n'] else np.nan for c in 'ABCD'] for m in MODELS])
    im=ax.imshow(arr,cmap='YlOrRd',vmin=0,vmax=100,aspect='auto')
    for i,m in enumerate(MODELS):
        for j,c in enumerate('ABCD'):
            r=metrics[m,c];ax.text(j,i,f"{r['H']}/{r['labelled_n']}" if r['labelled_n'] else 'No labels',ha='center',va='center',color='white' if arr[i,j]>60 else 'black')
    ax.set(xticks=range(4),xticklabels=['A\nNeutral','B\nLeading','C Neutral\n+ instruction','D Leading\n+ instruction'],yticks=range(6),yticklabels=names)
    fig.colorbar(im,ax=ax,label='False focal claims (%)')
    fig.savefig(out/'figure2_factual_errors.png',dpi=220);plt.close(fig)
    print(out)

if __name__=='__main__':main()
