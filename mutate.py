import ast
import astor
import sys
import random

class MyVisitor(ast.NodeTransformer):
    """Notes all Numbers and all Strings. Replaces all numbers with 481 and
    strings with 'SE' for now. Will be altering this class."""

    def __init__(self, mutProbs=None):
        self.mutProbs = {
            'Num': 0.01, # Probability to mutate numbers
            'Str': 0.1,
            'Compare': 0.04,
            'BinOp': 0.2,
            'AssOp': 0.001,
            'AssAugOp': 0.001,
            'AssAnnOp': 0.001
        }

    def mutate_or_no(self, nodeType):
        return random.random() < self.mutProbs.get(nodeType, 0.1)
 
    def visit_Num(self, node):
        if self.mutate_or_no('Num'):
            node.n = 481
        return node

    def visit_Str(self, node):
        # print("Visitor sees a string: ", ast.dump(node), " aka ", astor.to_source(node))
        if self.mutate_or_no('Str'):
            node.s = "SE"
        return node
    
    def visit_Compare(self, node):
        # print("Visitor sees a comparator: ", ast.dump(node), " aka ", astor.to_source(node))
        if self.mutate_or_no('Compare'):
            for i, op in enumerate(node.ops):
                if isinstance(op, ast.Gt): # > operator
                    node.ops[i] = ast.LtE() # Negation of > is <=
                elif isinstance(op, ast.GtE):
                    node.ops[i] = ast.Lt()
                elif isinstance(op, ast.Lt):
                    node.ops[i] = ast.GtE()
                elif isinstance(op, ast.LtE):
                    node.ops[i] = ast.Gt()
        return node
    
    def visit_BinOp(self, node):
        if self.mutate_or_no('BinOp'):
            if isinstance(node.op, ast.Add): # Check if op is '+'
                node.op = ast.Sub()
            elif isinstance(node.op, ast.Sub):
                node.op = ast.Add()
            elif isinstance(node.op, ast.Mult):
                node.op = ast.FloorDiv()
            elif isinstance(node.op, ast.FloorDiv):
                node.op = ast.Mult()
            elif isinstance(node.op, ast.Div):
                node.op = ast.Mult()
        return node
    
    def visit_Assign(self, node):
        if self.mutate_or_no('AssOp'):
            return None
        else:
            return node
            
    def visit_AugAssign(self, node):
        if self.mutate_or_no('AssAugOp'):
            return None
        else:
            return node
        
    def visit_AnnAssign(self, node):
        if self.mutate_or_no('AssAnnOp'):
            return None
        else:
            return node


if len(sys.argv) != 3:
    print("Exactly 2 arguments are required.")
    exit(1)

# sys.argv[0] is just "mutate.py"
programName = str(sys.argv[1])
numMutants = int(sys.argv[2])

code = ""
with open(programName, 'r') as file:
    code = file.read()

# As a sanity check, we'll make sure we're reading the code
    # correctly before we do any processing. 
    # print("Before any AST transformation")
    # print("Code is: ", code)

for i in range(numMutants):
    originalTree = ast.parse(code)
    # print(astor.dump_tree(originalTree))
    random.seed(i) # This keeps our program deterministic.
    tree = MyVisitor().visit(originalTree)
    # Add lineno & col_offset to the nodes we created
    ast.fix_missing_locations(tree)
    mutantCode = astor.to_source(tree)
    with open("%d.py" % i, 'w') as mutantFile:
        mutantFile.write(mutantCode)
    print("Mutant %d created." % i)