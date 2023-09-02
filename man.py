

import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt

plan=pd.read_excel('Plan.xlsx')
prod=pd.read_excel('Prduction.xlsx')
stock=pd.read_excel('stock.xlsx')

stock.head()

group_stock = stock.groupby('Material').agg({'Unrestricted': 'sum', 'Quality Inspection': 'sum'})

group_stock['net stock'] = group_stock['Unrestricted'] + group_stock['Quality Inspection']

group_stock.head(10)

prod2=prod.drop(columns=['Material Desc','Comp-Desc'])

prod2.head()

prod2['com per unit']=prod2['Comp-Qty']/prod2['Base Qty']
prod2.head()

group_stock.head()

plan2=plan.drop(columns='Material Desc')

comp_prod=prod2['Component'].unique()

group_stock.reset_index(inplace=True)

comp_stock=group_stock.Material.unique()

added_comp=list(set(comp_prod)-set(comp_stock))

added_comp

rows_to_add = [{'Material': comp, 'net stock': 0} for comp in added_comp]
group_stock = pd.concat([group_stock, pd.DataFrame(rows_to_add)], ignore_index=True)

group_stock.tail(15)

# for comp in added_comp:
#   group_stock=group_stock.append({'Material': comp, 'net stock': 0},ignore_index=True)

group_stock.tail(10)

group_stock=group_stock.rename(columns={'net stock': 'initial stock'})

group_stock['current stock']=group_stock['initial stock'].copy()
group_stock.head()

plan2['Net Pack']=plan2['Net Pack'].fillna(0)

#plan2['fg_alloted']=0

plan2[plan2['SKU']=='HT10DS1LVDFL']

plan2 = plan2.assign(Remarks=np.nan)
#plan2.head()

plan2 = plan2.assign(Shortage=np.nan)
#plan2.head()

group_stock['net req']=0
group_stock['Cumulative Shortage']=0

group_stock.head()

history = pd.DataFrame()
for i in range(len(plan2)):
  fg=plan2.loc[i,'SKU']
  fg_q=plan2.loc[i,'Plan Qty']
  prod_fg=prod2.query("Material==@fg").copy()

  #print(i,fg,len(prod_fg))
  prod_fg.loc[:,'req']=fg_q*(prod_fg['com per unit'])
  prod_fg= pd.merge(prod_fg, group_stock, left_on='Component', right_on='Material', how='left')
  prod_fg=prod_fg.loc[:,('Material_x','Base Qty','Component','Comp-Qty','com per unit','req','initial stock','current stock')]
  prod_fg['stock before allocation']=prod_fg['current stock'].copy().values
  if len(prod_fg)>0:

    if (prod_fg['current stock'] - prod_fg['req'] >= 0 ).all():
      prod_fg['current stock'] -= prod_fg['req']
    #print('I am in if conjdition')
    #print('fg_q=',fg_q)
     # Update current stock
      plan2.loc[i,'Net Pack']=fg_q
      plan2.loc[i,'Remarks']='Fully Alloted'
    else:
    # Compute fg_possible using the formula (1 / com per unit) * current stock
      prod_fg['fg_possible'] = (1 / prod_fg['com per unit']) * prod_fg['current stock']
      shortage_df = prod_fg[prod_fg["req"] > prod_fg["stock before allocation"]]
      shortage_quantity = shortage_df["req"] - shortage_df["stock before allocation"]
      shortage_string = "-".join([f"({component})" for component, shortage in zip(shortage_df["Component"], shortage_quantity)])
      list1=list(shortage_df['Component'])
      list2=list(shortage_quantity)

    # Compute the minimum value of fg_possible
      min_fg_possible = prod_fg['fg_possible'].min()
      base_qnt=prod_fg.loc[0,'Base Qty']

    #min_fg_possible=int(min_fg_possible/base_qnt)*base_qnt

    # Update current stock using the formula current stock = current stock - min(fg_possible) * (com per unit)
      prod_fg['current stock'] -= min_fg_possible * prod_fg['com per unit']
      plan2.loc[i,'Net Pack']=min_fg_possible
      plan2.loc[i,'Remarks']='Partial Alloted('+str(round((min_fg_possible/fg_q)*100,2))+'%)'
      plan2.loc[i,'Shortage']=shortage_string
      #group_stock.loc[group_stock['Material'] == list_1[i], 'Cumulative Shortage']+=
    #print('I am in else condition','fg is',min_fg_possible)
    #merged_df = pd.merge( group_stock,prod_fg, left_on='Material', right_on='Component', how='left')
  else:
      plan2.loc[i,'Remarks']='FG not found in BOM file'

  prod_fg['stock after allocation']=prod_fg['current stock'].copy().values
  list_1=list(prod_fg['Component'])
  list_2=list(prod_fg['current stock'])
  list_3=list(prod_fg['req'])

  prod_fg.drop(columns='current stock',inplace=True)
  #print(prod_fg)
  #print(list_1,list_2)
  for i in range(len(list_1)):
    group_stock.loc[group_stock['Material'] == list_1[i], 'current stock'] = list_2[i]
    group_stock.loc[group_stock['Material'] == list_1[i], 'net req']+=list_3[i]
    #group_stock.loc[group_stock['Material'] == list_1[i], 'Cumulative Shortage']+=
# Update the 'current stock' column in the original dataframe with the values from the filtered dataframe
    #group_stock['current stock'] = merged_df['current stock']
  #print(prod_fg)
  history = pd.concat([history, prod_fg])
  #history = history.append(prod_fg)

group_stock['Cumulative Shortage']=-(group_stock['initial stock']-group_stock['net req'])
group_stock['Cumulative Shortage'] = np.where(group_stock['Cumulative Shortage'] < 0, np.nan, group_stock['Cumulative Shortage'])


plan2.insert(1,'Material Desc',plan['Material Desc'])





history.to_excel('alloting_process.xlsx',index=True)

group_stock.to_excel('updated_stock.xlsx',index=True)

plan2.to_excel('updated_plan.xlsx',index=True)
