from flask import render_template
import markdown

def render_markdown_template(filesname_no_ext, replacements_dict={}):
    # Read the Markdown content from the file
    with open('markdown/' + filesname_no_ext + '.md', 'r') as file:
        md_string = file.read()

    # Replace placeholders with values from replacements_dict
    for key, value in replacements_dict.items():
        placeholder = f"{{{{ {key} }}}}"
        md_string = md_string.replace(placeholder, value)

    # Convert the modified Markdown to HTML
    html_content = markdown.markdown(md_string)
    return render_template('general_markdown' + '.html', content=html_content)

