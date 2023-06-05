
class Utility():
    
    def load_word_list(word_list_file_path:str, word_length:int=5, exclude_plurals:bool=True):
        english_words = [word.replace("\r", "").replace("\n", "") for word in open(word_list_file_path).readlines()]
        word_list = [word for word in english_words if len(word) == word_length]
        if exclude_plurals:
            word_list = [word for word in word_list if (word[-1] != "s" or word.endswith("ss"))]
        return word_list

    def load_word_socres_dict(word_socre_file_path: str):
        word_score_lines = [line.split("\t") for line in open(word_socre_file_path, "r").readlines()]
        word_score_dict = {}
        for (word, score) in word_score_lines:
            word_score_dict[word] = float(score.replace("\r", "").replace("\n", ""))
        return word_score_dict
