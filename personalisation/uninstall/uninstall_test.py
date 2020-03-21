# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from datetime import date

data=pd.read_json("way2_uninstall_data.json",lines=True)

data=data.drop(columns="_id")

data=data.fillna(0)

data=data.replace(["NULL",""],0)

def cal_tdays(row):
    #print(row.diff_days)
    if row["diff_days"]!=0:
        return row["diff_days"];
    else:
        x=row["RegDate"].split("-")
        a=date(int(x[0]),int(x[1]),int(x[2]))
        b=date(2019,6,21)
        return (b-a).days
    
def target(row):
    #print(row.diff_days)
    if row["diff_days"]!=0:
        return 1
    else:
        return 0

data["total_days"]=data.apply(cal_tdays,axis=1)

#calculate average of stats fields

data["uninstall"]=data.apply(target,axis=1)


data=data.apply(lambda x: x.astype(str).str.lower())

#data["custid"]=data["custid"].drop_duplicates()

brand_data=data[["brand","appType"]]

import category_encoders as ce

encoder = ce.BinaryEncoder(cols=['brand','appType'])

brand_data = encoder.fit_transform(brand_data)


import scipy.stats as stats
from scipy.stats import chi2_contingency

cat_labels=["brand","lang_id","modle","os","reg_city","reg_network","reg_state"]

test_label="version"
for l in cat_labels:
    ab=pd.crosstab(data[test_label],data[l])
    chi2,p,dof,expected=stats.chi2_contingency(ab)
    if p<0.05:
            print("{0} and {1} are dependent(p={2})".format(test_label,l,p))
    else:
            print("{0} and {1} are independent(p={2})".format(test_label,l,p))

time_groups=["tg1","tg2","tg3","tg4"]
def avg_stats(row):
    avg_list=[];
    for tg in time_groups:
        avg_tg_sessions=float(row[tg+"_sessions"])/float(row["total_days"])
        avg_pps=float(row[tg+"_pps"])/float(row["total_days"])
        avg_tsps=float(row[tg+"_tsps"])/float(row["total_days"])
        avg_whatsappshare=float(row["whatsappshare"])/float(row["total_days"])
        avg_notification_clear=float(row["notification_clear"])/float(row["total_days"])
        avg_list.extend([avg_tg_sessions,avg_pps,avg_tsps])
    avg_whatsappshare=float(row["whatsappshare"])/float(row["total_days"])
    avg_notification_clear=float(row["notification_clear"])/float(row["total_days"])
    avg_list.extend([avg_whatsappshare,avg_notification_clear])
    return pd.Series(avg_list)
    
avd_df=data[:2].apply(avg_stats,axis=1)
# =============================================================================
# uninstall and brand are dependent(p=3.9426194787033596e-79)
# uninstall and lang_id are dependent(p=1.273163062597188e-185)
# uninstall and modle are dependent(p=1.712694998434592e-272)
# uninstall and notification_flag are dependent(p=0.0)
# uninstall and os are dependent(p=1.6708085577800736e-289)
# uninstall and reg_city are independent(p=0.5720153136072003)
# uninstall and reg_network are dependent(p=7.391116917224324e-09)
# uninstall and reg_state are dependent(p=0.006671934291278905)
# uninstall and version are dependent(p=2.3083285272153662e-240)
# =============================================================================
