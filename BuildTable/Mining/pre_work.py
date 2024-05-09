import math
import json
import warnings
import pandas as pd
from Parameter import *
from ToolScript.readSql import sql_tool
from Apriori.apriori import Apriori
from maxFrequent.maxFrequent import maxFrequent

warnings.filterwarnings('ignore')

yc_tool = sql_tool('YagoCore')


def get_subcode_list(concept_idx: int) -> list:
    """
    获得concept_idx的子概念列表
    :param concept_idx: 需要获得概念编号
    :return: 子概念列表
    """
    table_name = 'concept_%d_subconcept_code' % concept_idx
    return sorted(yc_tool.get_table(table_name)['code'].values.astype('int').tolist())


def get_pure_table(table_name: str, is_reverse=False) -> pd.DataFrame:
    """
    获得概念表除subconcept只有-1所在的行, 或者仅仅获取-1所在的所有行
    :param table_name: 概念表名称
    :param is_reverse: True表示上述的前者，反之后者
    :return: 返回获取的表
    """
    table = yc_tool.get_table(table_name)
    table.sort_values(by='instance', inplace=True)
    # 在原始DataFrame上重置索引
    table.reset_index(drop=True, inplace=True)
    st = table.apply(lambda x: '-1' in x['subconcept'], axis=1)

    if is_reverse:
        return table.loc[st, :]
    return table.loc[~st, :]


def filter_data_by_subs_code(data, subs_code, threshold=30):
    # 创建data的副本
    filtered_data = data.copy()

    # 将subs_code转换为集合
    subs_code_set = set(subs_code)

    # 将subconcept列的字符串转换为列表
    filtered_data['subconcept'] = filtered_data['subconcept'].apply(lambda x: [int(i) for i in str(x).split(',')])

    # 统计subs_code中的所有值在data中的行数
    subs_code_counts = {}
    for code in subs_code_set:
        subs_code_counts[code] = sum(filtered_data['subconcept'].apply(lambda x: code in x))

    # 将低于阈值的值从data中删除，同时删除对应的subs_code中的值
    for code, count in subs_code_counts.items():
        if count < threshold:
            filtered_data = filtered_data[filtered_data['subconcept'].apply(lambda x: code not in x)]
            subs_code_set.remove(code)

    filtered_data['subconcept'] = filtered_data['subconcept'].apply(lambda x: ','.join(map(str, x)))

    return filtered_data, list(subs_code_set)


def get_subs_table(concept_idx: int, is_reverse=False) -> list:
    binary_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[0]
    type_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[1]
    value_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[2]

    Binary = get_pure_table(binary_name, is_reverse=is_reverse)
    Type = get_pure_table(type_name, is_reverse=is_reverse)
    Value = get_pure_table(value_name, is_reverse=is_reverse)

    return [Binary.iloc[:, 2:], Type.iloc[:, 2:], Value.iloc[:, 2:]]


def get_sub_table(concept_idx: int, sub_code: int) -> list:
    binary_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[0]
    type_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[1]
    value_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[2]

    Binary = get_pure_table(binary_name)
    Type = get_pure_table(type_name)
    Value = get_pure_table(value_name)
    st = Binary.apply(lambda x: str(sub_code) in x['subconcept'], axis=1)
    Binary = Binary.loc[st, :]
    st = Type.apply(lambda x: str(sub_code) in x['subconcept'], axis=1)
    Type = Type.loc[st, :]
    st = Value.apply(lambda x: str(sub_code) in x['subconcept'], axis=1)
    Value = Value.loc[st, :]

    return [Binary.iloc[:, 2:], Type.iloc[:, 2:], Value.iloc[:, 2:]]


def adjust_frequent(concept_idx: int, frequent: int, rows: int) -> float:
    sub_code_list = get_subcode_list(concept_idx)
    min_rows = 99999
    for sub_code in sub_code_list:
        Binary, Type, Value = get_sub_table(concept_idx, sub_code)
        min_rows = min([min_rows, math.ceil(Binary.shape[0] * frequent)])
    return min_rows / rows


def Apri(Binary: pd.DataFrame, Type: pd.DataFrame, Value: pd.DataFrame, frequent: float) -> list:

    apri_1 = Apriori(frequent)
    apri_1.predict(Binary, ans_type=1)
    Binary_runtime = apri_1.runtime

    apri_2 = Apriori(frequent)
    apri_2.predict(Type, ans_type=1)
    Type_runtime = apri_2.runtime

    apri_3 = Apriori(frequent)
    apri_3.predict(Value, ans_type=1)
    Value_runtime = apri_3.runtime

    return [Binary_runtime, Type_runtime, Value_runtime, Binary_runtime + Type_runtime + Value_runtime]


def Integ(Binary: pd.DataFrame, Type: pd.DataFrame, Value: pd.DataFrame, frequent: float) -> list:
    apri = Apriori(frequent)
    Binary_result = apri.predict(Binary, ans_type=1)
    Binary_runtime = apri.runtime

    mfq_1 = maxFrequent(frequent)
    Type_result = mfq_1.stack_use(Type, Binary_result, ans_type=1)
    Type_runtime = mfq_1.runtime

    mfq_2 = maxFrequent(frequent)
    Value_result = mfq_2.stack_use(Value, Type_result, ans_type=1)
    Value_runtime = mfq_2.runtime

    return [Binary_runtime, Type_runtime, Value_runtime, Binary_runtime + Type_runtime + Value_runtime]


def get_all_max_indices(lst):
    if not lst:
        raise ValueError("列表不能为空")

    max_value = max(lst)
    max_indices = [i for i, value in enumerate(lst) if value == max_value]
    return max_indices


def find_keys_with_max_value(my_dict):
    # 找到最高值
    max_value = max(my_dict.values())

    # 找到所有具有最高值的键
    max_keys = [key for key, value in my_dict.items() if value == max_value]

    return max_keys


def save_dict_to_file(my_dict, file_path):
    """
    将字典保存到文本文件中

    Parameters:
    - my_dict: 要保存的字典
    - file_path: 保存文件的路径
    """
    # 将字典转换为JSON字符串
    json_string = json.dumps(my_dict, indent=2)

    # 将JSON字符串写入文件
    with open(file_path, 'w') as file:
        file.write(json_string)


def dict_to_excel(input_dict, output_path):
    df = pd.DataFrame(input_dict)
    # Save the DataFrame to an Excel file in the specified directory
    df.to_excel(f"{output_path}.xlsx", index_label="pattern")
