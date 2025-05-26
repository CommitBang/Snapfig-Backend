This folder is responsible for the service of the ocr.
Opposed to the client-side, current files are for ocr server solely for ocr operation

In order to open the server,
0. navigate to the current ocr server folder (cd "C:\Users\USER\general\3-1 OSSW\advanced-pdf-viewer\ocr_server")
1. activate virtual environment (ocr_env\Scripts\activate.bat)
2. launch server via command (python main.py)


<server structure>
User provides pdf to web app --> sends request to pdf viewer server --> pdf viewer server receives request and passes message to api(fastapi) --> api routes to send request to ocr server

--> ocr server receives request and passes message to api(fastapi) --> api routes to python logic to run ocr --> python returns ocr result back to api --> ocr server --> api --> pdf viewer server --> User