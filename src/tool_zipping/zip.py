import zipfile

# Creating a ZIP file
with zipfile.ZipFile('example.zip', 'w') as zipf:
    zipf.write('file1.txt')
    zipf.write('file2.txt')

# Reading a ZIP file
with zipfile.ZipFile('example.zip', 'r') as zipf:
    zipf.extractall('extracted_files')
