# cintel-05-cintel

# If using local development place app.py in a folder. When Publishing Github Pages change it from root to docs in settings > Pages.

# Install shinylive module
pip install shinylive

.venv\Scripts\activate
shiny run --reload --launch-browser dashboard/app.py

shiny static-assets remove
shinylive export dashboard docs