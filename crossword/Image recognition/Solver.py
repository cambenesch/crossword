import Puzzle
import DictionaryTool
import copy
import numpy as np
import sys

#page_path = 'pic5.jpg'
#corner_path = 'points5.csv'

def solve(page_path, corner_path):
    print('Reading grid and clues...')
    puzzle = Puzzle.Puzzle(page_path, corner_path)
    print('Reading handwriting...')
    #Read handwriting, make any necessary updates to the puzzle. 
    print('Solving clues...')
    answerlist = DictionaryTool.DictionaryTool(puzzle.cluelist).answerlist
    print('Solving crossword puzzle...')

    answers = copy.deepcopy(answerlist)

    def prioritize(answers):
        priority = {}
        for key in answers.keys():
            num1 = answerlist[key]
            if len(num1) == 0:
                priority[key] = 0
            elif len(num1) == 1:
                priority[key] = num1[0][1]
            else: 
                priority[key] = num1[0][1] - num1[1][1]
        return priority

    
    while len(answers) > 0:
        priority = prioritize(answers)
        highest = max(priority, key=priority.get)
        if len(answers[highest]) == 0:
            del answers[highest]
            continue
        word = answers[highest][0][0]
        try: 
            puzzle.add_word(word, highest, conflict='exception')
        except: 
            pass
        del answers[highest]

    np.savetxt("solution_init.csv", puzzle.chargrid, delimiter=",", fmt='%s')

    wheres = np.where(puzzle.chargrid == '?')
    coords = list(zip(wheres[0], wheres[1]))

    for coord in coords: 
        x_list, y_list = {},{}
        y_id, y_pos, x_id, x_pos = puzzle.find_clueID(coord[0], coord[1])
        x_list[x_id] = puzzle.cluelist[x_id]
        y_list[y_id] = puzzle.cluelist[y_id]
        x_ans = DictionaryTool.DictionaryTool(x_list).answerlist
        y_ans = DictionaryTool.DictionaryTool(y_list).answerlist
        
        bestword, prob_max = ('0','0'), 0
        if len(x_ans[x_id]) == 0 and len(y_ans[y_id]) == 0: pass
        elif len(x_ans[x_id]) == 0:
            for word, prob in y_ans[y_id]:
                if prob > prob_max:
                    bestword, prob_max = (word, '0'), prob
        elif len(y_ans[y_id]) == 0:
            for word, prob in x_ans[x_id]:
                if prob > prob_max:
                    bestword, prob_max = ('0', word), prob
        else:
            agreement = False
            for x_word, x_prob in x_ans[x_id]:
                for y_word, y_prob in y_ans[y_id]:
                    prob = x_prob + y_prob
                    if x_word[x_pos] == y_word[y_pos] and prob > prob_max:
                        bestword, prob_max, agreement = (y_word, x_word), prob, True
            if not agreement:
                for word, prob in y_ans[y_id]:
                    if prob > prob_max:
                        bestword, prob_max = (word, '0'), prob
                for word, prob in x_ans[x_id]:
                    if prob > prob_max:
                        bestword, prob_max = ('0', word), prob
        print(bestword, prob_max, x_id, y_id)
            
        if bestword[0] != '0':
            puzzle.add_word(bestword[0], y_id, conflict='exception')
        if bestword[1] != '0':
            puzzle.add_word(bestword[1], x_id, conflict='exception')
            
    np.savetxt("solution.csv", puzzle.chargrid, delimiter=",", fmt='%s')
    print('Solution saved to ./solution.csv')
    puzzle.save_display_csv()
    print('Display csv saved to ./cluedata.csv')

if __name__ == "__main__":
    page_path = str(sys.argv[1])
    corner_path = str(sys.argv[2])
    solve(page_path, corner_path)