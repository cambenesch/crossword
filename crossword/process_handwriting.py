def read_image_file_header(filename):
    f = open(filename, 'rb')
    int.from_bytes(f.read(4), byteorder='big')  # magic number, discard it
    count = int.from_bytes(f.read(4), byteorder='big')  # number of samples in data set
    rows = int.from_bytes(f.read(4), byteorder='big')  # rows per image
    columns = int.from_bytes(f.read(4), byteorder='big')  # columns per image
    pos = f.tell()  # current position used as offset later when reading data
    f.close()
    return pos, count, rows, columns

def load_save_images(inputfilename, byte_offset, outputfilename, cols, rows, count):
    list_data = []
    infile = open(inputfilename, 'rb')
    infile.seek(byte_offset)
    for n in range(count):
        image_matrix = [[0 for x in range(cols)] for y in range(rows)]
        for r in range(rows):
            for c in range(cols):
                byte = infile.read(1)
                image_matrix[c][r] = float(ord(byte))
        list_data.append(image_matrix)
        # show progress
        if n % 5000 == 0:
            print("... " + str(n))
    infile.close()
    print('converting to numpy array')
    list_data = np.array(list_data)
    print('normalizing')
    list_data = tf.keras.utils.normalize(list_data, axis=1)
    print('saving')
    np.save(outputfilename, list_data)
    
image_matrix = [[0 for x in range(cols)] for y in range(rows)]

for n in range(count):
        image_matrix = [[0 for x in range(cols)] for y in range(rows)]
        for r in range(rows):
            for c in range(cols):
                byte = infile.read(1)
                image_matrix[c][r] = float(ord(byte))
        list_data.append(image_matrix)
        
