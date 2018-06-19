import pandas as pd
import numpy as np

data = pd.read_excel(r'final_spo2.xlsx')

grouped_data = data.groupby('object_2')

p2p = []

# 虚构人物之间的上下级树形关系
for name,group in grouped_data:
    for i in range(group.shape[0]):
        if i+1 > 3 and i+1 < 10:
            if (i+1) % 3 == 1:
                p2p.append({'object':group.iloc[i, 2], 'relation':'下属', 'object_2':group.iloc[0, 2], 'company':name})

            elif (i+1) % 3 == 2:
                p2p.append({'object': group.iloc[i, 2], 'relation': '下属', 'object_2': group.iloc[1, 2], 'company':name})

            elif (i+1) % 3 == 0:
                p2p.append({'object': group.iloc[i, 2], 'relation': '下属', 'object_2': group.iloc[2, 2], 'company':name})

        elif i+1 > 9 :
            if  3 < (i - 5) < 10:
                p2p.append({'object': group.iloc[i, 2], 'relation': '下属', 'object_2': group.iloc[i-5, 2], 'company':name})
            elif (i - 5) > 9:
                p2p.append({'object': group.iloc[i, 2], 'relation': '下属', 'object_2': group.iloc[i-11, 2], 'company':name})


df_p2p = pd.DataFrame(p2p)


# 删除多余的人物的三元组，并存入虚构的人物之间的三元组

contain_person = []
for name,group in grouped_data:
    for i in range(group.shape[0]):
        if i < 3:
            contain_person.append(group.iloc[i, 2])


new_data = data[data['object'].isin(contain_person)]

del new_data['index']
del new_data['code']
del new_data['sex']
del new_data['birthday']
del new_data['edu']
del new_data['id']

company = pd.Series(np.zeros(new_data.shape[0]))

for i in range(new_data.shape[0]):
    company[i] = new_data.iloc[i, 2]


new_data = new_data.reset_index()

new_data2 = pd.concat([new_data, company], axis=1)
new_data2.rename(columns={0:'company'}, inplace=True)
del new_data2['index']


final_data = pd.concat([df_p2p, new_data2])
print(final_data)

final_data.to_excel(r'C:\Users\jiang\Desktop\cj_try\final_spo.xlsx')

