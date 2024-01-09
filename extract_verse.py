from flask import Flask, render_template, request
import os
import re

app = Flask(__name__)


def get_chapter_list():
    # Path to the 'Livres' directory
    livres_path = './Livres'
    # Extracting folder names as chapters
    try:
        chapters = [d for d in os.listdir(livres_path) if os.path.isdir(os.path.join(livres_path, d))]
    except FileNotFoundError:
        chapters = ['Directory not found']
    return chapters



@app.route('/', methods=['GET', 'POST'])
def index():
    chapters = get_chapter_list()
    selected_chapter = "Exode"  # Default selection for the first load

    if request.method == 'POST':
        # Handle the form data here
        selected_chapter = request.form.get('selected_chapter','Exode')
        chap = request.form['chap']
        debut = request.form['debut']
        fin = request.form['fin']
        dir_path = f'./Livres/{selected_chapter}'
        # Get the list of markdown files in the directory
        md_files = [f for f in os.listdir(dir_path) if f.endswith('.md')]
        if not md_files:
            raise FileNotFoundError("No markdown files found in the directory.")

        # Assume the first file's naming convention applies to others
        base_file_name = md_files[0][:-4]  # Remove the last 4 characters (e.g., '001.md')

        # Construct the markdown file path
        md_file_path = f'{dir_path}/{base_file_name}{chap}.md'
        
        try:
            # Your existing code to open and read the markdown file
            with open(md_file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()

            # Construire le motif regex pour extraire le contenu requis
            verse_pattern = fr"###### {debut}\n(.*?)(###### {int(fin) + 1}\n|$)"
            # Extraire le contenu
            match = re.search(verse_pattern, md_content, re.DOTALL)
            extracted_content = match.group().strip() if match else "Versets non trouvés."
            extracted_content = re.sub(fr"\n###### {int(fin) + 1}", "", extracted_content)
            # Nettoyer le contenu extrait en enlevant les numéros de verset
            keep_verse_numbers = 'keep_verse_numbers' in request.form

            if keep_verse_numbers:
                # Keep verse numbers, allowing for multi-digit verse numbers
                cleaned_content = re.sub(fr"\n*###### (\d+)\n", r"\n\1 ", extracted_content)
            else:
                # Remove verse numbers
                extracted_content = re.sub(fr"###### {debut}\n", "", extracted_content)
                cleaned_content = re.sub(r"\n*###### \d+\n", " ", extracted_content)


            # ...
            return render_template('index.html', result=cleaned_content, chapters=chapters, keep_verse_numbers=keep_verse_numbers, selected_chapter=selected_chapter)
    
        except FileNotFoundError:
        # Update the result_text textbox if the file is not found
            keep_verse_numbers = 'keep_verse_numbers' in request.form

            cleaned_content = "Versets non trouvés."
            return render_template('index.html', result=cleaned_content, chapters=chapters, keep_verse_numbers=keep_verse_numbers, selected_chapter=selected_chapter)
        
    return render_template('index.html', chapters=chapters, selected_chapter=selected_chapter)

if __name__ == '__main__':
    app.run(debug=True)
