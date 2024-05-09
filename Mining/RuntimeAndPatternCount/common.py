import warnings
from Parameter import *
from ToolScript.readSql import sql_tool
from Apriori.apriori import Apriori
from maxFrequent.maxFrequent import maxFrequent

warnings.filterwarnings('ignore')
yc_tool = sql_tool('YagoCore')


def Integ(concept_idx: int, frequent: float, return_type='pattern') -> list:
    binary_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[0]
    type_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[1]
    value_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[2]

    Binary = yc_tool.get_table(binary_name).iloc[:, 2:]
    Type = yc_tool.get_table(type_name).iloc[:, 2:]
    Value = yc_tool.get_table(value_name).iloc[:, 2:]

    apri = Apriori(frequent)
    Binary_result_ls = apri.predict(Binary, ans_type=2)
    Binary_result = Binary_result_ls[0]
    Binary_runtime = apri.runtime

    mfq_1 = maxFrequent(frequent)
    Type_result = mfq_1.stack_use(Type, Binary_result_ls[1], ans_type=0)
    Type_runtime = mfq_1.runtime

    mfq_2 = maxFrequent(frequent)
    Value_result = mfq_2.stack_use(Value, Type_result, ans_type=0)
    Value_runtime = mfq_2.runtime

    if return_type == 'pattern':
        binary_cnt = [len(plist) for plist in Binary_result[1:]]
        type_cnt = [len(plist) for plist in Type_result[1:]]
        value_cnt = [len(plist) for plist in Value_result[1:]]
        return [Binary_result[1:], Type_result[1:], Value_result[1:], sum(type_cnt), sum(value_cnt)]
    else:
        return [Binary_runtime, Type_runtime, Value_runtime, Binary_runtime + Type_runtime + Value_runtime]


def Apri(concept_idx: int, frequent: float, ans_type=0, return_type='pattern') -> list:
    binary_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[0]
    type_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[1]
    value_name = 'concept_%d_' % concept_idx + TABLE_TYPE_LIST[2]

    Binary = yc_tool.get_table(binary_name).iloc[:, 2:]
    Type = yc_tool.get_table(type_name).iloc[:, 2:]
    Value = yc_tool.get_table(value_name).iloc[:, 2:]

    apri_1 = Apriori(frequent)
    Binary_result = apri_1.predict(Binary, ans_type=ans_type)
    Binary_runtime = apri_1.runtime

    apri_2 = Apriori(frequent)
    Type_result = apri_2.predict(Type, ans_type=ans_type)
    Type_runtime = apri_2.runtime

    apri_3 = Apriori(frequent)
    Value_result = apri_3.predict(Value, ans_type=ans_type)
    Value_runtime = apri_3.runtime

    if return_type == 'pattern':
        binary_cnt = [len(plist) for plist in Binary_result[1:]]
        type_cnt = [len(plist) for plist in Type_result[1:]]
        value_cnt = [len(plist) for plist in Value_result[1:]]
        return [Binary_result[1:], Type_result[1:], Value_result[1:], sum(type_cnt), sum(value_cnt)]
    else:
        return [Binary_runtime, Type_runtime, Value_runtime, Binary_runtime + Type_runtime + Value_runtime]

