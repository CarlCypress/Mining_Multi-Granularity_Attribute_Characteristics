import pandas as pd
from common import *
from Parameter import *


idx = 3
df = pd.DataFrame(columns=['concept_idx', 'frequent', 'algorithm', 'binary', 'type', 'value', 'type_cnt', 'value_cnt'])
result = []
is_break = False

for frequent in Freq_list_final:
    print('concept: {}, frequent: {}'.format(idx, frequent))
    Integ_result = Integ(idx, frequent)
    Apri_result = Apri(idx, frequent)

    # print(Integ_result)
    # print(Apri_result)

    # for i in range(3):
    #     if Integ_result[i] > 1010 or Apri_result[i] > 1010:
    #         is_break = True
    #         break
    #     pass
    result.append({
        'concept_idx': idx,
        'frequent': frequent,
        'algorithm': 'Integ',
        'binary': Integ_result[0],
        'type': Integ_result[1],
        'value': Integ_result[2],
        'type_cnt': Integ_result[3],
        'value_cnt': Integ_result[4],
    })
    result.append({
        'concept_idx': idx,
        'frequent': frequent,
        'algorithm': 'Apri',
        'binary': Apri_result[0],
        'type': Apri_result[1],
        'value': Apri_result[2],
        'type_cnt': Apri_result[3],
        'value_cnt': Apri_result[4],
    })
    # if is_break:
    #     break
    # pass

df = df.append(result, ignore_index=True)
df.to_excel('concept_%d.xlsx' % idx, index=False)
