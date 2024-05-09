import pandas as pd
from pre_work import *
from Apriori.apriori import Apriori
from pre_work import get_all_max_indices

tbtype_list = ['binary', 'type', 'value']


def catalog_1(row, subs_code, subRepDicList, return_type='subcode') -> pd.Series:
    sub_grade = [-1 for i in range(len(subs_code) + 1)]
    for sub in subs_code:
        patterns = subRepDicList[sub]  # 此处可以更改为dict
        grade = 0
        for grade_idx in range(1, len(patterns)):
            for ptn in patterns[grade_idx]:
                cols = ptn.split(',')
                is_plus_grade = True
                for col in cols:
                    if row[col] in {0, '0'}:
                        is_plus_grade = False
                if is_plus_grade:
                    grade += grade_idx
                pass
            pass
        sub_grade[sub] = grade
    if return_type == 'subcode':
        return pd.Series({
            'subcode': get_all_max_indices(sub_grade)
        })
    elif return_type == 'grade':
        return pd.Series({
            'grade': sub_grade[1:]
        })
    else:
        return pd.Series({
            'subcode': get_all_max_indices(sub_grade),
            'grade': sub_grade[1:]
        })


def predict_1(row, subs_code, subRepDic, return_type='subcode') -> pd.Series:
    """
    对概念的Binary表进行预测，主要依据为根据该行对应的频繁模式是否都是1，并且返回对应的分数
    :param row: 待预测的行
    :param subs_code: 需要预测的子概念编号
    :param subRepDic: 每个子概念存放的频繁模式
    :param return_type: 'subcode', 'grade', 'all'
    :return:
    """
    sub_grade = dict()
    for sub in subs_code:
        patterns = subRepDic[sub]
        grade = 0
        for grade_idx in range(1, len(patterns)):
            for ptn in patterns[grade_idx]:
                cols = ptn.split(',')
                is_plus_grade = True
                for col in cols:
                    if row[col] in {0, '0'}:
                        is_plus_grade = False
                if is_plus_grade:
                    grade += grade_idx
                pass
            pass
        sub_grade[sub] = grade
        # print(sub_grade)
    if return_type == 'subcode':
        return pd.Series({
            'subcode': find_keys_with_max_value(sub_grade)
        })
    elif return_type == 'grade':
        return pd.Series({
            'grade': sub_grade[1:]
        })
    else:
        return pd.Series({
            'subcode': find_keys_with_max_value(sub_grade),
            'grade': sub_grade[1:]
        })


def catalog_2(row, subs_code, subRepDicList, search_list, trace_ans=None, return_type='subcode',) -> pd.Series:

    sub_grade = [-1 for i in range(len(subs_code) + 1)]
    for sub in subs_code:
        patterns = subRepDicList[sub]
        sub_represents = search_list[sub]
        grade = 0
        for grade_idx in range(1, len(patterns)):
            for ptn in patterns[grade_idx]:
                cols = ptn.split(',')
                marking_list = sub_represents[ptn]
                for represent in marking_list:
                    reps = represent.split(',')
                    is_plus_grade = True
                    for idx in range(len(cols)):
                        if reps[idx] not in row[cols[idx]]:
                            is_plus_grade = False
                            break
                    if is_plus_grade:
                        grade += grade_idx
                    pass
                pass
            pass
        sub_grade[sub] = grade
        pass
    sub_code = get_all_max_indices(sub_grade)
    if trace_ans is not None:
        trace_ans = trace_ans.loc[row.name, 'subcode']
        if len(trace_ans) == 1:
            sub_code = trace_ans
        else:
            set1 = set(sub_code)
            set2 = set(trace_ans)

            sub_code = sorted(set1.intersection(set2))
            pass

    if return_type == 'subcode':
        return pd.Series({
            'subcode': sub_code
        })
    elif return_type == 'grade':
        return pd.Series({
            'grade': sub_grade[1:]
        })
    else:
        return pd.Series({
            'subcode': sub_code,
            'grade': sub_grade[1:]
        })


def predict_2(row, subs_code, subRepDic, searchDic, trace_ans=None, return_type='subcode',) -> pd.Series:

    sub_grade = dict()
    for sub in subs_code:
        patterns = subRepDic[sub]
        sub_represents = searchDic[sub]
        grade = 0
        for grade_idx in range(1, len(patterns)):
            for ptn in patterns[grade_idx]:
                cols = ptn.split(',')
                marking_list = sub_represents[ptn]
                for represent in marking_list:
                    reps = represent.split(',')
                    is_plus_grade = True
                    for idx in range(len(cols)):
                        if reps[idx] not in row[cols[idx]]:
                            is_plus_grade = False
                            break
                    if is_plus_grade:
                        grade += grade_idx
                    pass
                pass
            pass
        sub_grade[sub] = grade
        # print(sub_grade)
        pass
    sub_code = find_keys_with_max_value(sub_grade)
    if trace_ans is not None:
        trace_ans = trace_ans.loc[row.name, 'subcode']
        if len(trace_ans) == 1:
            sub_code = trace_ans
        else:
            set1 = set(sub_code)
            set2 = set(trace_ans)

            sub_code = sorted(set1.intersection(set2))
            pass

    if return_type == 'subcode':
        return pd.Series({
            'subcode': sub_code
        })
    elif return_type == 'grade':
        return pd.Series({
            'grade': sub_grade[1:]
        })
    else:
        return pd.Series({
            'subcode': sub_code,
            'grade': sub_grade[1:]
        })


def get_two_list(min_frequent, data, subs_code):
    subRepDicList = [None for i in range(len(subs_code) + 1)]
    search_list = [None for i in range(len(subs_code) + 1)]

    for sub in subs_code:
        apri = Apriori(min_frequent)
        st = data.apply(lambda x: str(sub) in x['subconcept'], axis=1)
        sub_data = data.loc[st, :].iloc[:, 2:]

        pattern = apri.predict(sub_data)
        subRepDicList[sub] = pattern
        search_list[sub] = apri.result_all_reps()

    return subRepDicList, search_list


def get_two_dict(min_frequent, data, subs_code):
    subRepDic = dict()
    searchDict = dict()

    for sub in subs_code:
        apri = Apriori(min_frequent)
        st = data.apply(lambda x: str(sub) in x['subconcept'], axis=1)
        sub_data = data.loc[st, :].iloc[:, 2:]

        pattern = apri.predict(sub_data)
        subRepDic[sub] = pattern
        searchDict[sub] = apri.result_all_reps()

    return subRepDic, searchDict


def dropTopCols(df, percentage_to_drop=0.2) -> pd.DataFrame:
    # 去除 'instance' 和 'subconcept' 列
    df_numeric = df.drop(['instance', 'subconcept'], axis=1)

    # 初始化一个字典用于存储每一列的非零元素集合
    column_values = {}

    # 遍历每一列，统计非零且不同元素的个数
    for column in df_numeric.columns:
        values = set()
        for value in df_numeric[column]:
            values.update(filter(lambda x: x != '0', value.split(',')))
        column_values[column] = values

    # 找出代表元素最多的一定百分比的列
    total_columns = len(df_numeric.columns)
    columns_to_drop = int(total_columns * percentage_to_drop)

    sorted_columns = sorted(column_values.items(), key=lambda x: len(x[1]), reverse=True)
    columns_to_drop = [col[0] for col in sorted_columns[:columns_to_drop]]

    # 从DataFrame中删除需要丢弃的列
    df_filtered = df.drop(columns=columns_to_drop)

    return df_filtered


def get_cols(concept_idx, drop_percent=0.2):
    data = get_pure_table('concept_{}_value' .format(concept_idx))
    return dropTopCols(data, drop_percent).columns
