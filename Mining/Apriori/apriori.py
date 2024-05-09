import json
import time
import copy
import numpy as np
import pandas as pd
from Parameter import FREQUENT


class Apriori:
    """此类实现Apriori算法，
    针对于 binary, type, value 表各自代表元素的不同，此类尽可能地实现形式上的统一。
    Note: FREQUENT 为最小频率阈值, mining_pattern 表示具体挖掘表的类型
    """

    def __init__(self, min_frequent=FREQUENT, is_debug=False):
        """
        apriori 的构造函数
        :param min_frequent: 最小阈值
        :param is_debug: 是否打印一些东西, 以帮助查看运行过程
        """
        self.min_frequent = min_frequent  # 最小频率
        self.S = None  # 逻辑上S为集合，物理上是一个np.array类型
        self.T = None  # 逻辑上T为集合，物理上是一个np.array类型
        self.data = None  # 需要分析的数据
        self.cols_data = None  # 需要检测的数据列(频率计算)
        self.repres_dict = None  # 保存data每一列的代表元素
        self.temp_keys = None  # 存放需要dfs的列名
        self.grid_result = None  # 保存完全dfs所有符合条件的结果
        self.ans = [None]  # 每一阶的关联度分析结果，下标为0使用None进行占位
        self.pure_ans = None  # 将self.ans去包含处理后的结果
        self.runtime = None  # 除去预处理外的运行时间
        self.is_debug = is_debug  # debug tool

    def check_this_tuple(self, arr):
        """arr中存放self.key_arr每列的代表元素
        """
        temp_need = pd.DataFrame.copy(self.cols_data, deep=True)  # 需要深拷贝，以防止二维数组中的元素为 list 时，修改值产生连带反应

        def t_func(series):
            """series相当于matrix的某一行，此函数的作用为：
            self.temp_keys 对应的列中的元素必须同时存在 arr 中的代表元素
            """
            for idx in range(len(self.temp_keys)):
                if arr[idx] not in str(series[self.temp_keys[idx]]):  # 只要有一个 self.key_arr 列中不存在该列的某个代表元素，就返回False
                    return False
            return True

        # 遍历每行，同时将每行按照 t_func 函数进行操作(axis=1表示竖向遍历)
        frequent = temp_need.apply(t_func, axis=1).sum() / temp_need.shape[0]  # 除数为总行数，计算结果为频率值

        # 以前的实验没有加等号，后又加入，可能导致部分数据稍有不同
        if frequent >= self.min_frequent:
            return True
        return False

    def dfs(self, check_arr, idx) -> bool:
        """
        遍历self.repres_dict中的所有代表元素元组
        dfs顺序为，idx从小到大，依次遍历第 self.temp_key[idx] 列，
        而 self.temp_key[idx] 中的代表元素存放在 self.repres_dic 中。
        因此，依次遍历 self.temp_key[idx] 中的元素即可(每次取出idx中的一个保存下来)。
        :param is_debug: debug tool
        :param check_arr: 存放搜索到的代表元素
        :param idx: 搜索到的第i个代表元素
        :return: bool 表示check_arr的频率>=FREQUENT
        """
        if idx == len(self.temp_keys):
            # if self.is_debug:
            #     print('debug:', check_arr)
            if self.check_this_tuple(check_arr):
                # print('debug:', self.temp_keys)
                return True
            return False

        idx_repres = self.repres_dict[self.temp_keys[idx]]
        for rep in idx_repres:
            check_arr.append(rep)
            if self.dfs(check_arr, idx + 1):
                return True
            check_arr.pop()
            # 这里不要使用remove, 否则达不到还原现场的效果
        return False

    def comb_freq(self, columns: list) -> bool:
        """
        判断data中的数据的columns列计算其代表元素中联合频率是否存在>=FREQUENT
        :param is_debug: debug tool
        :param columns: 需要进行查看联合频率的列名
        :return: bool, True表示存在一个代表元素组其联合频率>=FREQUENT
        """
        # length = len(columns)
        self.cols_data = self.data[columns]  # 取出需要计算频率的列
        self.temp_keys = columns  # 保存这些列名，方便dfs

        # print('debug:', columns)
        if self.dfs([], 0):
            # print('debug:', columns)
            return True
        return False

    def check_cols(self):
        """查看集合S中AND操作后符合条件的列，
        返回为一个bool类型的np.array，以方便对其进行切片操作
        """
        res = np.array([], dtype=np.bool)
        for col in self.S:  # 挨个遍历S中的元素
            cols = col.split(',')  # 对其元素(频繁模式列名)使用 ',' 进行split，对其每个分解的元素对应的列明进行AND操作
            # 如果AND操作后的 1 的数量 符合阈值，则往res中添加True，否则False
            res = np.append(res, self.comb_freq(cols))
            # res = np.append(res, self.AND(cols) >= FREQUENT)
        return res

    def get_p(self, array: np.array):
        """将array中的所有数字字符串通过中间加','的方式拼接起来
        """
        res = ",".join(map(str, array))
        if len(res) == 0:
            return None
        return res

    def check_set(self, s):
        """查看组成的新的高阶s组合是否符合要求"""
        length = s.shape[0]
        for idx in range(length):
            # 利用delete依次删一个元素，并查看其子元素是否在集合T中
            # print('debug:', self.get_p(np.delete(s, idx)), self.T)
            if self.get_p(np.delete(s, idx)) not in self.T:
                # 如果不存在，那么直接返回False
                return False
        # 否则组合成功
        return True

    def arrange(self):
        """对T集合的元素进行排列组合成高阶元素，
        且其子阶元素都存在已确认为频繁模式组合。
        """
        res = np.array([])
        length = self.T.shape[0]

        # 利用两层循环依次遍历集合T中的每个元素
        for a in range(length):
            for b in range(a + 1, length):
                # 提取出每个元素
                pa, pb = self.T[a].split(','), self.T[b].split(',')
                # 将两个列表元素进行组合
                s = np.array(sorted(set(pa) | set(pb)))
                # 如果长度符合高阶，那么进行下一步判断
                if len(s) == len(pa) + 1:
                    # 如果已存在，直接continue
                    # print('debug:', self.get_p(s), res)
                    if self.get_p(s) in res:  # res为空时会提示警告，不过不用担心，已经验证其为正常工作
                        continue
                    # 如果组成的高阶元素的低一阶所有元素都在T中，那么组合成功，将其存入res
                    if self.check_set(s):
                        res = np.append(res, self.get_p(s))
        # 将组合成功的res进行字典排序
        res = np.array(sorted(res))

        return res

    def get_pure_set_origin(self, arr: np.array) -> list:
        """
        朴素版
        将np.array当中没每一个代表元素剥开，并且进行元素去重
        优化：不保存部分非必要代表元素(该元素不可能实现该列frequent>=self.min_freq)
        :param arr: np.array, 需要统计的'列'表其元素的array
        :return: list, np.array 每一个元素剥离后的去重结果
        """
        pure_set = set()
        cnt_dict = dict()
        length = self.data.shape[0]

        for cell in arr:
            ems = str(cell).split(',')
            for em in ems:
                if em not in cnt_dict:
                    cnt_dict[em] = 0
                else:
                    # 以前的版本，此处许是少统计了一部分~
                    cnt_dict[em] += 1
                if cnt_dict[em] / length >= self.min_frequent:
                    pure_set.add(em)
            pass

        pure_set = pure_set - {0, '0'}

        # 在已有的实验当中，一直没有加入sorted函数，这导致了部分实验数据相同的表格，实验数据相差较大
        return sorted(list(pure_set))

    def get_pure_set(self, arr: np.array) -> list:
        """
        使用贪心策略优化的顺序
        将np.array中的每一个代表元素拆分，并按照cnt_dict中的次数排序返回
        只保留次数高于阈值且不等于'0'和0的代表元素
        :param arr: np.array, 需要统计的列表的元素数组
        :return: list, 按次数从大到小排序且高于阈值且不等于'0'和0的代表元素列表
        """
        cnt_dict = {}
        length = self.data.shape[0]

        for cell in arr:
            ems = str(cell).split(',')
            for em in ems:
                if em not in cnt_dict:
                    cnt_dict[em] = 0
                cnt_dict[em] += 1

        # 按次数从大到小排序代表元素，并只保留次数高于阈值且不等于'0'和0的元素
        sorted_reps = sorted(cnt_dict.keys(), key=lambda x: cnt_dict[x], reverse=True)
        filtered_reps = [rep for rep in sorted_reps if
                         cnt_dict[rep] / length >= self.min_frequent and rep != '0' and rep != 0]

        return filtered_reps

    def get_data_representative(self):
        """
        计算出self.data的每一列的代表元素
        :return: dict
        """
        self.repres_dict = dict()
        for col in self.data.columns:
            self.repres_dict[col] = self.get_pure_set(self.data[col].values)
            # print('debug:', col, self.data[col].values, self.repres_dict[col])
        if self.is_debug:
            # print the max calc times.
            res = 1
            for repre in self.repres_dict:
                # print(repre, len(self.repres_dict[repre]))
                res *= (len(self.repres_dict[repre]) if len(self.repres_dict[repre]) != 0 else 1)
            print('max clac times:{}.' .format(res))
            pass
        pass

    def get_data_representative_gate(self):
        """
        计算出self.data的每一列的代表元素
        :return: dict
        """
        self.repres_dict = dict()

        times = 1
        for col in self.data.columns:
            data_col = self.data[col].astype(str)
            combined_values = ','.join(data_col)
            value_counts = pd.Series(combined_values.split(',')).value_counts().to_dict()

            sorted_values = sorted(value_counts.keys(), key=lambda x: value_counts[x], reverse=True)
            sorted_values = [value for value in sorted_values if value != '0']

            self.repres_dict[col] = sorted_values
            times *= 1 if len(self.repres_dict[col]) == 0 else len(self.repres_dict[col])
        if self.is_debug:
            print(times)
        pass

    def de_include_pattern(self, pattern_list: list) -> list:
        """
        将pattern_list进行去包含，并返回去除后的结果。
        此处即暴力枚举进行删除(可以进行优化)
        :param pattern_list:  待处理去包含的list
        :return:  去包含后的结果
        """
        ans = copy.deepcopy(pattern_list)
        # 顺序遍历，仅需要遍历到2阶即可
        for idx in range(2, len(pattern_list)):
            # 依次取出当前阶的所有频繁模式
            for pattern in pattern_list[idx]:
                cols = pattern.split(',')
                # 删除存在的所有子阶频繁模式
                for de_val in cols:
                    backup = cols.copy()
                    backup.remove(de_val)
                    low_pattern = self.get_p(backup)
                    if low_pattern in ans[idx - 1]:
                        ans[idx - 1].remove(low_pattern)
                        pass
                    pass
                pass
            pass
        while len(ans) > 1 and len(ans[-1]) == 0:
            ans = ans[:-1]
        return ans

    def std_answer(self) -> list:
        """
        本来的self.ans当中的元素为np.array，为了形式上的统一将其全部转化为list
        :return: 返回标准化后的self.ans
        """
        if len(self.ans) == 2 and len(self.ans[1]) == 0:
            return [None]
        return [None] + [grade.tolist() for grade in self.ans[1:]]

    def search_range(self):
        """
        获取代表每列代表元素的乘之积
        :return: 搜索次数
        """
        res = 1
        for reps in self.repres_dict:
            cnt = 1 if len(self.repres_dict[reps]) == 0 else len(self.repres_dict[reps])
            res *= cnt
        return res

    def predict(self, X: pd.DataFrame, ans_type=0) -> list:
        """
        将X进行数据分析(apriori)，并返回结果
        :param X: 需要分析的原数据
        :param ans_type: 返回结果的类型。0:原始结果; 1:去包含处理后的结果; 2:返回两种结果
        :return: 频繁模式
        """
        start_time = time.time()
        self.data = X.copy()  # 拷贝
        self.S = np.array(self.data.columns)  # 逻辑上S为集合，物理上是一个np.array类型
        self.T = None  # 集合T一开始为空

        # 得到data每一列的代表元素
        self.get_data_representative()
        # if self.is_debug:
        #     with open('../represent/represent.json', 'w') as file:
        #         json.dump(self.repres_dict, file)
        #     print('完成!')
        # print('debug:', self.repres_dict)

        while self.S.shape[0] != 0:  # 如果下一阶没有组合出新的高阶，那么S集合就没有元素，就停止循环
            self.T = self.S[self.check_cols()]  # 查看S集合中符合条件(联合密度>=FREQUENT)的元素，放入集合T
            # if self.is_debug:
            #     print('debug1:', self.T)
            self.S = self.arrange()  # 将集合T进行组合成高阶的元素存入集合S
            self.ans.append(self.T)  # 将该阶中符合条件的列放入到ans中

        end_time = time.time()
        self.runtime = end_time - start_time

        self.ans = self.std_answer()
        if ans_type == 0:
            return self.ans
        else:
            self.pure_ans = self.de_include_pattern(self.ans)
            if ans_type == 1:
                return self.pure_ans
            else:
                return [self.ans, self.pure_ans]

    def dfs_all(self, check_arr, idx):
        """
        基本框架和前面dfs保持一致，不同的是，此方法会搜索完整颗树
        :param check_arr: 组合的
        :param idx:
        :return: None
        """
        if idx == len(self.temp_keys):
            # if self.is_debug:
            #     print(check_arr)
            if self.check_this_tuple(check_arr):
                self.grid_result.append(self.get_p(check_arr))
            return

        idx_repres = self.repres_dict[self.temp_keys[idx]]

        for rep in idx_repres:
            check_arr.append(rep)
            self.dfs_all(check_arr, idx + 1)
            check_arr.pop()
            # 这里不要使用remove, 否则达不到还原现场的效果
        pass

    def grid_search(self, columns: list) -> list:
        """
        搜索得到所有 s.t. list为频繁模式的代表元素集
        :param columns: 频繁模式集
        :return: 代表元素组成的list
        """
        self.cols_data = self.data[columns]
        self.temp_keys = columns

        self.grid_result = list()
        self.dfs_all([], 0)
        return self.grid_result

    def result_all_reps(self) -> dict:
        """
        key: frequent cols (str), value: [reps1, reps2, ..., repsN] ([str])
        返回挖掘结果频繁模式当中, 能够证其为频繁的所有代表元素集合
        :return: 频繁模式代表元素集
        """

        res = dict()
        # 遍历每一层(阶)的频繁模式列表
        for layer_freq_list in self.ans[1:]:
            # 遍历每一个列表中的频繁模式项集
            for pattern in layer_freq_list:
                # 将当前频繁项集切分成一阶子集
                cols = pattern.split(',')
                res[pattern] = self.grid_search(cols)
                # if self.is_debug:
                #     print(pattern, res[pattern])
                pass
            pass
        return res

    def estimate_times(self, pattern: list) -> int:
        """
        计算最大运算次数
        :param pattern: 频繁模式集合
        :return: 最大运算次数
        """
        def extract_numbers(data):
            numbers = set()

            def process_item(item):
                if isinstance(item, list):
                    for sub_item in item:
                        process_item(sub_item)
                elif isinstance(item, str):
                    numbers.update(item.split(','))

            for item in data:
                process_item(item)

            return sorted(filter(None, numbers))
        pure_cols = extract_numbers(pattern)

        res = 1
        for repre in pure_cols:
            res *= (len(self.repres_dict[repre]) if len(self.repres_dict[repre]) != 0 else 1)
        return res
