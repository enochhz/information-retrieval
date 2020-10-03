import os
import re
import pandas as pd

class FileManager: 

    @staticmethod
    def make_directories(html_content_folder: str, lang: str, csv_folder: str) -> None: 
        """
        Initializes necessary folder structures
        """
        if not os.path.isdir((f'./{html_content_folder}')):
            os.makedirs((f'./{html_content_folder}'))
        if not os.path.isdir((f'./{html_content_folder}/{lang}')):
            os.makedirs((f'./{html_content_folder}/{lang}'))
        if not os.path.isdir((f'./{csv_folder}')):
            os.makedirs((f'./{csv_folder}'))
    
    @staticmethod
    def store_html_content(page_url: str, html: str, folder_path: str) -> None:
        path_name = re.split('http[s]?://', page_url)[1]
        path_name = path_name.replace('/', '#')
        if page_url.endswith('.html') or page_url.endswith('.htm'):
            # file_name = f'{self.html_content_folder}/{self.lang}/{path_name}'
            file_name = f'{folder_path}/{path_name}'
        else:
            # file_name = f'{self.html_content_folder}/{self.lang}/{path_name}.html'
            file_name = f'{folder_path}/{path_name}.html'
        text_file = open(file_name, 'w')
        text_file.write(html)
        text_file.close()

    @staticmethod
    def write_to_csv(dictionary: dict, col1_name: str, col2_name: str, file_name: str) -> None:
        new_dict = {
            col1_name: [k for k in dictionary.keys()], 
            col2_name: [v for v in dictionary.values()]
        }
        new_df = pd.DataFrame.from_dict(new_dict)
        if os.path.exists(file_name):
            exist_df = pd.read_csv(file_name, index_col=0)
            exist_df.append(new_df).reset_index(drop=True).to_csv(file_name)
        else:
            new_df.reset_index(drop=True).to_csv(file_name)
