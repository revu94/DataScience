import json
def write_to_text_file(file_path:str,content:str)->None:
    with open(file_path,"w") as fw:
        fw.write(content)

def read_text_file_as_list(file_path:str)->list[str]:
    with open(file_path,"r") as f:
        lines=f.readlines()
    return lines

def read_json_file():
    pass

def write_to_json():
    pass



