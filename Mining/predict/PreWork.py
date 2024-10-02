import warnings
import pandas as pd
from Apriori.apriori import Apriori
from ToolScript.readSql import sql_tool

warnings.filterwarnings('ignore')
yl_tool = sql_tool('YagoLast')


def merge_table(table_type) -> pd.DataFrame:
    """
    将四个概念的binary, type, value表分别合成在一起
    :return: 三元组(binary, type, value)
    """
    table = pd.DataFrame()
    for idx in range(1, 5):
        table_name = 'concept_{}_{}' .format(idx, table_type)
        table_ = yl_tool.get_table(table_name)
        table_['concept_num'] = idx
        table = pd.concat([table, table_], axis=0)
        pass
    con_list = ['instance', 'subconcept', 'concept_num']
    con = table[['instance', 'concept_num']]
    table = table.drop(columns=con_list).sort_index(axis=1)
    table = pd.concat([con, table], axis=1).fillna(0)
    table.rename(columns={
        'concept_num': 'subconcept',
    }, inplace=True)
    return table


def get_two_dict(min_frequent, subs_code, tbtype):
    subRepDic = dict()
    searchDict = dict()

    for sub in subs_code:
        apri = Apriori(min_frequent)
        data = yl_tool.get_table('concept_{}_{}' .format(sub, tbtype)).iloc[:, 2:]
        pattern = apri.predict(data)
        subRepDic[sub] = pattern
        searchDict[sub] = apri.result_all_reps()

    return subRepDic, searchDict


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
                        if reps[idx] not in str(row[cols[idx]]):
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


def find_keys_with_max_value(my_dict):
    # 找到最高值
    max_value = max(my_dict.values())

    # 找到所有具有最高值的键
    max_keys = [key for key, value in my_dict.items() if value == max_value]

    return max_keys
