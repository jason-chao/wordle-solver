
class Utility():
    
    def load_word_list(word_list_file_path:str, word_length:int=5, exclude_plurals:bool=True):
        english_words = [word.replace("\n", "") for word in open(word_list_file_path).readlines()]
        word_list = [word for word in english_words if len(word) == word_length]
        if exclude_plurals:
            word_list = [word for word in word_list if (word[-1] != "s" or word.endswith("ss"))]
        return word_list
