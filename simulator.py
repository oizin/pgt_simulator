import numpy as np
import pandas as pd

class Simulation:
    def __init__(self,n_embryos,event_rate,lbr,tpr,fpr):
        """
        Args:
        - n_embryos: number of (frozen) embryos available to transfer
        - event_rate: the rate of aneuploidy
        - lbr: expected live birth rate amongst non-aneuploid embryos
        - tpr: the % of abnormal embryos detected by PGT
        - fpr: the % of normal embryos falsely marked as aneuploidy
        """
        self.n_embryos = n_embryos
        self.event_rate = event_rate
        self.lbr = lbr
        self.tpr = tpr
        self.fpr = fpr

    def simulate_complete_cycle(self,pgt):
        """
        Simulate a complete cycle

        Args:
            - ids: a list of IDs
            - pgt: True/False
        """
        aneuploid = np.random.binomial(1,self.event_rate,self.n_embryos)

        # pgt simulation
        pgt_results = np.zeros_like(aneuploid)
        if pgt == True:
            for j in range(len(aneuploid)):
                pgt_results[j] = np.random.binomial(1,(1-aneuploid[j])*self.fpr + aneuploid[j]*self.tpr)
            aneuploid = aneuploid[~pgt_results.astype(bool)]

        n_embryos = len(aneuploid) 

        # outcome simulation
        if np.sum(aneuploid) == n_embryos:
            n_et = n_embryos
            event = 0
        else:
            i = 0
            event = 0
            n_et = 0
            while (i < n_embryos) & (event == 0):
                event = np.random.binomial(1,self.lbr*(1-aneuploid[i]))
                n_et += 1
                i += 1
        out = {'pgt': pgt, 'n_et':n_et,'lb': event,'aneuploid':aneuploid,'pgt_results':pgt_results}
        return out
    
    def simulate(self,J,N_pgt,N_nopgt):
        out = []
        ids_pgt = list(range(N_pgt))
        ids_nopgt = list(range(N_pgt,N_pgt + N_nopgt))
        for j in range(J):
            if j == 0:
                N_pgt = N_pgt
                N_nopgt = N_nopgt
            else:
                ids_pgt = df_j.loc[(df_j.lb == 0) & (df_j.pgt == True),"id"].to_list()
                N_pgt = len(ids_pgt)
                ids_nopgt = df_j.loc[(df_j.lb == 0) & (df_j.pgt == False),"id"].to_list()
                N_nopgt = len(ids_nopgt)
            et_n = [0] * N_pgt
            data = {'id': ids_pgt, 'pgt': [True] * N_pgt, 'et_n': et_n, 'lb': np.zeros_like(et_n)}
            results_pgt = pd.DataFrame(data)
            et_n = [0] * N_nopgt
            data = {'id': ids_nopgt,'pgt': [False] * N_nopgt, 'et_n': et_n, 'lb': np.zeros_like(et_n)}
            results_nopgt = pd.DataFrame(data)
            for i in range(N_pgt):
                tmp = self.simulate_complete_cycle(pgt=True)
                results_pgt.iloc[i,[1,2,3]] = [tmp['pgt'],tmp['n_et'],tmp['lb']]
            for i in range(N_nopgt):
                tmp = self.simulate_complete_cycle(pgt=False)
                results_nopgt.iloc[i,[1,2,3]] = [tmp['pgt'],tmp['n_et'],tmp['lb']]
            df_j = pd.concat([results_pgt,results_nopgt])
            df_j["complete_n"] = j + 1
            out.append(df_j)
        self.results = pd.concat(out).reset_index()

    def get_results(self):
        return self.results
    
    def get_summarised_results(self,which='et_n'):
        results = self.results
        if which == "et_n": 
            results = results.groupby('id').agg({'lb':'max','et_n':'sum','pgt':'max'})
        elif which == "complete_n":
            results = results.groupby('id').agg({'lb':'max','complete_n':'max','pgt':'max'})
        results = results.reset_index(drop=True)
        out = []
        for pgt in [True,False]:
            N = results.loc[results.pgt == pgt,:].shape[0]
            # how many did each cycle
            max_n = results.loc[results.pgt == pgt,:].groupby(which)[which].count()    
            max_n = np.insert(max_n,0,0)
            n = N - np.cumsum(max_n)
            n = n[:-1]
            lb = results.loc[results.pgt == pgt,:].groupby(which)['lb'].sum()
            data = {which: lb.index, 'pgt': pgt, 'n': n, 'lb': lb, 'lbr': lb/n, 'clbr': np.cumsum(lb)/N}
            out.append(pd.DataFrame(data))
        return pd.concat(out).reset_index(drop=True)
                             
sim = Simulation(8,0.4,0.4,0.9,0.1)
sim.simulate(3,1000,1000)
print(sim.get_summarised_results())
print(sim.get_summarised_results('complete_n'))