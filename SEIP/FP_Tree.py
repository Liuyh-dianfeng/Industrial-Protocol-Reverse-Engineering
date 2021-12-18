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
        self.transaction_num = None  
 
        self.item_head = defaultdict(list) 
        self.fp_tree = defaultdict()  
        self.max_node_id = 0  
        self.frequent_one_itemsets = defaultdict(lambda: 0) 
        self.frequent_k_itemsets = []  
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
        self.frequent_one_itemsets = dict(sorted(self.frequent_one_itemsets.items(), key=lambda x: x[1], reverse=True))
        self.sort_keys = sorted(self.frequent_one_itemsets, key=self.frequent_one_itemsets.get, reverse=True)
        return
 
    def create_fp_tree(self, data):
        frequent_one_itemsets_keys = set(self.frequent_one_itemsets.keys())
        self.fp_tree[0] = node(item=None, count=0, parent_id=-1)
        for transaction in data:
            transaction = list(set(transaction) & frequent_one_itemsets_keys)  
            if len(transaction) > 0:
                transaction = sorted(transaction, key=self.sort_keys.index)  
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
        self.max_node_id += 1
        next_node_id = copy.copy(self.max_node_id)
        self.fp_tree[next_node_id] = node(item=item, count=1, parent_id=parent_id)  
        self.fp_tree[parent_id].child_id_list.append(next_node_id)  
        self.item_head[item].append(next_node_id)  
        return next_node_id
 
    def get_frequent_k_itemsets(self, data):
        self.ini_param(data)
        suffix_items_list = []
        suffix_items_id_list = []
        for key, value in self.frequent_one_itemsets.items():
            suffix_items = [key]
            suffix_items_list.append(suffix_items)
            suffix_items_id_list.append(self.item_head[key])
            self.frequent_k_itemsets.append(suffix_items)
            self.frequent_k_itemsets_sup.append(value)
        pre_tree = copy.deepcopy(self.fp_tree)
        self.dfs_search(pre_tree, suffix_items_list, suffix_items_id_list)
        return
 
    def dfs_search(self, pre_tree, suffix_items_list, suffix_items_id_list):
        for suffix_items, suffix_items_ids in zip(suffix_items_list, suffix_items_id_list):
            condition_fp_tree = self.get_condition_fp_tree(pre_tree, suffix_items_ids)
            new_suffix_items_list, new_suffix_items_id_list = self.extract_frequent_k_itemsets(condition_fp_tree,
                                                                                               suffix_items)
            if new_suffix_items_list:  
                self.dfs_search(condition_fp_tree, new_suffix_items_list, new_suffix_items_id_list)
        return
 
    def get_condition_fp_tree(self, pre_tree, suffix_items_ids):
        condition_tree = defaultdict()
        for suffix_items_id in suffix_items_ids:
            suffix_items_count = copy.copy(pre_tree[suffix_items_id].count)
            suffix_items_parent_id = pre_tree[suffix_items_id].parent_id
            if suffix_items_parent_id == 0:
                continue
            self.get_path(pre_tree, condition_tree, suffix_items_parent_id, suffix_items_count)
        return condition_tree
 
    def get_path(self, pre_tree, condition_tree, suffix_items_parent_id, suffix_items_count):
        if suffix_items_parent_id == 0:
            return
        else:
            if suffix_items_parent_id not in condition_tree.keys():
                parent_node = copy.deepcopy(pre_tree[suffix_items_parent_id])
                parent_node.count = suffix_items_count
                condition_tree[suffix_items_parent_id] = parent_node
            else:  
                condition_tree[suffix_items_parent_id].count += suffix_items_count
            suffix_items_parent_id = condition_tree[suffix_items_parent_id].parent_id
            self.get_path(pre_tree, condition_tree, suffix_items_parent_id, suffix_items_count)
            return
 
    def extract_frequent_k_itemsets(self, condition_fp_tree, suffix_items):
        new_suffix_items_list = []  
        new_item_head = defaultdict(list)  
        item_sup_dict = defaultdict(int)
        for key, val in condition_fp_tree.items():
            item_sup_dict[val.item] += val.count  
            new_item_head[val.item].append(key)
 
        for item, sup in item_sup_dict.items():
            if sup >= self.minsup_num:  
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
