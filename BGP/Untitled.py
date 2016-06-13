
# coding: utf-8

# In[1]:

import pandas as pd

# Get the delegation data from APNIC

# apnic_url = 'http://ftp.apnic.net/stats/apnic/delegated-apnic-latest'
apnic_url = 'delegated-apnic-latest'
rir = pd.read_csv(apnic_url, delimiter="|", skiprows=31,
                  names=['rir', 'cc', 'resource_type', 'resource', 'size',
                         'created', 'status'],
                  comment="#")



# In[3]:

rir.head()


# In[59]:

def test_f(a):
    s = int(a['resource'])
    n = a['size']
    return pd.DataFrame({'resource': [a for a in range(s+1, s+n)],
                         'resource_type': [a['resource_type']] * (n-1),
                        'size': [1] * (n-1)})
    # return "Happy " + str(type(a['resource']))


# In[60]:

nz_data = rir[rir['cc']=='NZ'][['resource_type', 'resource', 'size']]


# In[71]:

dlist=[]
for idx, row in nz_data.query('(resource_type=="asn") & (size>1)').iterrows():
    dlist.append(test_f(row))
    
asn_data = pd.concat(dlist + [nz_data.query('resource_type=="asn"')])


# In[72]:

from collections import defaultdict

prefixes = defaultdict(list)
for idx, row in nz_data.query('(resource_type!="asn")').iterrows():
    if row['resource_type'] == 'ipv6':
        mask = row['size']
    elif row['resource_type'] == 'ipv4':
        mask = 32 - (row['size'] - 1).bit_length()
        
    prefixes[row['resource_type']].append("%s/%s" % (row['resource'], mask))


# In[70]:

prefixes


# In[73]:

asn_data


# In[74]:

prefixes['asn'] = asn_data['resource'].tolist()


# In[75]:

prefixes


# In[ ]:



