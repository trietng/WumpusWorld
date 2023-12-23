# Note:
# "Symbol(s)" are variable in a clause. For example, the clause A^B^C has 3 symbols are A,B, and C.
# sign = 0 is possitive symbol, otherwise, sign = 1 is negation of the symbol.
# clause[symbol] = sign. For example, ~A is stored as clause[A] = 1. Note that clause is a dictionary ==> A: 1, intuitively.
# self.clauses is a dictionary contains list of clauses.
# model: Assignment for each symbol. 
import copy
class KnowledgeBase:
    
    def __init__(self, status, clauses):
        self.status = status # Does the problem solved successfully?
        self.clauses = clauses # initial list of clauses (aka bootstrap_with)
        
    def KB_Initialize(self):
        print("In progressing")
        
            
    def add_clause(self, clause):
        if clause in self.clauses:
            return False
        self.clauses.append(clause)
        return True
        
    def del_clause(self, symbol):
        for clause in self.clauses:
            if symbol in list(clause.keys()):
                self.clauses.remove(clause)
                return True
        return False
        
        
    # Pure symbols are symbols that always be positive (or negative) in the clause dictionary. This symbol should be replaced by a corresponding constant (positive
    # or negative) to enhance the performance of the SAT Solver Algorithm.
    def extractPureSymbols(self, symbols, current_clauses):
        pured_symbols = []
        for symbol in symbols:
            isPos = False # is the symbol positive?
            isNeg = False # Is there negation in the symbol?
            
            for clause in current_clauses:

                if symbol in clause:
                    if clause[symbol] == 1:
                        isNeg = True 
                    elif clause[symbol] == 0:
                        isPos = True 
                    
                    if isPos and isNeg:
                        break 
                    
            if not isPos:
                return symbol, 1
            
            if not isNeg:
                return symbol, 0
        return None, None
                

    # Unit clauses are clauses that contains only one symbol (e.g, A).
    def extractUnitClauses(self, current_clauses):
        for clause in current_clauses:
            if len(clause) == 1:
                symbol = list(clause.keys())[0]
                return symbol, clause[symbol]
        return None, None
    
    def listSymbols(self, listOfClauses):
        res = []
        for clause in listOfClauses:
            for symbol in clause:
                res.append(symbol)
        return res
    
    
    def selection(self, clauses, symbols):          

        repeat = {}
        pos_neg = {} # format: [positive_count, negative_count]
        
        for clause in clauses:
            for symbol in clause:
                if symbol not in repeat:
                    repeat[symbol] = 0
                    pos_neg[symbol] = [0,0] 
                repeat[symbol] += 1
                if clause[symbol] == 0:
                    pos_neg[symbol][0] += 1
                elif clause[symbol] == 1:
                    pos_neg[symbol][1] += 1
        max = symbols[0]
        iteratorMaxValue = 0
        for symbolTemp in repeat:
            if iteratorMaxValue < repeat[symbolTemp]:
                max = symbolTemp
                iteratorMaxValue = repeat[symbolTemp]

        if pos_neg[max][0]>pos_neg[max][1]:
            return max, 0
        else:
            return max, 1

    
    # Solving problem using DBLL
    def dpll(self, current_clauses, model, symbols):
        visited=[]
        # model = {} # Assignment for each symbol
        # symbols = self.listSymbols(current_clauses)
        
        for clause in current_clauses:
            known = False
            removedSymbols = []
            
            for symbol in clause:
                if symbol in model: 
                    if model[symbol] == clause[symbol]:
                        visited.append(clause)
                        known = True
                        break 
                    else:
                        removedSymbols.append(symbol)
            for symbol in removedSymbols:
                del clause[symbol]
            
            # If there is contradition so the problem is unsolvable.  
            if known == False and not bool(clause):
                return False
        
        # just copy the elements from the base KB that not be deleted
        temp_clauses = []
        for clause in current_clauses:
            if clause in visited:
                continue
            temp_clauses.append(clause)
        current_clauses = temp_clauses

        if len(current_clauses) == 0: #The case when all clauses are entailment by KB
            return True
        
        # Prunning    
        puredSymbols, mark = self.extractPureSymbols(symbols, current_clauses)
        if mark != None:
            if(puredSymbols in symbols):
                symbols.remove(puredSymbols)
            model[puredSymbols] = mark
            return self.dpll(current_clauses, model, symbols)
        
        unit_clauses, mark = self.extractUnitClauses(current_clauses)
        if mark != None:
            if(unit_clauses in symbols):
                symbols.remove(unit_clauses)
            model[unit_clauses] = mark
            return self.dpll(current_clauses, model, symbols)
            
        symbol, mark = self.selection(current_clauses, symbols)
        if(symbol in symbols):
            symbols.remove(symbol)
        model[symbol]= mark

        if self.dpll(copy.deepcopy(current_clauses), copy.deepcopy(model), copy.deepcopy(symbols)):
            return True
        
        model[symbol]= -mark
        return self.dpll(current_clauses, model, symbols) 
    
    def solve(self):
        if not self.clauses:
            return False
        symbols = self.listSymbols(self.clauses)
        return self.dpll(self.clauses, {}, symbols)
                
def test():
    # case 1: Successfully
    kb = KnowledgeBase(True, [{'S': 1, 'B': 0}, {'W': 1}, {'P': 1}, {'T': 1}, {'T':0, 'A': 0}])
    result = kb.solve()
    assert(result == True)
    
    # case 2: There is contradition
    kb = KnowledgeBase(True, [{'S': 1, 'B': 0}, {'W': 1}, {'P': 1}, {'T': 1}, {'T':0}])
    result = kb.solve()
    assert(result == False)
    
    # case 3: taken from https://fanpu.io/blog/2021/a-dpll-sat-solver/
    
    kb = KnowledgeBase(True, [{'x1': 0, 'x2': 0, 'x3':0}, {'x1': 1, 'x2': 1, 'x3':1}])
    result = kb.solve()
    assert(result == True)
    
    # case 4: Also in https://fanpu.io/blog/2021/a-dpll-sat-solver/
    kb = KnowledgeBase(True, [{'x1': 1, 'x2': 0, 'x4':0}, {'x2': 1, 'x3': 0, 'x4':0}, {'x1': 0, 'x3': 1, 'x4':0}, {'x1': 0, 'x2': 1, 'x4':1}, {'x2': 0, 'x3': 1, 'x4':1}, {'x1': 1, 'x3': 0, 'x4':1},{'x1': 0, 'x2': 0, 'x3':0}, {'x1': 1, 'x2': 1, 'x3':1}])
    result = kb.solve()
    assert(result == False)
    
    # case 5: Taken from https://www.cs.cornell.edu/courses/cs4860/2009sp/lec-04.pdf
    kb = KnowledgeBase(True, [{'p': 0, 'q': 0, 'r': 0, 's': 0}, {'p': 1, 'q': 0, 'r': 1}, {'q': 1, 'r': 1, 's': 0}, {'p': 0, 'q': 1, 'r': 0, 's': 0}, {'q': 0, 'r': 1, 's': 1}, {'p': 1, 'r': 1, 's': 0}, {'p': 1, 's': 1}, {'p': 0, 'q': 1}])
    result = kb.solve()
    assert(result == True)
    
    # case 6: Test for del clause:
    kb = KnowledgeBase(True, [{'x1': 1, 'x2': 1, 'x3': 0}, {'x1': 1}, {'x4': 1, 'x3': 1, 'x1': 0}])
    
        # subtest: initially, the clause is existed in the kb
    result = True if {'x4': 1, 'x3': 1, 'x1': 0} in kb.clauses else False
    assert(result == True)

    kb.del_clause('x4')
    
         # subtest: the clause is removed from the kb.
    result = True if {'x4': 1, 'x3': 1, 'x1': 0} in kb.clauses else False
    assert(result == False)
        
    # case 7: Test for add clause:
    kb = KnowledgeBase(True, [{'x1': 1, 'x2': 1, 'x3': 0}, {'x1': 1}, {'x4': 1, 'x3': 1, 'x1': 0}])
    
        # subtest: initially, the clause is not existed in the kb
    result = True if {'x1': 1, 'x2': 1, 'x3': 0, 'x4':1, 'x5': 0} in kb.clauses else False
    assert(result == False)

    kb.add_clause({'x1': 1, 'x2': 1, 'x3': 0, 'x4':1, 'x5': 0})
    
         # subtest: the clause is added to the kb.
    result = True if {'x1': 1, 'x2': 1, 'x3': 0, 'x4':1, 'x5': 0} in kb.clauses else False
    assert(result == True)
    
        # subtest: the recently added clause is removed to the kb.
    kb.del_clause('x5')
    result = True if {'x1': 1, 'x2': 1, 'x3': 0, 'x4':1, 'x5': 0} in kb.clauses else False
    assert(result == False)
    
        # subtest: add existed clause:
    isSuccessful = kb.add_clause({'x1': 1, 'x2': 1, 'x3': 0})
    assert(isSuccessful == False)
    
    print(kb.clauses)
    
    
    
    kb = KnowledgeBase(True, [])
    a = kb.solve()
    assert(a == False)
    
    print(a)
    
    print("Passed all tests")
    
test()
            
        
    
    
    

    