from graphviz import Digraph
from queue import Queue

class PTA:
 
    def __init__(self):
        """
        Initialize your data structure here.
        """
        self.root = {}
        self.end = '#'
 
    def insert(self, word):
        """
        Inserts a word into the trie.
        :type word: str
        :rtype: void
        """
        
        curNode = self.root
        for c in word:
            if not c in curNode:
                curNode[c] = {}
            curNode = curNode[c]
        curNode[self.end] = True
 
    def search(self, word):
        """
        Returns if the word is in the trie.
        :type word: str
        :rtype: bool
        """
        curNode = self.root
        for c in word:
            if not c in curNode:
                return False
            curNode = curNode[c]
            
        # Doesn't end here
        if not self.end in curNode:
            return False
        
        return True
 
    def startsWith(self, prefix):
        """
        Returns if there is any word in the trie that starts with the given prefix.
        :type prefix: str
        :rtype: bool
        """
        curNode = self.root
        for c in prefix:
            if not c in curNode:
                return False
            curNode = curNode[c]
        
        return True
    
    def printTree(self):
        Alpha = {i:chr(i+65) for i in range(26)}
        Alpha['#'] = '#'
        
        dot = Digraph('state machine')
        
        q = Queue()
        Nodes = []
        Nodes.append(('start','start'))
        Edges = []
        for key in self.root.keys():
            if ('start',str(key)) not in Edges:
                Edges.append(('start',str(key)))
            
        q.put(self.root)
        while(q.qsize() > 0):
            node = q.get()
            for key in node.keys():
                if (str(key),Alpha[key]) not in Nodes:
                    Nodes.append((str(key),Alpha[key]))
                if node[key] != True:
                    q.put(node[key])
                    for nkey in node[key].keys():
                        if (str(key),str(nkey)) not in Edges:
                            Edges.append((str(key),str(nkey)))

        for tup in Nodes:
            dot.node(tup[0],tup[1])
        for tup in Edges:
            dot.edge(tup[0],tup[1],label = tup[0])
            
#         display(dot)
        return dot

