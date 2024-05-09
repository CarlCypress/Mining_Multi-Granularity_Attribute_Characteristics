import numpy as np
from search import *
from pre_work import *
from ToolScript.readSql import sql_tool

warnings.filterwarnings('ignore')
yc_tool = sql_tool('YagoCore')

n = 10
concept_idx = 2
min_frequent = 0.007
seed_value = 42


y_hat = None
for min_frequent in Freq_list_final + [0.05, 0.007]:
    for tbtype in tbtype_list:
        table_name = 'concept_{}_{}'.format(concept_idx, tbtype)
        print(table_name)

        np.random.seed(seed_value)
        data = get_pure_table(table_name)
        print(data)
        data = data.loc[data['subconcept'].apply(lambda x: len(x) == 1), :]
        # data = data[get_cols(concept_idx, 0.2)]  # 删去一定比例的列
        subs_code = get_subcode_list(concept_idx)

        data, subs_code = filter_data_by_subs_code(data, subs_code)  # 删除低于30行的子概念

        test_idx = np.random.choice(data.index, n, replace=False)
        # test_data = data.loc[test_idx]  # 预测行
        test_data = data

        test_X, test_y, index = test_data.iloc[:, 2:], test_data.iloc[:, 1], test_data.iloc[:, 0]

        # subRepDicList, search_list = get_two_list(min_frequent, data, subs_code)
        subRepDic, searchDic = get_two_dict(min_frequent, data, subs_code)
        # dict_to_excel(searchDic, './Excel/ReCpt{}_{}' .format(concept_idx, tbtype))

        if tbtype == 'binary':
            # y_hat = test_X.apply(func=catalog_1, axis=1, args=(subs_code, subRepDicList,))
            y_hat = test_X.apply(func=predict_1, axis=1, args=(subs_code, subRepDic,))
        else:
            # y_hat = test_X.apply(func=predict_2, axis=1, args=(subs_code, subRepDicList, search_list, y_hat,))
            y_hat = test_X.apply(func=predict_2, axis=1, args=(subs_code, subRepDic, searchDic, y_hat,))

        break_condition = all(len(sub_list) == 1 for sub_list in y_hat['subcode'])
        result = pd.concat([index, y_hat, test_y], axis=1)

        if break_condition or tbtype == 'value':
            file_name = './result/concept_{}_{}.xlsx'.format(concept_idx, min_frequent)
            result.to_excel(file_name, index=False)
        pass

