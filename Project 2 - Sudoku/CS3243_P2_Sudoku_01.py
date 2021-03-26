# CS3243 Introduction to Artificial Intelligence
# Project 2

import sys
import copy

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists
        self.size = len(puzzle)
        self.domains = {}
        self.constraints = None

    """
    Initialises Constraints and Domains, and calls Backtrack with Inferencing algorithm
    """
    def solve(self):
        self.createConstraints()
        self.getDomains()
        return self.backtrack()

    """
    Initiating row, column and box constraints
    Constructs all constraints for each unit which has 20 constraints
    Used in restricting domains during inferencing
    """
    def createConstraints(self):
        self.constraints = ()
        for i in range(self.size):
            row = ()
            for j in range(self.size):
                row += ([],)
            self.constraints += (row,)

        for i in range(self.size):
            for j in range(self.size):
                # Sets by row and col
                for k in range(self.size):
                    if i != k:
                        self.constraints[i][j].append((k,j))
                    if j != k:
                        self.constraints[i][j].append((i,k))
                
                # Sets by 3 * 3 group
                group_r = i // 3
                group_c = j // 3

                for row in range(group_r * 3, (group_r + 1) * 3):
                    for col in range(group_c * 3, (group_c + 1) * 3): 
                        if row == i or col == j: 
                            continue
                        self.constraints[i][j].append((row, col))

    """
    Constructs initial domains of each unit(i,j)
    """
    def getDomains(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.ans[i][j]:
                    continue
                domain = self.constructDomain(i,j)
                self.domains[(i, j)] = [len(domain), domain]

    """
    Constructs domain of each unit(i,j) based on three constraints: row, column and group.
    """
    def constructDomain(self, i, j):
        # possible is enumerative of possibilities in each cell of Sudoku
        possible = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        for unit in self.puzzle[i]:
            if (unit in possible):
                possible.remove(unit)
        for row in self.puzzle:
            if (row[j] in possible):
                possible.remove(row[j])
        groupx = i // 3
        groupy = j // 3
        s = self.getgroupset(groupx, groupy)

        # Removing inconsistent values from the domain based on initial state
        for i in s:
            if (i in possible):
                possible.remove(i)
        return possible

    """
    Picks next variable among list of variables with least remaining possibilities
    Equivalent to maximum restrained variable
    """
    def pickUnassignedVariable(self):
        domain_items = self.domains.items()
        all_min_var = [domain_items[0][0]]
        minRV = domain_items[0][1][0]

        for var, rv_domain in self.domains.items():
            curRV = rv_domain[0]

            if curRV < minRV:
                minRV = curRV
                all_min_var = [var]
            elif curRV == minRV:
                all_min_var.append(var)

        return all_min_var[0]

    """
    Function calls are structured in the way to correspond to lectures.
    Backtrack -> Check complete Assignment -> Choose unassigned variable ->
        Change global domain -> Inference -> Success and return solution 
        OR Backtrack to previous consistent value by removing current assignment
    """
    def backtrack(self):
        # Check for complete Assignment
        if (len(self.domains) == 0):
            return self.ans
        
        # Choose unassigned variable for inferring
        var = self.pickUnassignedVariable()
        if var is None:
            # All variables checked without a solution so return empty
            # As per question, this will not be triggered
            return
        
        row, col = var

        domain = self.domains[(row,col)]

        # Deletes the domain of var from domains
        # Equivalent to current assignment
        del self.domains[(row,col)]
        
        val_list = domain[1]

        for val in val_list:

            # Assigns the value to ans
            self.ans[row][col] = val

            # Updates domains
            changed_domains = self.updateDomains(val, row, col)

            # Inferencing until inconsistent result is reached
            if self.infer(row, col, val):
                # Calls next recursion
                res = self.backtrack()
                # If valid, returns result
                if res:
                    return res

            # Reconstructs domains if fails to get result
            self.reconstructDomains(changed_domains, val)

            # Resets the var in ans to be 0
            # As this assignment failed to achieve a consistent solution
            self.ans[row][col] = 0

        # Reconstructs domains
        self.domains[(row,col)] = domain

    """
    Records changed domains and returns based on the assignment of variable
    in the for loop of backtrack
    """
    def updateDomains(self, num, row, col):
        changed = []
        for i, j in self.constraints[row][col]:
            if self.ans[i][j]:
                continue
            if num in self.domains[(i,j)][1]:
                self.domains[(i,j)][0] -= 1
                self.domains[(i,j)][1].remove(num)
                changed.append((i,j))
        return changed

    """
    Reconstructs domains, equivalent to removing consideration of particular variable
    assignment in Backtracking step and check for alternate values for the variable
    """
    def reconstructDomains(self, domain, num):
        for i, j in domain:
            if (self.domains[(i,j)] == []):
                self.domains[(i,j)] = [1, [num]]
            else:
                self.domains[(i,j)][1].append(num)
                self.domains[(i,j)][0] += 1

    """
    Basis of Inferencing in the Backtrack algorithm where each change due to
    current assignment results in further checking of the variables whose
    domains (valid values) were changed by this assignment
    Here occurs maximally upper bound due to known 9x9 Sudoku range
    """
    def infer(self, row, col, num):
        for i, j in self.constraints[row][col]:
            # All non-zero in the constraints without inconsistency
            if self.ans[i][j]:
                continue

            if num in self.domains[(i,j)][1]:
                if (self.domains[(i,j)][0] == 1):
                    return False
        return True

    """
    Gets all the filled non-zero places for contraint building
    """
    def getgroupset(self, groupx, groupy):
        s = set()
        for i in range(3 * groupx, 3 * (groupx + 1)):
            for j in range(3 * groupy, 3 * (groupy + 1)):
                s.add(self.puzzle[i][j])
        return s

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
