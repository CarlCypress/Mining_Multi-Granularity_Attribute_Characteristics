from PreWork import *
from Parameter import *


y_hat = None
for freq in Freq_list:
    for tbtype in TABLE_TYPE_LIST:
        print('The frequent is {}, type is {}.' .format(freq, tbtype))
        data = merge_table(tbtype).reset_index(drop=True)
        subs_code = [1, 2, 3, 4]

        test_X, test_y, index = data.iloc[:, 2:], data.iloc[:, 1], data.iloc[:, 0]
        subRepDic, searchDic = get_two_dict(freq, subs_code, tbtype)

        if tbtype == 'binary':
            y_hat = test_X.apply(func=predict_1, axis=1, args=(subs_code, subRepDic,))
        else:
            y_hat = test_X.apply(func=predict_2, axis=1, args=(subs_code, subRepDic, searchDic, y_hat,))
        break_condition = all(len(sub_list) == 1 for sub_list in y_hat['subcode'])
        result = pd.concat([index, y_hat, test_y], axis=1)
        result.to_excel('result_{}.xlsx' .format(tbtype), index=False)
        print('中间结果保存完成!')

        if break_condition or tbtype == 'value':
            file_name = './result/Frequent_{}.xlsx' .format(freq)
            result.rename(columns={
                'subcode': 'predict',
                'subconcept': 'concept_num'
            }, inplace=True)
            result.to_excel(file_name, index=False)
        pass
    pass
