from collections import defaultdict, Counter, deque
import math
import copy
from pandas import DataFrame as df
import numpy as np
import pandas as pd
from graphviz import Digraph
from utils import *

class node:
    def __init__(self, item, count, parent_id):
        self.item = item
        self.count = count
        self.parent_id = parent_id
        self.child_id_list = []
 
 
class FP_Tree:
    def __init__(self, minsup=0.5):
        self.minsup = minsup
        self.minsup_num = None
        self.transaction_num = None  # 一个传入数据集的事务数目
 
        self.item_head = defaultdict(list)  # 项头表{['A']:[1,2,4,5]}由item和对应的id list组成
        self.fp_tree = defaultdict()  # 键为节点id，值为node
        self.max_node_id = 0  # 当前树的最大节点id，用于插入节点时，新建node_id。
        self.frequent_one_itemsets = defaultdict(lambda: 0)  # 频繁一项集
        self.frequent_k_itemsets = []  # 频繁k项集
        self.frequent_k_itemsets_sup = []
        self.sort_keys = None
 
    def ini_param(self, data):
        self.transaction_num = len(data)
        self.minsup_num = math.ceil(self.transaction_num * self.minsup)
        self.get_frequent_one_itemsets(data)
        self.create_fp_tree(data)
 
    def get_frequent_one_itemsets(self, data):
        c = Counter()
        for t in data:
            c += Counter(t)
        for key, value in c.items():
            if value >= self.minsup_num:
                self.frequent_one_itemsets[key] = value
        # 已初步获取频繁一项集，按照出现次数逆序排序
        self.frequent_one_itemsets = dict(sorted(self.frequent_one_itemsets.items(), key=lambda x: x[1], reverse=True))
        # 此处已获得了已排序的频繁一项集，考虑到后续的事务需要按照其键的顺序来进行排序和筛选，再返回FP_Tree的初始化函数加成员
        self.sort_keys = sorted(self.frequent_one_itemsets, key=self.frequent_one_itemsets.get, reverse=True)
        return
 
    def create_fp_tree(self, data):
        frequent_one_itemsets_keys = set(self.frequent_one_itemsets.keys())
        # 创建根节点
        self.fp_tree[0] = node(item=None, count=0, parent_id=-1)
        for transaction in data:
            transaction = list(set(transaction) & frequent_one_itemsets_keys)  # 去除非频繁项
            if len(transaction) > 0:
                transaction = sorted(transaction, key=self.sort_keys.index)  # 对事务筛选后进行排序
                parent_id = 0
                for item in transaction:
                    parent_id = self.insert_fptree(parent_id, item)
        return
 
    def insert_fptree(self, parent_id, item):
        child_id_list = self.fp_tree[parent_id].child_id_list
        for child_id in child_id_list:
            child_node = self.fp_tree[child_id]
            if child_node.item == item:
                self.fp_tree[child_id].count += 1
                return child_id
            # if return降低圈复杂度的同时，再判断当前的父节点的子节点中没有项与之匹配，所以新建子节点，更新项头表和树
        self.max_node_id += 1
        next_node_id = copy.copy(self.max_node_id)
        self.fp_tree[next_node_id] = node(item=item, count=1, parent_id=parent_id)  # 更新树，添加节点
        self.fp_tree[parent_id].child_id_list.append(next_node_id)  # 更新父节点的孩子列表
        self.item_head[item].append(next_node_id)  # 项头表的建立是和树的建立一并进行的
        return next_node_id
 
    def get_frequent_k_itemsets(self, data):
        self.ini_param(data)
        # 现在已经构造好的数据类型有fp树，项头表，频繁一项集。现在提取频繁k项集
        # 这时候需要用到项头表里面的节点列表来向上搜索条件FP树，后通过条件FP树形成条件模式基，递归得出频繁k项集
        suffix_items_list = []
        suffix_items_id_list = []
        for key, value in self.frequent_one_itemsets.items():
            suffix_items = [key]
            suffix_items_list.append(suffix_items)
            suffix_items_id_list.append(self.item_head[key])
            self.frequent_k_itemsets.append(suffix_items)
            self.frequent_k_itemsets_sup.append(value)
        # self.frequent_k_itemsets = copy.deepcopy(self.frequent_one_itemsets)
        # 这里的前缀树是fp树的深拷贝，这样处理和Python的传对象方式有关。即在Python中基础类型是传值，复杂类型是传引用。
        pre_tree = copy.deepcopy(self.fp_tree)
        self.dfs_search(pre_tree, suffix_items_list, suffix_items_id_list)
        return
 
    def dfs_search(self, pre_tree, suffix_items_list, suffix_items_id_list):
        for suffix_items, suffix_items_ids in zip(suffix_items_list, suffix_items_id_list):
            # 这时候需要用到项头表里面的节点列表来向上搜索条件FP树
            condition_fp_tree = self.get_condition_fp_tree(pre_tree, suffix_items_ids)
            # 根据条件模式基，获取频繁k项集
            new_suffix_items_list, new_suffix_items_id_list = self.extract_frequent_k_itemsets(condition_fp_tree,
                                                                                               suffix_items)
            if new_suffix_items_list:  # 如果后缀有新的项添加进来，则继续递归深度搜索
                # 以开始的单项'G'后缀项为例，经过第一次提取k项频繁集后。单一后缀变为新的后缀项列表[['C', 'G'], ['A', 'G'],
                # ['E', 'G']]，其计数5 5 4也加入到k项集的计数列表里面去了，new_suffix_items_id_list记录了新的后缀项节点id。
                # 此时把原本的pre_tree参数变为条件树，原本的单一后缀项参数变为new_suffix_items_list， 原本的后缀项id列表参数变
                # 为新的id项列表参数。
                # 在这样的递归过程中完成了对k项频繁集的挖掘。
                self.dfs_search(condition_fp_tree, new_suffix_items_list, new_suffix_items_id_list)
        return
 
    def get_condition_fp_tree(self, pre_tree, suffix_items_ids):
        condition_tree = defaultdict()
        # 从各个后缀叶节点出发，综合各条路径形成条件FP树
        for suffix_items_id in suffix_items_ids:
            suffix_items_count = copy.copy(pre_tree[suffix_items_id].count)
            suffix_items_parent_id = pre_tree[suffix_items_id].parent_id
            # 后缀项父节点id为0的话，表示已经搜索到了根节点
            if suffix_items_parent_id == 0:
                continue
            self.get_path(pre_tree, condition_tree, suffix_items_parent_id, suffix_items_count)
        return condition_tree
 
    def get_path(self, pre_tree, condition_tree, suffix_items_parent_id, suffix_items_count):
        # 根据后缀的某个叶节点的父节点出发，选取出路径，并更新计数。suffix_item_count为后缀的计数
        if suffix_items_parent_id == 0:
            return
        else:
            if suffix_items_parent_id not in condition_tree.keys():
                # 把后缀计数赋值给页节点计数
                parent_node = copy.deepcopy(pre_tree[suffix_items_parent_id])
                parent_node.count = suffix_items_count
                condition_tree[suffix_items_parent_id] = parent_node
            else:  # 如果叶节点有多个，则路径可能重复，计数叠加
                condition_tree[suffix_items_parent_id].count += suffix_items_count
            suffix_items_parent_id = condition_tree[suffix_items_parent_id].parent_id
            self.get_path(pre_tree, condition_tree, suffix_items_parent_id, suffix_items_count)
            return
 
    def extract_frequent_k_itemsets(self, condition_fp_tree, suffix_items):
        # 根据条件模式基，提取频繁项集, suffix_item为该条件模式基对应的后缀
        # 返回新的后缀，以及新添加项(将作为下轮的叶节点)的id
        new_suffix_items_list = []  # 后缀中添加的新项
        new_item_head = defaultdict(list)  # 基于当前的条件FP树，更新项头表， 新添加的后缀项
        item_sup_dict = defaultdict(int)
        for key, val in condition_fp_tree.items():
            item_sup_dict[val.item] += val.count  # 对项出现次数进行统计
            new_item_head[val.item].append(key)
 
        for item, sup in item_sup_dict.items():
            if sup >= self.minsup_num:  # 若条件FP树中某个项是频繁的，则添加到后缀中
                current_item_set = [item] + suffix_items
                self.frequent_k_itemsets.append(current_item_set)
                self.frequent_k_itemsets_sup.append(sup)
                new_suffix_items_list.append(current_item_set)
            else:
                new_item_head.pop(item)
        return new_suffix_items_list, new_item_head.values()
    
    ############
    def max_frequent_k_itemsets(self):
        num_list = [len(itemset) for itemset in self.frequent_k_itemsets]
        max_k_index_list = [i for i, x in enumerate(num_list) if x == max(num_list)]
        frequent_k_itemsets_list = []
        frequent_k_itemsets_sup_list = []

        for index in max_k_index_list:
            frequent_k_itemsets_list.append(self.frequent_k_itemsets[index]) 
            frequent_k_itemsets_sup_list.append(self.frequent_k_itemsets_sup[index])

        return frequent_k_itemsets_list,frequent_k_itemsets_sup_list

    ###############
    def plotFPtree(self):
        dot = Digraph('FP Tree')
        dot.node('0','start')

        for key in self.fp_tree.keys():
            if self.fp_tree[key].parent_id != -1:
                dot.node(str(key),str(self.fp_tree[key].item)+': '+str(self.fp_tree[key].count))
                dot.edge(str(self.fp_tree[key].parent_id),str(key))

#         display(dot)
        return dot