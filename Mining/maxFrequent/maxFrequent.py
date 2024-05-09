import time
import numpy as np
import pandas as pd
from Parameter import FREQUENT
from Apriori.apriori import Apriori


class maxFrequent(Apriori):
    """
    最大频繁模式的挖掘类
    """

    def __init__(self, min_frequent=FREQUENT, is_debug=False):
        super().__init__(min_frequent, is_debug)
        self.min_frequent = min_frequent  # 最小频率
        self.data = None  # 需要进行挖掘的数据表
        self.mfreq_pattern = None  # 可能为最大频繁度的模式，作为降解的起点频繁模式
        self.detect_pattern_list = None  # 待检测的频繁模式列表
        self.record_pattern_list = None  # 确认为频繁的模式进行记录
        self.repres_dict = None  # 保存data每一列的代表元素
        self.temp_keys = None
        self.is_debug = is_debug  # debug tool

    def direct_to_max_pattern(self) -> str:
        """
        单独计算每一个属性的频率，将所有满足条件的属性列拼凑起来
        :return: 拼凑的可能为最大频繁模式的属性列
        """
        def func(series) -> bool:
            """
            针对遍历self.data的每一列元素，分别计算其每一列的频繁模式
            :param series: self.data的某一列
            :return: True表示该列频率>=FREQUENT
            """
            col_name = series.name
            for reps in self.repres_dict[col_name]:
                frequent = series.apply(lambda x: reps in str(x) if x != 0 and x != '0' else False).sum() / series.shape[0]
                # print('debug:', col_name, reps, frequent)
                if frequent >= self.min_frequent:
                    return True
            return False
        res = self.get_p(self.data.columns[self.data.apply(func, axis=0)])
        return res

    def decomposition_pattern(self, pattern: str) -> list:
        """
        将pattern分解为低一阶的且不存在待检测列表中的子模式。
        :param pattern: 需要分解的模式
        :return: 所有分解的子模式所构成的list
        """
        cols = pattern.split(',')
        grade = len(cols)
        res = list()

        for col in cols:
            backup = cols.copy()
            backup.remove(col)
            lptn = self.get_p(backup)  # lptn: low pattern
            if lptn not in self.detect_pattern_list[grade - 1]:
                res.append(lptn)
                pass
            pass
        return res

    def find_freq_pattern(self, mfreq_pattern_list: list) -> list:
        """
        将mfreq_pattern_list当中的模式作为起点，判断其联合频率是否>=min_frequent。
        若满足条件，则记录下来，否则将其分解成低一阶频繁模式加入下一次待判断序列，直到无法分解。
        :param mfreq_pattern_list: 最大待定频繁模式
        :return: 所有真正的频繁模式所构成的list
        """
        res = list()
        self.detect_pattern_list = mfreq_pattern_list
        # 从高到低阶依次遍历
        for idx in range(len(self.detect_pattern_list) - 1, 0, -1):
            t_pattern = list()
            # 当前阶的每一个'高'阶疑似频繁模式
            # hptn: high pattern
            if self.is_debug:
                print('debug: {}.' .format(self.detect_pattern_list[idx]))
            for hptn in self.detect_pattern_list[idx]:
                # 若当前为频繁模式
                if self.comb_freq(hptn.split(',')):
                    # 进行记录
                    t_pattern.append(hptn)
                    pass
                else:
                    # print('count')
                    # 将高阶频繁模式进行分解(除1阶无法进行分解)
                    if idx == 1:
                        continue
                    # lptn: low pattern
                    lptn_list = self.decomposition_pattern(hptn)
                    self.detect_pattern_list[idx - 1] += lptn_list  # 加入待检测序列
                    pass
                pass
            res.append(sorted(t_pattern))
            pass
        res.append(None)
        res.reverse()
        return res

    def init_detect_pattern_list(self, init_list=None):
        """
        对self.detect_pattern_list进行初始化，方便向下挖掘
        优化：对于待检测的频繁模式当中，若存在无代表元素的频繁项，直接删去，并将该频繁模式移动到对应的阶数列表
        :param init_list: None或list，若为None使用self.mfreq_pattern进行初始化，否则使用init_list进行初始化
        :return: None
        """
        if init_list is None:
            if self.mfreq_pattern is None:
                self.detect_pattern_list = [None]
                return
            cols = self.mfreq_pattern.split(',')
            record = list()
            for col in cols:
                if len(self.repres_dict[col]) > 0:
                    record.append(col)
            length = len(record)
            self.mfreq_pattern = self.get_p(record)
            self.detect_pattern_list = [None if i == 0 else [] for i in range(length)] + [[self.mfreq_pattern]]
            return

        # 以下的操作目的为，将待检测的频繁模式中存在的不必要的col去除
        self.detect_pattern_list = [list() if i != 0 else None for i in range(len(init_list))]
        for grade in range(len(init_list) - 1, 0, -1):
            ptn_list = init_list[grade]
            if grade == 1:
                # 因为不存在将其进行分解的动作，故对于1阶进行特殊处理。
                for ptn in ptn_list:
                    if len(self.repres_dict[ptn]) > 0:
                        if ptn not in self.detect_pattern_list[grade]:
                            self.detect_pattern_list[grade].append(ptn)
                    pass
                continue
            for ptn in ptn_list:
                # 将ptn频繁模式中不存在代表元素的col去除
                # checked_grade 为剩余组成频繁模式的阶数, checked_ptn 为组成的频繁模式
                checked_grade, checked_ptn = self.get_exist_ptn(ptn)
                if checked_grade > 0:
                    if checked_ptn not in self.detect_pattern_list[checked_grade]:
                        self.detect_pattern_list[checked_grade].append(checked_ptn)
                    pass
                pass
            pass
        # self.detect_pattern_list = init_list

    def get_exist_ptn(self, pattern: str):
        """
        检测当前pattern的每个分量是都存在代表元素
        :param pattern: 待检测的频繁模式
        :return: 返回仅存在代表元素分量所组合的频繁模式
        """
        cols = pattern.split(',')
        res = list()
        for col in cols:
            if len(self.repres_dict[col]) > 0:
                res.append(col)
        return len(res), self.get_p(res)  # special: return (0, None)

    def stack_use(self, X: pd.DataFrame, mfreq_list, ans_type=0) -> list:
        """
        此方法与self.predict基本一样，区别在于使用自定义的self.mfreq_pattern
        :param X: 需要进行最大频繁模式挖掘的数据
        :param mfreq_list: 自定义的最大频繁模式列表
        :param ans_type: 返回结果的类型。0:原始结果; 1:去包含处理后的结果。
        :return: 频繁模式
        """
        start_time = time.time()
        self.data = X.copy()
        self.get_data_representative()
        print(self.repres_dict)

        self.init_detect_pattern_list(mfreq_list)
        res = self.find_freq_pattern(self.detect_pattern_list)
        end_time = time.time()
        self.runtime = end_time - start_time

        if ans_type == 0:
            return res
        else:
            return self.de_include_pattern(res)

    def predict(self, X: pd.DataFrame, ans_type=0) -> list:
        """
        该类的执行方法
        :param ans_type: 返回结果的类型。0:原始结果; 1:去包含处理后的结果。
        :param X: 需要进行最大频繁模式挖掘的数据
        :param ans_type: 返回结果的类型。0:原始结果; 1:去包含处理后的结果。
        :return: 频繁模式
        """
        start_time = time.time()
        self.data = X.copy()

        # 得到data每一列的代表元素
        self.get_data_representative()
        # 直接计算每一个属性列的频率，并将单独满足条件的属性直接拼凑起来
        self.mfreq_pattern = self.direct_to_max_pattern()
        # if self.is_debug:
        #     print('debug:', self.mfreq_pattern)
        self.init_detect_pattern_list()
        res = self.find_freq_pattern(self.detect_pattern_list)
        end_time = time.time()
        self.runtime = end_time - start_time

        if ans_type == 0:
            return res
        else:
            return self.de_include_pattern(res)
