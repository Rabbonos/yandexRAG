#llamaindex semantic splitter?

import pymupdf



def pdf_reader(pdf_bytes:bytes)->str:
        '''
        This function takes in a pdf file from memory and returns the text in the pdf file
        '''
        doc = pymupdf.open(stream=pdf_bytes, filetype='pdf') # open a document
        text=''
        for page in doc: # iterate the document pages
            text += page.get_text() #text = text+ page.get_text().encode("utf8") # get plain text (is in UTF-8)
        return text
