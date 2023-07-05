import glob
import random
from prompts import INSPECTOR, FUNCTIONS, INSTRUCTS_SEX

def get_photo(folder):
    # read folder and return random photo
    print("get_photo ", folder)
    return random.choice(glob.glob(folder + "/*"))
    

def get_video(query):
    print("get_video ", query)

def inspect(llm, response):
    return llm(INSTRUCTS_SEX + "User:" + response, temperature=0)

if __name__ == "__main__":
    while 1:
        input__ = input("Enter")
        print(inspect(input__))