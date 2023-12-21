# Note:
# "Symbol(s)" are variable in a clause. For example, the clause A^B^C has 3 symbols are A,B, and C.
# sign = 0 is possitive symbol, otherwise, sign = 1 is negation of the symbol.
# clause[symbol] = sign. For example, ~A is stored as clause[A] = 1. Note that clause is a dictionary ==> A: 1, intuitively.
# self.clauses is a dictionary contains list of clauses.
# model: Assignment for each symbol. 

class KnowledgeBase:
    
    def __init__(self, status, clauses):
        self.status = status # Does the problem solved successfully?
        self.clauses = clauses # initial list of clauses (aka bootstrap_with)
        
    def KB_Initialize(self):
        print("In progressing")
        
            
    def addClause(self, clause):
        self.clauses.append(clause)
        
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
                pured_symbols.append((symbol, 1)) 
            
            if not isNeg:
                pured_symbols.append((symbol, 0))
                
        return pured_symbols

    # Unit clauses are clauses that contains only one symbol (e.g, A).
    def extractUnitClauses(self, current_clauses):
        unitSymbols = []
        for clause in current_clauses:
            if len(clause) == 1:
                symbol = list(clause.keys())[0]
                unitSymbols.append((symbol, clause[symbol]))
        return unitSymbols
    
    def listSymbols(self, listOfClauses):
        res = []
        for clause in listOfClauses:
            for symbol in clause:
                res.append(symbol)
        return res
    
    # Solving problem using DBLL
    def solve(self, current_clauses):

        visited=[]
        model = {} # Assignment for each symbol
        symbols = self.listSymbols(current_clauses)
        
        while current_clauses:
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

            if not current_clauses: #The case when all clauses are entailment by KB
                return True
            
            # Prunning    
            puredSymbols = self.extractPureSymbols(symbols, current_clauses)
            for puredSymbol in puredSymbols:
                if(puredSymbol[0] in symbols):
                    symbols.remove(puredSymbol[0])
                model[puredSymbol[0]] = puredSymbol[1]
            
            unit_clauses = self.extractUnitClauses(current_clauses)
            for unitclause in unit_clauses:
                if(unitclause[0] in symbols):
                    symbols.remove(unitclause[0])
                model[unitclause[0]] = unitclause[1]
                
def test():
    # case 1: Successfully
    kb = KnowledgeBase(True, [{'S': 1, 'B': 0}, {'W': 1}, {'P': 1}, {'T': 1}, {'T':0, 'A': 0}])
    result = kb.solve(kb.clauses)
    assert(result == True)
    
    # case 2: There is contradition
    kb = KnowledgeBase(True, [{'S': 1, 'B': 0}, {'W': 1}, {'P': 1}, {'T': 1}, {'T':0}])
    result = kb.solve(kb.clauses)
    assert(result == False)
    
    print("Passed Tests")
    
test()
            
        
    
    
    

    