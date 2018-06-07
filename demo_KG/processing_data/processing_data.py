import pandas as pd
import numpy as np

cninfo_data = pd.read_csv(r'C:\Users\jiang\Desktop\tutorial2\cninfo2.csv')
cninfo_data = cninfo_data.sort_values('code')
cninfo_data = cninfo_data.reset_index()
del cninfo_data['index']

after_data = cninfo_data.drop_duplicates(['name', 'sex', 'birthday'], keep='first')
person = after_data.iloc[:, 1:]
person = person.reset_index()
del person['index']

sign_cninfo = cninfo_data.duplicated(['name', 'sex', 'birthday'], keep=False)

same_one = cninfo_data[sign_cninfo]
same_one = same_one.sort_values('name')

id = list(range(1, same_one.shape[0] + 1))
id[1] = 2
e = 1

for i in range(same_one.shape[0]):
    for j in range(i+1, same_one.shape[0]):
        if same_one.iloc[i, 1] == same_one.iloc[j, 1]:
            id[j] = id[i]
    e += 1
    
id = pd.Series(id) 
id.to_csv(r'C:\Users\jiang\Desktop\tutorial2\id.csv')
same_one.to_csv(r'C:\Users\jiang\Desktop\tutorial2\same_one.csv')

print(same_one)


droped_cninfo = cninfo_data.drop_duplicates(['name', 'sex', 'birthday'], keep=False)

droped_cninfo.to_csv(r'C:\Users\jiang\Desktop\tutorial2\drop_cninfo.csv')






def drop_same_person(data, nature=['name', 'sex', 'birthday']):
    after_data = data.drop_duplicates(nature, keep='first')
    person = after_data.iloc[:, 1:]
    person = person.reset_index()
    del person['index']
    person.to_csv(r'C:\Users\jiang\Desktop\tutorial2\person.csv')
    return


def spo_data(person, cninfo_data):
    pass


#if __name__ == '__main__':
#    cninfo_data = pd.read_csv(r'C:\Users\85751\Desktop\tutorial\cninfo2.csv')
#    cninfo_data = cninfo_data.sort_values('code')
#    cninfo_data = cninfo_data.reset_index()
#    del cninfo_data['index']

#    drop_same_person(cninfo_data)
