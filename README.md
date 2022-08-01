### Running the application (Bash)
        export FLASK_APP=app.py
        python -m flask run

 * Running on http://127.0.0.1:5000/

 ## Flask installation (pip install Flask)
    1. Werkzeug(WSGI) - interface between applications and webservers
    2. Jinja - template language to render the pages 
    3. MarkupSafe - to escape unstrusted input when rendering templates (prevent innjection attacks)
    4. ItsDangerous - Sign data to ensure integrity protect session cookies)
    5. Click - writing command line applications



## Requirements
&#9745; Semantic HTML

&#9745; Custom CSS

&#9745; Dynamically Change DOM 
with Javascript

&#9745; Backend with multiple Routes

&#9745; Uses a Database

&#9745; Users can Create Database Records

&#9745; Database records get Dynamically rendered in at least one View

&#9745; Include authentication (minimum login/logout)

&#9745; Cleaner Code with Blueprints

&#9745; Test Coverage in coverage.pdf
 
 &#9745; Security Optimization & Validations

    a. users are not able to upload image files that would cause XSS problems Cross-Site Scripting (XSS)
    
    b. Prepared Statements (with Parameterized Queries)
    WHERE p.id = ? (id,) - Any time user input can be converted to a non-String, like a date, numeric, boolean, enumerated type, etc. before it is appended to a query, or used to select a value to append to the query, this ensures it is safe to do so.