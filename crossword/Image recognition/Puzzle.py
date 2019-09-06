import pytesseract as pt
pt.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
from PIL import Image
import cv2
import numpy as np
from matplotlib import pyplot as plt
import copy
import pandas as pd

class Puzzle:
    
    def __init__(self, page_path, corner_path):
        self.page_pic = cv2.cvtColor(cv2.imread(page_path), cv2.COLOR_BGR2GRAY)
        #self.corners = np.array([[240,2120], [1840,2115], [1890,3800], [150,3830]])
        self.corners = np.loadtxt(corner_path, delimiter=',', dtype=int)
        self.flatgrid = self.flatten(self.page_pic, self.corners, imgsize=(1000,1000))
        self.blacks = self.black_coords(self.flatgrid)
        self.crossgrid, self.cluelist, self.acrossnums, self.downnums = self.blacks_to_grid(self.blacks)
        self.smallboxes = self.all_smallboxes(self.flatgrid, imgsize=1000)
        self.acrossimg, self.downimg = self.getAcross(self.page_pic, self.corners)
        self.cluelist = self.process_ocr(self.acrossimg, 'ACROSS', self.acrossnums, self.cluelist)
        self.cluelist = self.process_ocr(self.downimg, 'DOWN', self.downnums, self.cluelist)
        self.chargrid = self.init_chargrid()
    
    def flatten(self, page_pic, corners, imgsize=(1000,1000)): 
        '''
        page_pic is the original full-page image taken by the user
        corners is a 2D nparray, lists pixel coordinates of the crossgrid's 4 corners
            First row is top left corner, proceed counterclockwise
        imgsize is the side pixel length of the returned flattened image
        '''
        newCorners = np.array([[0,0], [imgsize[0]-1, 0], [imgsize[0]-1, imgsize[1]-1], [0, imgsize[1]-1]])
        h, status = cv2.findHomography(corners, newCorners)
        return cv2.warpPerspective(page_pic, h, imgsize)

    def corner_crop(self, flatgrid, corners): #corners is 2D nparray. 4 rows, one for each coordinate. 
        x, y, w, h = cv2.boundingRect(corners)
        smallimg = flatgrid[y:y+h, x:x+w].copy()

        corners -= corners.min(axis=0)
        mask = np.zeros(smallimg.shape[:2], np.uint8)
        cv2.drawContours(mask, [corners], -1, (255,255,255), -1, cv2.LINE_AA)

        dst = cv2.bitwise_and(smallimg, smallimg, mask=mask)

        return dst

    def get_smallbox(self, flatgrid, i, j, imgsize=1000): 
        '''
        flatgrid is the transformed crossgrid image (must have square dimensions)
        i, j are coordinates of the desired smallbox
        imgsize is the side length of flatgrid
        '''
        i1, i2 = int(i * imgsize / 15), int((i+1) * imgsize / 15)
        j1, j2 = int(j * imgsize / 15), int((j+1) * imgsize / 15)
        smallCorners = np.array([[i1, j1], [i2, j1], [i2, j2], [i1, j2]])
        smallImg = self.corner_crop(flatgrid, smallCorners)
        return smallImg

    def all_smallboxes(self, flatgrid, imgsize=1000): #returns dictionary mapping coordinate to smallbox. 
        allsmalls = {}
        for i in range(15):
            for j in range(15):
                allsmalls[(i,j)] = self.get_smallbox(flatgrid, i, j, imgsize)
        return allsmalls

    def black_coords(self, flatgrid): #flatgrid is the transformed crossgrid image
        data = np.zeros((15, 15))
        for i in range(15):
            for j in range(15):
                data[j, i] = self.get_smallbox(flatgrid, i, j).mean()

        sortedData = np.msort(data.flatten()) #sorted mean values
        shifted = np.append(sortedData, sortedData[-1]) #shifted has something at end of array
        diffs = shifted - np.insert(sortedData, 0, sortedData[0])
        numblack = np.argmax(diffs) #tells us how many black boxes there are
        threshold = np.mean(sortedData[numblack - 1:numblack+1])
        blackboxes = np.where(data < threshold)
        return np.concatenate((blackboxes[0].reshape(-1,1), blackboxes[1].reshape(-1,1)), axis=1)

    def blacks_to_grid(self, blacks): #blacks is the list of black grid coordinates
        printgrid = np.zeros((15, 15))
        printgrid[blacks[:,0],blacks[:,1]] = 255
        refgrid = copy.deepcopy(printgrid)
        counter, cluelist = 1, {}
        acrossnums, downnums = [], []
        for i in range(15):
            for j in range(15):
                down, across = False, False
                if i==0 and refgrid[i,j]==0:
                    down = True
                if j==0 and refgrid[i,j]==0:
                    across = True
                if j > 0 and refgrid[i,j-1] == 255 and refgrid[i,j] == 0:
                    across = True
                if i > 0 and refgrid[i-1,j] == 255 and refgrid[i,j] == 0:
                    down = True
                if down:
                    below = refgrid[i:15,j]
                    if len(np.where(below==255)[0]) == 0:
                        word_len = 15 - i
                    else: word_len = np.where(below==255)[0][0]
                    cluelist[str(counter)+' DOWN'] = ['?' * word_len]
                    downnums.append(counter)
                if across: 
                    below = refgrid[i,j:15]
                    if len(np.where(below==255)[0]) == 0:
                        word_len = 15 - j
                    else: word_len = np.where(below==255)[0][0]
                    cluelist[str(counter)+' ACROSS'] = ['?' * word_len]
                    acrossnums.append(counter)
                if down or across:
                    printgrid[i,j] = counter
                    counter += 1
        return printgrid, cluelist, sorted(acrossnums), sorted(downnums)

    def getAcross(self, img, corners):

        corners = np.fliplr(corners)

        def getCorner(corns, bottom_ind, top_ind, ratio):
            x1, y1, x2, y2 = np.stack((corns[bottom_ind], corns[top_ind])).flatten()
            x = int(x2 + ratio * (x1 - x2))
            y = int(y2 + ratio * (y1 - y2))
            return np.array([y, x])

        acrossCorners = -np.ones((4, 2)).astype(int)
        param_sets = [(0, -1, 2.04), (1, 2, 2.04), (1, 2, 1.055), (0, -1, 1.055)]
        for i, param_set in enumerate(param_sets):
            bottom_ind, top_ind, ratio = param_set
            acrossCorners[i,:] = getCorner(corners, bottom_ind, top_ind, ratio)

        new_corns = np.concatenate((np.fliplr(acrossCorners[0:2,:]), corners[2:4,:]))
        downCorners = -np.ones((4, 2)).astype(int)
        r1, r2 = 1.035, 1.69
        param_sets = [(1, 0, r1), (1, 0, r2), (2, 3, r2), (2, 3, r1)]
        for i, param_set in enumerate(param_sets):
            bottom_ind, top_ind, ratio = param_set
            downCorners[i,:] = getCorner(new_corns, bottom_ind, top_ind, ratio)

        acrosses = self.flatten(img, acrossCorners, imgsize=(1000,1000))
        downs = self.flatten(img, downCorners, imgsize=(710,2340))

        return acrosses, downs

    def process_ocr(self, img, direction, cluenums, cluelist): #modifies cluelist in-place
        cluenums = copy.deepcopy(cluenums)
        text = pt.image_to_string(img).replace("'","")
        no_newlines = text.split(direction)[1].split('\n')
        nonempty = list(filter(lambda x : x.strip() != '', no_newlines))

        def get_prefix(line):
            prefix = line.split(')')[0]
            if (line.find(')') in (1, 2)) and prefix.isnumeric():
                return int(prefix), line[len(prefix)+1:].strip()
            else: return -1, ''

        prevnum = -1
        for line in nonempty:
            cluenum, txt = get_prefix(line)
            if cluenum == -1:
                if prevnum != -1:
                    cluelist[str(prevnum) + ' ' + direction][1] += ' ' + line
            else: 
                try: nextclue = cluenums.pop(0)
                except IndexError: assert False, 'Extra clue at ' + str(cluenum) + direction
                assert cluenum == nextclue, "Can't read clue: " + line
                cluelist[str(cluenum) + ' ' + direction].append(txt)
                prevnum = cluenum

        assert cluenums == [], 'Not all clues were found for direction ' + direction
        return cluelist
    
    def init_chargrid(self):
        chars = np.empty((15,15), dtype=str)
        chars[:] = '?'
        chars[np.where(self.crossgrid==255)] = ' '
        return chars
        
    def save_display_csv(self, filename='cluedata.csv'):
        returner = pd.DataFrame(columns=['dir', 'key', 'clue'])
        for i, clueID in enumerate(self.cluelist.keys()):
            returner.loc[i] = [clueID.split()[1].lower(), clueID.split()[0], self.cluelist[clueID][1]]
        returner.loc[200] = ['size', '', 15]
        charstring = ''
        for entry in self.chargrid.flatten():
            if entry == ' ': charstring += ' '
            elif entry == '?': charstring += '_'
            else: charstring += entry
        returner.loc[300] = ['letters','', charstring]
        returner.to_csv(filename, index=False)
    
    def find_clueID(self, y, x):
        assert self.crossgrid[y,x] != 255, "can't find clueIDs of black box."
        y_down, x_across = y, x
        while y_down > 0 and self.crossgrid[y_down-1, x] != 255:
            y_down -= 1
        while x_across > 0 and self.crossgrid[y, x_across-1] != 255:
            x_across -= 1
        y_pos, x_pos = y - y_down, x - x_across
        y_id = str(int(self.crossgrid[y_down,x])) + ' DOWN'
        x_id = str(int(self.crossgrid[y,x_across])) + ' ACROSS'
        
        return y_id, y_pos, x_id, x_pos
    
    def add_letter(self, letter, y, x, conflict='exception'): #updates self.chargrid, self.cluelist
        assert len(letter) == 1 and letter.isalpha(), 'Letter must be 1 digit and isalpha.'
        assert self.chargrid[y,x] != ' ', 'Cannot set letter for black cell.'
        if conflict == 'ignore':
            if self.chargrid[y,x] not in ('?', letter): return
        elif conflict == 'exception':
            assert self.chargrid[y,x] in ('?', letter), 'Cannot override existing letter.'
        else: assert conflict == 'override', 'Conflict behavior must be exception, ignore, or override'
        self.chargrid[y,x] = letter
        
        y_id, y_pos, x_id, x_pos = self.find_clueID(y, x)
        prev_solution = self.cluelist[y_id][0]
        self.cluelist[y_id][0] = prev_solution[:y_pos] + letter + prev_solution[y_pos+1:]
        prev_solution = self.cluelist[x_id][0]
        self.cluelist[x_id][0] = prev_solution[:x_pos] + letter + prev_solution[x_pos+1:]
        
    def find_cell(self, clueID, pos): #returns y, x of the corresponding cell
        cluenum, direction = clueID.split()
        cluenum = int(cluenum)
        assert np.where(self.crossgrid == cluenum)[0].shape[0] == 1, 'Strange error in find_cell'
        y, x = np.where(self.crossgrid == cluenum)
        y, x = y[0], x[0]
        if direction == 'ACROSS': x += pos
        elif direction == 'DOWN': y += pos
        else: assert False, 'Bad clueID in find_cell'
        return y, x
        
    def add_word(self, word, clueID, conflict='ignore'):
        '''
        Updates [self.cluelist] and [self.chargrid].
        [word] is the solution that's being added. String. 
        [clueID] is the clueID of the word being changed. String. 
        Conflicts occur when we attempt to *change* an already-solved cell.
            'override': replace any existing letters.
            'exception': restore the previous solution and raise an exception
            'ignore': only add the non-conflicting letters
        Example: add_word('FAST', '31 ACROSS')
        '''
        backup = copy.deepcopy((self.cluelist, self.chargrid))
        assert len(self.cluelist[clueID][0]) == len(word), 'Solution length is incorrect.'
        assert clueID in self.cluelist.keys(), 'Given clueID is not valid.'
        try:
            for pos, letter in enumerate(word):
                y, x = self.find_cell(clueID, pos)
                self.add_letter(letter, y, x, conflict=conflict)
        except:
            self.cluelist, self.chargrid = backup
            raise